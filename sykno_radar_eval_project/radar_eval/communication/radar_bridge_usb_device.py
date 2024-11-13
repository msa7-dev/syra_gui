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

from typing import List, Tuple, Optional
from pathlib import Path
from loguru import logger

from radar_eval.radar_system.radar_system_definition import SYRA_RADAR_PARAMETER
from radar_eval.communication.radar_bridge_mcu_commands import SYRA_MCU_COMMANDS, SYRA_MCU_USB_DEF


class SYRA_USB_SPI_BRIDGE:
    def __init__(self, syra_device: SYRA_RADAR_PARAMETER) -> None:
        self.config = configparser.ConfigParser()
        self.config.read(__init__.SYRA_SYS_CONFIG_PATH)

        self.read_counter = 0
        self.write_counter = 0

        self.syra_device = syra_device
        self.mcu_usb_def = SYRA_MCU_USB_DEF()
        self.mcu_commands = SYRA_MCU_COMMANDS()
        self.radar_param: SYRA_RADAR_PARAMETER = syra_device.radar_param

        self.device: Optional[usb.core.Device] = None
        self.interface: Optional[int] = None
        self.endpoint_in: Optional[usb.core.Endpoint] = None
        self.endpoint_out: Optional[usb.core.Endpoint] = None
        self.n_fifo_overhead = np.uint8(0)
        self.usb_device_available = multiprocessing.Value('b', True)

        self.init_stm_usb_device()

        if self.device is None:
            logger.error("No USB device found, exiting initialization.")
            return

        if self.used_usb_product_id != 'e404':
            self.spi_init_bgt()

        logger.debug('Finished BGT Device Init')

    def send_usb_payload(self, usb_payload: bytearray) -> None:
        try:
            self.usb_device_available.get_lock().acquire(block=True, timeout=1000)
            self.endpoint_out.write(usb_payload)
            usb.util.release_interface(self.device, self.interface)
            self.usb_device_available.get_lock().release()
        except:
            logger.debug("Error sending USB data.")

    def receive_usb_payload(self, read_n_bytes: int) -> Optional[bytearray]:
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

    def spi_deinit_syra(self) -> None:
        self.spi_bgt_reset()
        self.spi_stm_reset()

    def spi_bgt_finished_init(self) -> None:
        self.send_usb_payload(bytearray([self.mcu_commands.init_finished_cmd]))

    def spi_bgt_reset(self) -> None:
        self.send_usb_payload(bytearray([self.mcu_commands.bgt_reset_cmd]))

    def spi_stm_reset(self) -> None:
        self.send_usb_payload(bytearray([self.mcu_commands.stm_rst_cmd]))
        self.init_stm = False

    def spi_activate_boot_mode(self, product_name: str = 'Sykno_Radar_Bridge_FW', firmware_name: str = '') -> None:
        self.send_usb_payload(bytearray([self.mcu_commands.flash_cmd]))
        self.deinit_stm_usb_device()
        time.sleep(1.5)  # Delay to ensure the device is ready for programming

        firmware = product_name if not firmware_name else firmware_name
        command = [
            './tools/programmer/bin/STM32_Programmer_CLI',
            '-c', 'port=/dev/ttyUSB0', 'br=921600',
            '-e', 'all',
            '-w', f'./radar_eval/setup/mcu_firmware/{firmware}.elf',
            '-v',
            '-g 0x00000000'
        ]
        self.run_subprocess(command, success_message="  Address:      : 0x0")

    def run_subprocess(self, command: List[str], success_message: str) -> None:
        """Run a subprocess with the given command and log its output."""
        with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as proc:
            try:
                for line in proc.stdout:
                    logger.info(line, end='')
                    if success_message in line:
                        logger.info("Detected successful execution of the run command.")
                        time.sleep(1)
                        proc.kill()
                        return
                for line in proc.stderr:
                    logger.error(line, end='')
            except Exception as e:
                logger.error(f"An error occurred: {e}")

    def init_fifo_overhead(self) -> None:
        """Initialize FIFO overhead."""
        usb_allocation = int(self.config.get("SYRA_USB_SPI_BRIDGE", f"USB_SPI_BRIDGE_DATA_ALLOCATION_{self.radar_param.mon.sykno_product_name}"))
        self.radar_param.sys.n_fifo_overhead = np.uint8(
            usb_allocation / (
                self.radar_param.sys.n_samples_per_chirp[0] *
                self.radar_param.sys.allocation_factor *
                (self.radar_param.sys.rx_active_antennas[0] / sum(self.radar_param.sys.tx_active_antennas))
            )
        )
        self.spi_set_n_fifo_overhead(self.radar_param.sys.n_fifo_overhead)

    def spi_set_n_fifo_overhead(self, n_fifo_overhead: np.uint8) -> None:
        self.n_fifo_overhead = n_fifo_overhead
        usb_payload = bytearray([self.mcu_commands.set_fifo_overhead_cmd, self.n_fifo_overhead])
        self.send_usb_payload(usb_payload)

    def spi_get_chip_id(self) -> None:
        usb_payload = bytearray([self.mcu_commands.bgt_chip_id_cmd])
        self.send_usb_payload(usb_payload)
        ret_payload = self.receive_usb_payload(self.mcu_usb_def.get_chip_id_rx_len)
        if ret_payload is not None:
            chip_id = self.extract_chip_id(ret_payload)
            self.radar_param.mon.chip_id = f"{chip_id:012X}"
            self.decode_sensor_version(ret_payload[7], ret_payload[6])

    def extract_chip_id(self, payload: bytearray) -> np.uint64:
        """Extract the chip ID from the returned payload."""
        return np.uint64(
            np.uint64(payload[0] << 40) |
            np.uint64(payload[1] << 32) |
            np.uint64(payload[2] << 24) |
            np.uint64(payload[3] << 16) |
            np.uint64(payload[4] << 8) |
            np.uint64(payload[5])
        )

    def decode_sensor_version(self, chip_rf_id: int, chip_digital_id: int) -> None:
        product_name = self.config.get('DEFAULT', f'SYRA_PRODUCT_NAME_{self.used_usb_product_id}')
        allocation_factor = 1
        if chip_rf_id == 4 and chip_digital_id == 5:
            self.set_sensor_version("BGT60ATR24C", "2 Tx, 4 Rx", "MiRa6024I1A", 3)
        elif chip_rf_id == 3 and chip_digital_id == 3:
            self.set_sensor_version("BGT60TR13C", "1 Tx, 3 Rx", "SY60I13", 1.5)
        elif chip_rf_id == 12 and chip_digital_id == 7:
            self.set_sensor_version("BGT60UTR11AIP", "1 Tx, 1 Rx", "SY60I11", 1.5)
        else:
            logger.warning("Unknown chip version detected.")

        logger.debug(f"Connected to {product_name} device, equipped with {self.radar_param.mon.chip_version_digital_id} radar sensor with {self.radar_param.mon.chip_version_rf_id} antennas")

    def set_sensor_version(self, digital_id: str, rf_id: str, product_name: str, allocation_factor: float) -> None:
        """Set the sensor version details."""
        self.radar_param.mon.chip_version_digital_id = digital_id
        self.radar_param.mon.chip_version_rf_id = rf_id
        self.radar_param.mon.sykno_product_name = product_name
        self.radar_param.sys.allocation_factor = allocation_factor

    def spi_set_dummy_cref(self, user_reg_vals: bytearray) -> None:
        index = 0
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

    def raw_data_acquisition_process(self, usb_extraction_data_queue: multiprocessing.Queue, process_stop_event: multiprocessing.Event) -> None:
        """Acquire raw data from the device and put it into the queue."""
        self.configure_process_settings()

        data_allocation = self.get_data_allocation()
        raw_data = np.zeros(1,)

        while not process_stop_event.is_set():
            try:
                usb.util.release_interface(self.device, self.interface)
                raw_data = np.asarray(self.endpoint_in.read(data_allocation), dtype=np.uint8)
                usb.util.release_interface(self.device, self.interface)
                if raw_data.shape == (data_allocation,):
                    usb_extraction_data_queue.put(raw_data)
            except usb.core.USBError:
                continue

    def configure_process_settings(self) -> None:
        """Configure the CPU affinity and priority for the acquisition process."""
        cpu_core = int(self.config.get("SYRA_HOST_SYS_PARAMETER", "SYRA_AQUISITION_CPU_CORE"))
        process_priority = np.int8(self.config.get("SYRA_HOST_SYS_PARAMETER", "SYRA_PROCESS_PRIO"))

        current_process = psutil.Process(os.getpid())
        current_process.cpu_affinity([cpu_core])
        current_process.nice(process_priority)
        setproctitle.setproctitle("Sykno - Radar Eval GUI - Data Acquisition Process")

    def get_data_allocation(self) -> np.uint32:
        """Calculate and return the data allocation size."""
        usb_allocation = np.uint32(self.config.get("SYRA_USB_SPI_BRIDGE", f"USB_SPI_BRIDGE_DATA_ALLOCATION_{self.radar_param.mon.sykno_product_name}"))
        return np.uint32(usb_allocation + np.uint32(self.radar_param.sys.n_fifo_overhead) * 9)

    def spi_read_reg(self, reg_adr: np.uint8) -> Tuple[np.uint8, np.ndarray]:
        usb_payload = bytearray([self.mcu_commands.read_cmd, reg_adr])
        self.read_counter += 1

        self.send_usb_payload(usb_payload)
        ret_payload = self.receive_usb_payload(self.mcu_usb_def.spi_read_reg_cmd_len)
        if ret_payload is not None:
            return np.uint8(ret_payload[0]), np.array(ret_payload[1:])
        else:
            logger.error("Failed to read register value.")
            return np.uint8(0), np.array([])

    def spi_read_n_reg(self, reg_start_adr: np.uint8, n_reg: np.uint16) -> np.ndarray:
        usb_payload = bytearray([self.mcu_commands.read_n_cmd, reg_start_adr,
                                 np.uint8((n_reg >> 8)), np.uint8(n_reg)])
        self.send_usb_payload(usb_payload)
        ret_payload = self.receive_usb_payload(n_reg * 3)
        if ret_payload is not None:
            return np.array(ret_payload)
        else:
            logger.error("Failed to read multiple register values.")
            return np.array([])

    def spi_write_reg_vals(self, reg_adr: np.uint8, reg_vals: List[np.uint8]) -> None:
        usb_payload = bytearray([self.mcu_commands.write_cmd, reg_adr] + reg_vals)
        self.send_usb_payload(usb_payload)

    def spi_write_reg_val(self, reg_adr: np.uint8, reg_vals: List[np.uint8]) -> None:
        usb_payload = bytearray([self.mcu_commands.write_cmd, reg_adr] + reg_vals)
        self.write_counter += 1
        self.send_usb_payload(usb_payload)

    def init_stm_usb_device(self) -> None:
        """Initialize the STM USB device by finding it via vendor and product IDs."""
        vendor_id, product_ids = self.get_vendor_and_product_ids()

        for product_id in product_ids:
            try:
                self.device = usb.core.find(idVendor=vendor_id, idProduct=product_id)
                if self.device:
                    self.used_usb_product_id = str(hex(product_id).split('x')[1])
                    break
                else:
                    self.log_usb_device_search(vendor_id, product_id)
            except usb.core.USBError as e:
                self.log_usb_device_search(vendor_id, product_id, error=e)

        if self.device is None:
            logger.error("Failed to find any suitable USB device.")
            return

        self.log_usb_device_info(vendor_id, product_id)
        self.setup_usb_endpoints()

    def get_vendor_and_product_ids(self) -> Tuple[int, List[int]]:
        """Retrieve vendor and product IDs from the configuration."""
        vendor_id = int(self.config.get("SYRA_USB_SPI_BRIDGE", "SYRA_USB_VENDOR_ID"), 16)
        product_ids = [
            int(self.config.get("SYRA_USB_SPI_BRIDGE", "SYRA6024_USB_PRODUCT_ID"), 16),
            int(self.config.get("SYRA_USB_SPI_BRIDGE", "SYRA6013_USB_PRODUCT_ID"), 16),
            int(self.config.get("SYRA_USB_SPI_BRIDGE", "SYRA6011_USB_PRODUCT_ID"), 16),
            int(self.config.get("SYRA_USB_SPI_BRIDGE", "SYRA_ERR_USB_PRODUCT_ID"), 16)
        ]
        return vendor_id, product_ids

    def log_usb_device_search(self, vendor_id: int, product_id: int, error: Optional[usb.core.USBError] = None) -> None:
        """Log the search process for USB devices."""
        if error:
            logger.error(f"Error searching for USB device: {error}")
        else:
            logger.debug(f"Searched for MiRa USB device with Vendor ID: {hex(vendor_id)}, Product ID: {hex(product_id)}")

    def log_usb_device_info(self, vendor_id: int, product_id: int) -> None:
        """Log information about the connected USB device."""
        product_name = self.config.get('DEFAULT', f'SYRA_PRODUCT_NAME_{self.used_usb_product_id}')
        logger.debug(f"Device found: {product_name}\n"
                     f"Connected to USB device with Vendor ID: {hex(vendor_id)}\n"
                     f"Connected to USB device with Product ID: {hex(product_id)}")
        try:
            manufacturer = usb.util.get_string(self.device, self.device.iManufacturer)
            product = usb.util.get_string(self.device, self.device.iProduct)
            serial_number = usb.util.get_string(self.device, self.device.iSerialNumber)
            logger.debug(f"Manufacturer: {manufacturer}\nProduct: {product}\nSerial Number: {serial_number}")
        except ValueError as e:
            logger.warning(f"Could not retrieve USB Device Descriptor: {e}")

    def setup_usb_endpoints(self) -> None:
        """Set up the IN and OUT endpoints for the USB device."""
        max_iterations = 0xFF
        iteration_counter = 0

        for config in self.device:
            for interface in config:
                iteration_counter += 1
                self.interface = interface.bInterfaceNumber

                if self.device.is_kernel_driver_active(self.interface):
                    self.device.detach_kernel_driver(self.interface)

                for endpoint in interface:
                    iteration_counter += 1
                    if iteration_counter >= max_iterations:
                        logger.error("OUT and/or IN endpoints not found.")
                        self.device = None
                        return

                    if usb.util.endpoint_direction(endpoint.bEndpointAddress) == usb.util.ENDPOINT_IN and endpoint.bEndpointAddress == 0x81:
                        self.endpoint_in = endpoint
                    elif usb.util.endpoint_direction(endpoint.bEndpointAddress) == usb.util.ENDPOINT_OUT and endpoint.bEndpointAddress == 0x01:
                        self.endpoint_out = endpoint

                    if self.endpoint_out and self.endpoint_in:
                        self.log_usb_endpoints()
                        break

    def log_usb_endpoints(self) -> None:
        """Log information about the USB device's endpoints."""
        try:
            self.radar_param.mon.product_usb = usb.util.get_string(self.device, self.device.iProduct)
            self.radar_param.mon.serial_usb = usb.util.get_string(self.device, self.device.iSerialNumber)
            self.radar_param.mon.manufacturer_usb = usb.util.get_string(self.device, self.device.iManufacturer)
            logger.debug(f"Product: {self.radar_param.mon.product_usb}, Serial: {self.radar_param.mon.serial_usb}, Manufacturer: {self.radar_param.mon.manufacturer_usb}")
        except usb.core.USBError:
            logger.error("Failed to retrieve endpoint information from the USB device.")

    def deinit_stm_usb_device(self) -> None:
        """Deinitialize the STM USB device, releasing the interface and resources."""
        try:
            self.spi_deinit_syra()
            if self.device and self.interface is not None:
                usb.util.release_interface(self.device, self.interface)
                usb.util.dispose_resources(self.device)
            logger.debug(f"{self.config.get('DEFAULT', f'SYRA_PRODUCT_NAME_{self.used_usb_product_id}')} by Sykno GmbH: USB Interface released.")
        except usb.core.USBError as e:
            if e.errno == 19:  # Errno 19 corresponds to "No such device"
                logger.debug("Device has been disconnected before interface could be released.")
            else:
                logger.error(f"Error releasing USB interface: {e}")
        finally:
            self.device = None
            self.endpoint_in = None
            self.endpoint_out = None

    def split_reg_val(self, reg_val: List[str]) -> bytearray:
        """Convert register values from hex string format to a bytearray."""
        reg_val_ret = bytearray()
        reg_val_arr = np.array([item.split(' ') for item in reg_val])

        for i in range(reg_val_arr.shape[0]):
            reg_val_ret.append(int(reg_val_arr[i, 0], 16))  # Register address
            reg_val_ret.extend(bytes.fromhex(reg_val_arr[i, 1][2:]))  # Register value

        return reg_val_ret

    def get_default_bgt_register_values(self) -> bytearray:
        """Retrieve the default BGT register values from a configuration file."""
        syra_reg_dir_path = Path(self.config.get("SYRA_BGT_SETTINGS", "SYRA_SENS_CONF_DIR_PATH")).resolve()
        project_name = self.radar_param.gui.project_name if self.radar_param.gui.project_name == ' ' else 'Default_'
        file_path = syra_reg_dir_path / f"{project_name}{self.radar_param.mon.sykno_product_name}.txt"

        with open(file_path, 'r') as file:
            lines = [line.replace('reg ', '') for line in file.read().splitlines()]

        return self.split_reg_val(lines)



