import __init__
import numpy as np
import configparser
from pathlib import Path
from enum import IntEnum
from loguru import logger
from typing import Any, Dict, Optional, Union
import radar_eval.radar_sensor.MiRa6024_register_defintion as BGT_REG

def check_sensor_register(instance: Any) -> bool:
    """Check if all register values in the instance are set."""
    for content in instance.CONTENT:
        content_instance = getattr(instance, content)
        if not all(value is not None for value in vars(content_instance).values()):
            return False
    return True

def status_overview(instance: Any) -> None:
    """Generate a status overview of all registers in the instance."""
    log_output = []

    for content in instance.CONTENT:
        content_instance = getattr(instance, content)
        reg_adr = _get_register_address(content_instance)
        log_output.append(f"{reg_adr.name[:-4]} ({hex(reg_adr)}):\n")
        log_output.append(f"Register Value: {hex(build_register_from_content(content_instance))}\n")
        log_output.append(_format_register_content(content_instance))
    
    logger.debug("\n".join(log_output))

def build_register_from_content(instance: Any) -> np.uint32:
    """Build a register value from the content of the instance."""
    result = np.uint32(0)
    for name, member in instance.REG_DEF.__members__.items():
        if name.endswith("_ID"):
            field_name = name[:-3]  # Remove "_ID" from the end
            pos = np.uint32(getattr(instance.REG_DEF, f"{field_name}_POS"))
            mask = np.uint32(getattr(instance.REG_DEF, f"{field_name}_MSK"))
            value = np.uint32(getattr(instance, f"_{field_name}", 0))
            result |= (value << pos) & mask
    return result

def get_reg_def_data(instance: Any, field_id: BGT_REG) -> Dict[str, Union[IntEnum, np.uint32]]:
    """Retrieve register definition data for a given field ID."""
    field_name = _get_field_name_from_id(field_id)
    reg_adr = _get_register_address(instance)

    field_data = {
        "ADR": reg_adr,
        "ID": field_id,
        "POS": getattr(field_id.__class__, f"{field_name}_POS"),
        "MSK": getattr(field_id.__class__, f"{field_name}_MSK"),
        "SET": getattr(field_id.__class__, f"{field_name}_SET"),
        "RST": getattr(field_id.__class__, f"{field_name}_RST"),
    }
    return field_data

def set_bgt_dev_register(instance: Any) -> None:
    """Set the BGT device registers based on the instance content."""
    for attr_name in build_content(instance):
        if attr_name == "usb_spi_bridge":
            break

        def_name = attr_name[1:]
        reg_id = getattr(instance.REG_DEF, f"{def_name}_ID")

        reg_adr = getattr(instance, 'REG_ADR', None)
        if reg_adr is not None:
            new_value = get_reg_val(instance, reg_id, reg_adr)
        else:
            new_value = get_reg_val(instance, reg_id)
        
        setattr(instance, attr_name, new_value)

def build_content(instance: Any) -> Dict[str, Any]:
    """Build a dictionary of the instance content that starts with '_'."""
    return {attr: getattr(instance, attr) for attr in vars(instance) if attr.startswith('_')}

def extract_reg_symbol_value(reg: np.uint32, msk: np.uint32, pos: np.uint32) -> int:
    """Extract a symbolic register value using mask and position."""
    return (reg & msk) >> pos

def get_reg_val(instance: Any, reg_id: IntEnum, adr: Optional[IntEnum] = None, rxData: Optional[int] = None) -> np.uint32:
    """Get the register value for a given ID."""
    field_data = get_reg_def_data(instance, reg_id)
    if adr is None:
        adr = field_data["ADR"]
    if rxData is None:
        adr, rx_data_bytes = instance.usb_spi_bridge.spi_read_reg(adr)
        rxData = int.from_bytes(rx_data_bytes, byteorder='big')

    msk = field_data['MSK']
    pos = field_data['POS']
    return np.uint32(extract_reg_symbol_value(rxData, msk, pos))

def split_24_bit_to_bytes(num: int) -> list[int]:
    """Split a 24-bit integer into three 8-bit bytes."""
    return [(num >> shift) & 0xFF for shift in (16, 8, 0)]

def set_reg_val(instance: Any) -> None:
    """Set a register value using SPI."""
    adr = _get_register_address(instance)
    tx_data = build_register_from_content(instance)
    tx_data_list = split_24_bit_to_bytes(tx_data)
    instance.usb_spi_bridge.spi_write_reg_val(adr, tx_data_list)

def generate_register_to_readable_txt(instance: Any, save_to_file: bool = True) -> str:
    """Generate a readable text file representation of the register contents."""
    result = []

    for content in instance.CONTENT:
        content_instance = getattr(instance, content)
        reg_adr = _get_register_address(content_instance)
        result.append(f"{reg_adr.name[:-4]} ({hex(reg_adr)}):\n")
        result.append(f"Register Value: {hex(build_register_from_content(content_instance))}\n")
        result.append(_format_register_content(content_instance))
    
    result_str = "\n".join(result)
    
    if save_to_file:
        filename = _get_configured_file_path("SYRA_REG_LOG_READABLE_TXT")
        with open(filename, 'w') as file:
            file.write(result_str)
    
    return result_str

def generate_register_to_txt(instance: Any, save_to_file: bool = True) -> str:
    """Generate a plain text file of the register contents."""
    result = []

    for content in instance.CONTENT:
        content_instance = getattr(instance, content)
        reg_adr = _get_register_address(content_instance)
        reg_value = build_register_from_content(content_instance)
        result.append(f"reg {reg_adr:#04x} {reg_value:#08x}\n")
    
    result_str = "".join(result)
    
    if save_to_file:
        filename = _get_configured_file_path("SYRA_REG_LOG_TXT")
        with open(filename, 'w') as file:
            file.write(result_str)
    
    return result_str

def clear_log_file() -> None:
    """Clear the log files."""
    file_path = _get_configured_file_path("SYRA_REG_LOG_TXT")
    file_path_readable = _get_configured_file_path("SYRA_REG_LOG_READABLE_TXT")

    _clear_file(file_path)
    _clear_file(file_path_readable)

def _get_register_address(instance: Any) -> Optional[IntEnum]:
    """Helper function to get the register address from the instance."""
    try:
        return instance.REG_ADR
    except AttributeError:
        # Fallback to find the register address in REG_DEF
        for name, value in vars(instance.REG_DEF).items():
            if name.endswith('_ADR'):
                return value
        raise AttributeError("Register address not found in instance or REG_DEF")

def _get_field_name_from_id(field_id: IntEnum) -> str:
    """Helper function to get the field name from the field ID."""
    for name, member in field_id.__class__.__members__.items():
        if member == field_id and name.endswith("_ID"):
            return name[:-3]  # Remove "_ID" from the end
    raise ValueError(f"No field found with ID {field_id}")

def _get_configured_file_path(config_key: str) -> Path:
    """Helper function to get a file path from the configuration."""
    config = configparser.ConfigParser()
    config.read(__init__.SYRA_SYS_CONFIG_PATH)
    return Path(config.get("SYRA_BGT_SETTINGS", config_key)).resolve()

def _format_register_content(content_instance: Any) -> str:
    """Helper function to format the content of a register for logging."""
    format_str = "{:<16} | {:^12} | {:^12} | {:^12}\n"
    line_length = 16 + 3 * 3 + 3 * 12
    formatted_content = []
    formatted_content.append(format_str.format("Register Symbol", "Value (dec)", "Value (hex)", "Value (bin)"))
    formatted_content.append("_" * line_length)

    for attr_name in vars(content_instance):
        if attr_name.startswith("_"):
            attr_value = getattr(content_instance, attr_name[1:])
            formatted_content.append(format_str.format(
                attr_name[1:],  
                str(attr_value),
                hex(attr_value),
                bin(attr_value)
            ))
    
    formatted_content.append("_" * line_length + "\n")
    return "\n".join(formatted_content)

def _clear_file(file_path: Path) -> None:
    """Helper function to clear or remove a file."""
    if file_path.exists():
        file_path.unlink()
        logger.debug(f"\nFile '{file_path}' removed successfully.")
    else:
        file_path.touch()
        logger.debug(f"\nFile '{file_path}' created successfully.")
