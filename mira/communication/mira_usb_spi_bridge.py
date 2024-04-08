import __init__
import os 
import time
import psutil
import logging
import usb.core
import usb.util
import subprocess
import numpy as np
import setproctitle
import configparser
import multiprocessing

from typing import List
from pathlib import Path
from loguru import logger

from mira.radar_system.mira_radar_sys import MIRA_RADAR_PARAMETER
#from mira.com.mira_mcu_cmds import MIRA_MCU_COMMANDS, MIRA_MCU_USB_DEF
from mira.communication.cython.mira_mcu_cmds import MIRA_MCU_COMMANDS, MIRA_MCU_USB_DEF

# ==============================================================================
# Class Name: MIRA_USB_SPI_BRIDGE
# ==============================================================================
class MIRA_USB_SPI_BRIDGE():
    def __init__(self, mira_device) -> None:
        self.config = configparser.ConfigParser()
        self.config.read(__init__.MIRA_SYS_CONFIG_PATH)
        
        self.read_counter = 0
        self.write_counter = 0
        
        self.mira_device = mira_device
        self.mcu_usb_def = MIRA_MCU_USB_DEF()
        self.mcu_commands = MIRA_MCU_COMMANDS()
        self.radar_param: MIRA_RADAR_PARAMETER = mira_device.radar_param
        
        self.device = None
        self.interface = None
        self.endpoint_in = None
        self.endpoint_out = None
        self.n_fifo_overhead = np.uint8(0)
        self.usb_device_available = multiprocessing.Value('b', True) 
        
        self.init_stm_usb_device()
        
        if self.device is None:
            return

        self.spi_init_bgt()
        
        logger.debug('Finished BGT Device Init')

        
    def send_usb_payload(self, usb_payload: bytearray) -> None:
        try:
            self.usb_device_available.get_lock().acquire(block=True, timeout=100)
            self.endpoint_out.write(usb_payload)
            usb.util.release_interface(self.device, self.interface)
            self.usb_device_available.get_lock().release()
        except:
            logger.debug("Error sending USB data.")
            
    def receive_usb_payload(self, read_n_bytes: int):
        try:
            self.usb_device_available.get_lock().acquire(block=True)
            ret_payload = self.endpoint_in.read(read_n_bytes)
            usb.util.release_interface(self.device, self.interface)
            self.usb_device_available.get_lock().release()
            return ret_payload
        except:
            logger.debug("Error reading USB data.")
    
    def spi_init_bgt(self) -> None:
        self.spi_get_chip_id()
        user_reg_vals = self.get_default_bgt_register_values()

        self.spi_set_dummy_cref(user_reg_vals)
        usb_payload = bytearray([self.mcu_commands.init_bgt_cmd]) + user_reg_vals
        self.send_usb_payload(usb_payload)
        
    def spi_reinit_bgt(self) -> None:
        self.spi_bgt_reset()
        self.spi_init_bgt()
        
    def spi_deinit_mira(self) -> None:
        self.spi_bgt_reset()
        self.spi_stm_reset()
        
    def spi_bgt_finished_init(self) -> None:
        self.send_usb_payload(bytearray([self.mcu_commands.init_finished_cmd]))
        
    def spi_bgt_reset(self) -> None:
        self.send_usb_payload(bytearray([self.mcu_commands.bgt_reset_cmd]))
        
    def spi_stm_reset(self) -> None:
        self.send_usb_payload(bytearray([self.mcu_commands.stm_rst_cmd]))
        self.init_stm = False
    
    def spi_activate_boot_mode(self, product_name: str='MiRa6024I1A', firmware_name: str='') -> None:
        self.send_usb_payload(bytearray([self.mcu_commands.flash_cmd]))
        self.deinit_stm_usb_device()
        time.sleep(2)  # Delay to ensure the device is ready for programming
        firmware = product_name if firmware_name == '' else firmware_name
        command = [
            './tools/programmer/bin/STM32_Programmer_CLI',
            '-c', 'port=/dev/ttyUSB0', 'br=115200',
            '-w', f'./mira/setup/mcu_firmware/{firmware}.bin', '0x08000000',
            '-v',
            '-g 0x00000000']
        success_message = "  Address:      : 0x0"

        # Start the subprocess and obtain handles to its stdout and stderr
        with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as proc:
            try:
                # Monitor the stdout of the process
                for line in proc.stdout:
                    print(line, end='')  # Print each line of stdout
                    if success_message in line:
                        print("\nDetected successful execution of the run command.")
                        # Optionally do additional steps here
                        # Terminate the process if it's still running
                        time.sleep(0.5)
                        proc.kill()  # Force-terminate if it didn't exit in time
                        return
                    
                # It's important to read stderr to prevent deadlocks
                for line in proc.stderr:
                    print(line, end='')  # Log or handle errors as needed

            except Exception as e:
                logging.error(f"An error occurred: {e}")

    def init_fifo_overhead(self):
        USB_SPI_BRIDGE_DATA_ALLOCATION = int(self.config.get("MIRA_USB_SPI_BRIDGE", 
                                                            f"USB_SPI_BRIDGE_DATA_ALLOCATION_{self.radar_param.mon.sykno_product_name}")) 
        self.radar_param.sys.n_fifo_overhead = np.uint8(USB_SPI_BRIDGE_DATA_ALLOCATION \
            / (self.radar_param.sys.n_samples_per_chirp[0] * self.radar_param.sys.allocation_factor  \
            * (self.radar_param.sys.rx_active_antennas[0] / sum(self.radar_param.sys.tx_active_antennas))))

        self.spi_set_n_fifo_overhead(self.radar_param.sys.n_fifo_overhead)
      
    def spi_set_n_fifo_overhead(self, n_fifo_overhead: np.uint8) -> None:
        self.n_fifo_overhead = n_fifo_overhead
        print(self.n_fifo_overhead)
        usb_payload = bytearray([self.mcu_commands.set_fifo_overhead_cmd, self.n_fifo_overhead])
        self.send_usb_payload(usb_payload)
        
    def spi_get_chip_id(self) -> None:
        usb_payload = bytearray([self.mcu_commands.bgt_chip_id_cmd])
        self.send_usb_payload(usb_payload)
        ret_payload = self.receive_usb_payload(self.mcu_usb_def.get_chip_id_rx_len)
        chip_id = np.uint64(np.uint64(ret_payload[0] << 40) | \
                            np.uint64(ret_payload[1] << 32) | \
                            np.uint64(ret_payload[2] << 24) | \
                            np.uint64(ret_payload[3] << 16) | \
                            np.uint64(ret_payload[4] <<  8) | \
                            np.uint64(ret_payload[5] <<  0))
        self.radar_param.mon.chip_id = f"{chip_id:012X}"
        
        chip_rf_id = ret_payload[7]
        chip_digital_id = ret_payload[6]
        
        self.decode_sensor_version(chip_rf_id, chip_digital_id)
        
    def decode_sensor_version(self, chip_rf_id: int, chip_digital_id: int) -> None:
        product_name = str(self.config.get('DEFAULT', 
                                          f'MIRA_PRODUCT_NAME_{self.used_usb_product_id}'))
        if chip_rf_id == 4 and chip_digital_id == 5:
            self.radar_param.mon.chip_version_digital_id = str("BGT60ATR24C")
            self.radar_param.mon.chip_version_rf_id = str("2 Tx, 4 Rx")
            self.radar_param.mon.sykno_product_name = str("MiRa6024I1A")
            self.radar_param.sys.allocation_factor = 3
        elif chip_rf_id == 3 and chip_digital_id == 3:
            self.radar_param.mon.chip_version_digital_id = str("BGT60TR13C")
            self.radar_param.mon.chip_version_rf_id = str("1 Tx, 3 Rx")
            self.radar_param.mon.sykno_product_name = str("SY60I13")
            self.radar_param.sys.allocation_factor = 1.5
        elif chip_rf_id == 12 and chip_digital_id == 7:
            self.radar_param.mon.chip_version_digital_id = str("BGT60UTR11AIP")
            self.radar_param.mon.chip_version_rf_id = str("1 Tx, 1 Rx")
            self.radar_param.mon.sykno_product_name = str("SY60I11")
            self.radar_param.sys.allocation_factor = 1.5
            
        logger.debug(f"\nConnected to {product_name} device, equipped with {self.radar_param.mon.chip_version_digital_id} radar sensor with {self.radar_param.mon.chip_version_rf_id} antenns")

    def spi_set_dummy_cref(self, user_reg_vals: bytearray) -> None:
        index = 0
        # TODO remove cref (not needed any longer through const qspi reading)
        while(index < 4*0x07):
            index = user_reg_vals.find(b'\x06')  # Find the first occurrence of 0x06
            if index != -1 and index + 1 < len(user_reg_vals) - 2:
                if index % 4 == 0:  # Check if the index is divisible by 4 or equal to 2
                    cref = user_reg_vals[index+2:index + 4]
                    dummy_cycles = np.uint8(user_reg_vals[index+1] >> 4) + 1
                    index = 0xff
                    usb_payload = bytearray([self.mcu_commands.set_fifo_cref_cmd]) + cref
                    self.send_usb_payload(usb_payload)
                    usb_payload = bytearray([self.mcu_commands.set_dummy_cycles_cmd, dummy_cycles])
                    self.send_usb_payload(usb_payload)
                else:
                    user_reg_vals[index] = 0x00
        
    def raw_data_aquisition_process(self, usb_extraction_data_queue: multiprocessing.Queue,
                                    process_stop_event: multiprocessing.Event) -> None:
        
        MIRA_AQUISITION_CPU_CORE = int(self.config.get("MIRA_HOST_SYS_PARAMETER",
                                                       "MIRA_AQUISITION_CPU_CORE"))
        MIRA_PROCESS_PRIO = np.int8(self.config.get("MIRA_HOST_SYS_PARAMETER", 
                                                    "MIRA_PROCESS_PRIO"))        
        
        current_process = psutil.Process(os.getpid())
        current_process.cpu_affinity([MIRA_AQUISITION_CPU_CORE])
        current_process.nice(MIRA_PROCESS_PRIO)
        setproctitle.setproctitle("Sykno - MiRa Eval GUI - Data Acquisition Process")

        USB_SPI_BRIDGE_DATA_ALLOCATION = np.uint32(self.config.get("MIRA_USB_SPI_BRIDGE", 
                                                                   f"USB_SPI_BRIDGE_DATA_ALLOCATION_{self.radar_param.mon.sykno_product_name}")) 
        DATA_ALLOCATION = np.uint32(USB_SPI_BRIDGE_DATA_ALLOCATION+self.radar_param.sys.n_fifo_overhead*9)
        
        raw_data = np.zeros(1,)
        while not process_stop_event.is_set():
            usb.util.release_interface(self.device, self.interface)
            try:
                raw_data = np.asarray(self.endpoint_in.read(DATA_ALLOCATION, 
                                                            timeout=0),
                                                            dtype=np.uint8)
            except:
                continue
            usb.util.release_interface(self.device, self.interface)
            if raw_data.shape == (DATA_ALLOCATION,):
                usb_extraction_data_queue.put(raw_data)



    def spi_read_reg(self, reg_adr: np.uint8) -> list[np.uint8, np.ndarray]:
        usb_payload = bytearray([self.mcu_commands.read_cmd, reg_adr])
        self.read_counter += 1
        
        self.send_usb_payload(usb_payload)
        ret_payload = self.receive_usb_payload(self.mcu_usb_def.spi_read_reg_cmd_len)
        return [np.uint8(ret_payload[0]), np.array(ret_payload[1:])]

    def spi_read_n_reg(self, reg_start_adr: np.uint8, n_reg: np.uint16) -> np.ndarray:
        usb_payload = bytearray([self.mcu_commands.read_n_cmd, reg_start_adr, 
                                 np.uint8((n_reg >> 8)), np.uint8(n_reg)]) 
        self.send_usb_payload(usb_payload)
        ret_payload = self.receive_usb_payload(n_reg*3)
       
        return np.array(ret_payload)

    def spi_write_reg_vals(self, reg_adr: np.uint8, reg_vals: list[np.uint8]) -> None:
        usb_payload = bytearray([self.mcu_commands.write_cmd, reg_adr] + reg_vals)
        self.send_usb_payload(usb_payload)

    def spi_write_reg_val(self, reg_adr: np.uint8, reg_vals: list[np.uint8]) -> None:
        usb_payload = bytearray([self.mcu_commands.write_cmd, reg_adr] + reg_vals)
        self.write_counter += 1
        self.send_usb_payload(usb_payload)
        
    def init_stm_usb_device(self) -> None:
        # Find the USB device based on vendor and product IDs
        vendor_id = int(self.config.get("MIRA_USB_SPI_BRIDGE", 
                                        "MIRA_USB_VENDOR_ID"), 16) 
        product_ids = []
        product_ids.append(int(self.config.get("MIRA_USB_SPI_BRIDGE", 
                                               "MIRA6024_USB_PRODUCT_ID"), 16))
        product_ids.append(int(self.config.get("MIRA_USB_SPI_BRIDGE", 
                                               "MIRA6013_USB_PRODUCT_ID"), 16))
        product_ids.append(int(self.config.get("MIRA_USB_SPI_BRIDGE", 
                                               "MIRA6011_USB_PRODUCT_ID"), 16))
        product_ids.append(int(self.config.get("MIRA_USB_SPI_BRIDGE", 
                                               "MIRA_ERR_USB_PRODUCT_ID"), 16))
        
        for product_id in product_ids:
            try:
                self.device = usb.core.find(idVendor=vendor_id, idProduct=product_id)
                if self.device is not None: 
                    self.used_usb_product_id = str(hex(product_id).split('x')[1])
                    break
                else:
                    logger.debug(f"\nSearched for MiRa USB device with:\n" +
                             f"USB Vendor ID:  {hex(vendor_id)},\n" + 
                             f"USB Product ID: {hex(product_id)}") 
            except usb.core.USBError as usb_error:
                logger.debug(f"\nSearched for MiRa USB device with:\n" +
                             f"USB Vendor ID:  {hex(vendor_id)},\n" + 
                             f"USB Product ID: {hex(product_id)}") 

        if self.device is None:
            return
        
        logger.debug('\nDevice found: '+str(self.config.get('DEFAULT', f'MIRA_PRODUCT_NAME_{self.used_usb_product_id}') + "\n") +
                     f"Connected to USB device: Vendor ID: {hex(vendor_id)}\n" +
                     f"Connected to USB device: Product ID: {hex(product_id)}")
        try:
            logger.debug("\nConnected to USB Device iMandufacturer:\n" +
                str(self.config.get('DEFAULT', f"MIRA_PRODUCT_NAME_{self.used_usb_product_id}") + " Manufacturer:") +
                f"{usb.util.get_string(self.device, self.device.iManufacturer)}")
            logger.debug("\nConnected to USB Device iProduct:\n" +
                str(self.config.get('DEFAULT', f"MIRA_PRODUCT_NAME_{self.used_usb_product_id}") +" Product:") +
                f"{usb.util.get_string(self.device, self.device.iProduct)}")
            logger.debug("\nConnected to USB Device iSerialNumber:\n" +
                str(self.config.get('DEFAULT', f'MIRA_PRODUCT_NAME_{self.used_usb_product_id}') + " Serial Number:") +
                f"{usb.util.get_string(self.device, self.device.iSerialNumber)}")
        except ValueError:
            logger.debug(f"Could not retrieve USB Device Descriptor.")
        
        self.get_usb_endpoints()
        if self.endpoint_out is None or self.endpoint_in is None:
            logger.debug("OUT and/or IN endpoints not found.")
            self.device = None
            return
        if self.endpoint_out is None:
            logger.debug("OUT endpoint not found.")
            self.device = None
            return
        if self.endpoint_in is None:
            logger.debug("IN endpoint not found.")
            self.device = None
            return

    def get_usb_endpoints(self) -> None:
        max_interation = 0xFF
        interations_counter = 0
        # Iterate through configurations
        for config in self.device:
            # Iterate through interfaces
            interations_counter += 1
            for interface in config:
                interations_counter += 1
                
                # Detach the kernel driver if active
                self.interface = interface.bInterfaceNumber

                if self.device.is_kernel_driver_active(self.interface):
                    self.device.detach_kernel_driver(self.interface)
                
                # Iterate through endpoints
                for endpoint in interface:
                    interations_counter += 1
                    if interations_counter >= max_interation:
                        logger.debug("OUT and/or IN endpoints not found.")
                        self.device = None
                        return
                    
                    # Check for IN endpoint
                    if usb.util.endpoint_direction(endpoint.bEndpointAddress) == usb.util.ENDPOINT_IN:
                        if endpoint.bEndpointAddress == 0x81:  # Endpoint 0x81 (IN)
                            self.endpoint_in = endpoint
                    # Check for OUT endpoint
                    elif usb.util.endpoint_direction(endpoint.bEndpointAddress) == usb.util.ENDPOINT_OUT:
                        if endpoint.bEndpointAddress == 0x1:  # Endpoint 0x1 (OUT)
                            self.endpoint_out = endpoint
                    if self.endpoint_out is not None and self.endpoint_in is not None:
                        self.radar_param.mon.product_usb = usb.util.get_string(self.device, self.device.iProduct)
                        self.radar_param.mon.serial_usb = usb.util.get_string(self.device, self.device.iSerialNumber)
                        self.radar_param.mon.manufacturer_usb = usb.util.get_string(self.device, self.device.iManufacturer)
                        break

    def deinit_stm_usb_device(self) -> None:
        # Check if the device is still connected
        time.sleep(0.100)
        try:
            self.spi_deinit_mira()
            # Attempt to release the interface and dispose resources if the device is connected
            usb.util.release_interface(self.device, self.interface)
            usb.util.dispose_resources(self.device)
            logger.debug(str(self.config.get('DEFAULT', f"MIRA_PRODUCT_NAME_{self.used_usb_product_id}")) +
                         " by Sykno GmbH: USB Interface released.")
        except usb.core.USBError as e:
            # Handle the case where the device has been disconnected
            if e.errno == 19:  # Errno 19 corresponds to "No such device"
                logger.debug("Device has been disconnected before interface could be released.")
            else:
                # Log other USB errors that may occur
                logger.error(f"Error releasing USB interface: {e}")
        self.device = None
        self.endpoint_in = None
        self.endpoint_out = None

        
    def split_reg_val(self, reg_val: list) -> bytearray:
        reg, val = [], []
        for content in reg_val:
            spilt = content.split(' ')
            reg.append(spilt[0])
            val.append(spilt[1])
        reg_val_ret = bytearray()
        reg_val_arr = np.array([reg, val])
        for i in range(reg_val_arr.shape[1]):
            # Convert hex string to bytes and append
            reg_val_ret.append(int(reg_val_arr[0][i], 16))  # From first array
            
            # 3 bytes from the second array
            bytes_from_second_array = bytes.fromhex(reg_val_arr[1][i][2:])  # Remove '0x' prefix
            reg_val_ret.extend(bytes_from_second_array)
        # Output
        hex_array = []
        for i in range(0, len(reg_val_ret), 4):
            # get 4 bytes
            four_bytes = reg_val_ret[i:i+4]
            # convert to hex string
            hex_str = '0x'+''.join(format(b, '02x') for b in four_bytes)
            # add to array
            hex_array.append(hex_str)

        return reg_val_ret

    def get_default_bgt_register_values(self) -> bytearray:
        mira_reg_dir_path = Path(self.config.get("MIRA_BGT_SETTINGS",
                                                 "MIRA_SENS_CONF_DIR_PATH")).resolve()
        self.radar_param.gui.project_name = self.radar_param.gui.project_name if self.radar_param.gui.project_name == ' ' else 'Default_'
        file_path = Path(f"{mira_reg_dir_path}/{self.radar_param.gui.project_name}{self.radar_param.mon.sykno_product_name}.txt")
        
        file = open(file_path, 'r')
        content = file.read()
        lines = content.splitlines()
        
        raw_reg_val = []
        for line in lines:
            raw_reg_val.append(str(line).replace('reg ', ''))
        file.close()
        
        return self.split_reg_val(raw_reg_val)