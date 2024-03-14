import __init__
import os
import numpy as np
import configparser
from enum import IntEnum
from pathlib import Path
from loguru import logger

import mira.sens.mira6024_reg_def as BGT_REG

def check_sensor_register(instance) -> bool:
    checker = False
    for content in instance.CONTENT:
        content = getattr(instance, content)
        checker = all(value is not None for value in vars(instance).values())
    return checker

def status_overview(instance):
    logger.debug_str = ""

    for content in instance.CONTENT:
        content = getattr(instance, content)    
        try:
            adr = content.REG_ADR
        except:
            adr = 0
            for name, value in vars(content.REG_DEF).items():
                if name.endswith('_ADR'):
                    adr = value
                    break
        
        logger.debug_str += (f"{adr.name[:-4]} ({hex(adr)}):\n")
        logger.debug_str += (f"Register Value:  {hex(build_register_from_content(content))}\n")
        format_str = f"{{:<16}} | {{:^12}} | {{:^12}} | {{:^12}}\n"
        logger.debug_str += (format_str.format("Register Symbol", "Value (dec)", "Value (hex)", "Value (bin)"))
        line_length = 16 + 3 * 3 + 3 * 12
        logger.debug_str += ("_" * line_length + "\n")
        format_str = f"{{:<16}} | {{:^12}} | {{:^12}} | {{:^12}}\n"
        for attr_name in vars(content):
            if attr_name.startswith("_"):
                attr_value = getattr(content, attr_name[1:])
                logger.debug_str += (format_str.format(
                    attr_name[1:],  
                    str(attr_value),
                    hex(attr_value),
                    bin(attr_value)
                ))
        logger.debug_str += ("_" * line_length + "\n\n")
                
    logger.debug(logger.debug_str)


def build_register_from_content(instance):
    # Create a dictionary of the register values
    result = 0
    for name, member in instance.REG_DEF.__members__.items():
        if name.endswith("_ID"):
            field_name = name[:-3]  # Remove "_ID" from the end
            pos = getattr(instance.REG_DEF, f"{field_name}_POS")
            mask = getattr(instance.REG_DEF, f"{field_name}_MSK")
            value = instance.CONTENT.get(f"_{field_name}", 0)
            result |= ((value << pos) & mask)
    return np.uint32(result)  # Ensure the result is a 24-bit integer


def get_reg_def_data(instance, field_id: BGT_REG=None):
    field_name = None
    for name, member in field_id.__class__.__members__.items():
        if member == field_id and name.endswith("_ID"):
            field_name = name[:-3]  # Remove "_ID" from the end
            break
    if field_name is None:
        raise ValueError(f"No field found with ID {field_id}")
    
    try:
        reg_adr = instance.REG_ADR
    except:
        reg_adr = 0
        for name, value in vars(instance.REG_DEF).items():
            if name.endswith('_ADR'):
                reg_adr = value
                break
    
    field_data = {
        "ADR": reg_adr,
        "ID": field_id,
        "POS": getattr(field_id.__class__, f"{field_name}_POS"),
        "MSK": getattr(field_id.__class__, f"{field_name}_MSK"),
        "SET": getattr(field_id.__class__, f"{field_name}_SET"),
        "RST": getattr(field_id.__class__, f"{field_name}_RST"),
    }
    return field_data

def set_bgt_dev_register(instance):
    for attr in build_content(instance):
        if attr == "usb_spi_bridge": break

        def_name = attr[1:]
        id = getattr(instance.REG_DEF, f"{def_name}_ID")
        
        try:
            new_value = get_reg_val(instance, id, instance.REG_ADR)
        except:
            new_value = get_reg_val(instance, id)

        setattr(instance, attr, new_value)


def build_content(instance):
    content = {attr: getattr(instance, attr) for attr in vars(instance) \
                if (not attr.startswith('__') and attr.startswith('_'))}
    return content

def extract_reg_symbol_value(reg: np.uint32, msk: np.uint32, pos: np.uint32):
    return (reg & msk) >> pos

def get_reg_val(instance, id: IntEnum, 
                adr: np.uint8=None,
                rxData: np.uint32=None) -> np.uint32:

    field_data = get_reg_def_data(instance, id)
    if adr == None:
        adr = field_data["ADR"]
    if rxData == None:
        adr, rxData = instance.usb_spi_bridge.spi_read_reg(adr)
        rxData = int.from_bytes(rxData, byteorder='big')

    msk = field_data['MSK']
    pos = field_data['POS']
    reg_val = extract_reg_symbol_value(rxData, msk, pos)
    
    return reg_val

def split_24_bit_to_bytes(num):
    byte1 = (num >> 16) & 0xFF
    byte2 = (num >> 8) & 0xFF
    byte3 = num & 0xFF
    return [byte1, byte2, byte3]

def set_reg_val(instance):
    try:
        adr = instance.REG_ADR
    except:
        adr = 0
        for name, value in vars(instance.REG_DEF).items():
            if name.endswith('_ADR'):
                adr = value
                break

    txData = build_register_from_content(instance)
    txData_list = [np.uint8(txData >> 16), np.uint8(txData >> 8), np.uint8(txData >> 0)]
    instance.usb_spi_bridge.spi_write_reg_val(adr, txData_list)


def generate_register_to_readable_txt(instance, save_to_file=True):    
    result = ""  # Initialize an empty string to store the file content
    
    for content in instance.CONTENT:
        content = getattr(instance, content)
        try:
            adr = content.REG_ADR
        except:
            adr = 0
            for name, value in vars(content.REG_DEF).items():
                if name.endswith('_ADR'):
                    adr = value
                    break
        result += f"{adr.name[:-4]} ({hex(adr)}):\n"
        result += f"Register Value:  {hex(build_register_from_content(content))}\n"

        format_str = f"{{:<16}} | {{:^12}} | {{:^12}} | {{:^12}}\n"
        result += format_str.format("Register Symbol", "Value (dec)", "Value (hex)", "Value (bin)")
        line_length = 16 + 3 * 3 + 3 * 12
        result += "_" * line_length + "\n"
        format_str = f"{{:<16}} | {{:^12}} | {{:^12}} | {{:^12}}\n"

        for attr_name in vars(content):
            if attr_name.startswith("_"):
                attr_value = getattr(content, attr_name[1:])
                result += format_str.format(
                    attr_name[1:],  
                    str(attr_value),
                    hex(attr_value),
                    bin(attr_value)
                )
        result += "_" * line_length + "\n\n"
    
    if save_to_file:
        config = configparser.ConfigParser()
        config.read(__init__.MIRA_SYS_CONFIG_PATH)
        filename = Path(config.get("MIRA_BGT_SETTINGS", "MIRA_REG_LOG_READABLE_TXT")).resolve()
        with open(filename, 'w') as file:
            file.write(result)
    
    return result  # Return the complete file content as a string if save_to_file is False


def generate_register_to_txt(instance, save_to_file=True):
    result = ""  # Initialize an empty string to store the file content
    
    for content in instance.CONTENT:
        content = getattr(instance, content)
        try:
            adr = content.REG_ADR
        except:
            adr = 0
            for name, value in vars(content.REG_DEF).items():
                if name.endswith('_ADR'):
                    adr = value
                    break

        register_value = build_register_from_content(content)
        result += f"reg {adr:#04x} "
        result += f"{register_value:#08x}\n"
    
    if save_to_file:
        config = configparser.ConfigParser()
        config.read(__init__.MIRA_SYS_CONFIG_PATH)
        filename = Path(config.get("MIRA_BGT_SETTINGS", "MIRA_REG_LOG_TXT")).resolve()
        with open(filename, 'w') as file:
            file.write(result)
    
    return result  # Return the complete file content as a string if save_to_file is False


def clear_log_file():
    config = configparser.ConfigParser()
    config.read(__init__.MIRA_SYS_CONFIG_PATH)
    file_path = Path(config.get("MIRA_BGT_SETTINGS", 
                                "MIRA_REG_LOG_TXT")).resolve()
    file_path_readable = Path(config.get("MIRA_BGT_SETTINGS", 
                                         "MIRA_REG_LOG_READABLE_TXT")).resolve()

    # Check if the file exists before attempting to remove it
    if os.path.exists(file_path):
        os.remove(file_path)
        logger.debug(f"\nFile '{file_path}' removed successfully.")
    else:
        with open(file_path, "w") as file:
            file.write("")
        file.close()
    
    if os.path.exists(file_path_readable):
        os.remove(file_path_readable)
        logger.debug(f"\nFile '{file_path_readable}' removed successfully.")
    else:
        with open(file_path_readable, "w") as file:
            file.write("")
        file.close()
        