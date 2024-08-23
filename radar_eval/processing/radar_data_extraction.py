import __init__

import os 
import time
import psutil
import platform
import numpy as np
import setproctitle
import configparser
import multiprocessing
from pathlib import Path
from radar_eval.radar_sensor.MiRa6024_sensor_device import MIRA_DEVICE
from radar_eval.radar_system.radar_system_definition import MIRA_RADAR_PARAMETER
from radar_eval.control.multiprocessing import distribute_cores_to_process
import radar_eval.processing.cython.radar_extract_raw_data as mira_extract_raw_data

# ==============================================================================
# Class Name: MIRA_DATA_EXTRACTOR
# ==============================================================================
class MIRA_DATA_EXTRACTOR():
    def __init__(self, mira_device: MIRA_DEVICE):
        self.config = configparser.ConfigParser()
        self.config.read(Path(__init__.MIRA_SYS_CONFIG_PATH).resolve())
        self.mira_device = mira_device
        self.radar_param: MIRA_RADAR_PARAMETER = mira_device.radar_param
        
    
    def data_extracting_process(self, usb_extraction_data_queue: multiprocessing.Queue,
                                prefix_header_queue: multiprocessing.Queue,
                                extracted_processing_data_queue: multiprocessing.Queue,
                                save_data_queue: multiprocessing.Queue,
                                process_stop_event: multiprocessing.Event):
        self.prefix_header_queue = prefix_header_queue

        MIRA_PROCESS_PRIO = np.int8(self.config.get("MIRA_HOST_SYS_PARAMETER", "MIRA_PROCESS_PRIO"))
        MIRA_EXTRACTING_CPU_CORE = int(self.config.get("MIRA_HOST_SYS_PARAMETER", "MIRA_EXTRACTING_CPU_CORE"))

        if platform.system() != "Windows":  # Only adjust affinity if not on Windows
            mira_data_extraction_process = psutil.Process(os.getpid())
            mira_data_extraction_process.cpu_affinity([MIRA_EXTRACTING_CPU_CORE])
            mira_data_extraction_process.nice(MIRA_PROCESS_PRIO)
            distribute_cores_to_process(mira_data_extraction_process, 1)
            setproctitle.setproctitle("Sykno - Radar Eval GUI - Extraction Process")

        radar_data_cube_build_buffer = np.zeros((self.radar_param.sys.n_samples_per_chirp[0],  # Dim 1 - Samples
                                                 int(self.radar_param.sys.rx_active_antennas[0]),  # Dim. 2 - Number RX Antennas
                                                 int(sum(self.radar_param.sys.tx_active_antennas)),  # Dim. 3 - Number Chirps per Shape
                                                 int(self.radar_param.sys.shape_set_repetition),  # Dim. 4 - Shape Set Repetition
                                                 self.radar_param.sys.max_frame_cnt),  # Dim. 5
                                                 dtype=np.uint16)
        
        USB_SPI_BRIDGE_DATA_ALLOCATION = np.uint32(self.config.get("MIRA_USB_SPI_BRIDGE",
                                                                   f"USB_SPI_BRIDGE_DATA_ALLOCATION_{self.radar_param.mon.sykno_product_name}"))
        overhead = np.multiply(self.radar_param.sys.n_fifo_overhead, 9, dtype=np.uint8)
        DATA_ALLOCATION = np.uint32(USB_SPI_BRIDGE_DATA_ALLOCATION + overhead)

        self.package_chirp_header_index_distance = np.uint32(
            self.radar_param.sys.n_samples_per_chirp[0] *
            (self.radar_param.sys.rx_active_antennas[0] /
             sum(self.radar_param.sys.tx_active_antennas)) * self.radar_param.sys.allocation_factor + 9)
        
        header_matches = list()
        for n_headers in range(np.uint32(DATA_ALLOCATION / self.package_chirp_header_index_distance)):
            header_matches.append(self.package_chirp_header_index_distance * n_headers)

        self.data_values = list()
        start_time = time.time()
        self.prev_frame_cnt = np.uint16(0)
        accumulated_data = {}
        rep_counter = {}

        while not process_stop_event.is_set():
            if not usb_extraction_data_queue.empty():
                raw_fifo_data = np.asarray(usb_extraction_data_queue.get(), dtype=np.uint8)  # ndarray.shape = (12288, )
            else:
                time.sleep(20e-6)
                continue
            
            self.data_values.append((raw_fifo_data.shape[0] * 8) / (time.time() - start_time))
            self.data_values = self.data_values[-256:]
            start_time = time.time()
            
            for header_match in header_matches:
                header_values = np.asarray(mira_extract_raw_data.prefix_header_cy(
                    raw_fifo_data[header_match: header_match + 9]), np.uint32)

                self.header_dict = {
                    'sync_word1': header_values[0],
                    'sync_word0': header_values[1],
                    'frame_cnt': header_values[2],
                    'shape_grp_cnt': header_values[3],
                    'chirp_len': header_values[4],
                    'sadc_val': header_values[5],
                    'cs': header_values[6],
                    'temperature': header_values[7],
                    'datarate': header_values[8],
                }

                self._update_header_dict_to_gui()
                curr_frame_cnt = np.uint16(self.header_dict['frame_cnt'])
                raw_data_slice = raw_fifo_data[header_match + 9: header_match + self.package_chirp_header_index_distance]

                data_field = np.asarray(mira_extract_raw_data.extract_raw_data_cy(
                    raw_data_slice,
                    raw_data_slice.shape[0],
                    self.radar_param.sys.rx_active_antennas[0]), dtype=np.uint16)

                if curr_frame_cnt > self.radar_param.sys.max_frame_cnt:
                    frame_cnt = np.mod(curr_frame_cnt, self.radar_param.sys.max_frame_cnt)
                else:
                    frame_cnt = curr_frame_cnt

                cs_index = self.header_dict['cs']
                shape_grp_cnt_index = np.uint16(self.header_dict['shape_grp_cnt'] / sum(self.radar_param.sys.tx_active_antennas))

                frame_cnt_index = frame_cnt
                key = (cs_index, shape_grp_cnt_index, frame_cnt_index)

                if key not in accumulated_data:
                    accumulated_data[key] = np.zeros_like(data_field, dtype=np.uint32)
                    rep_counter[key] = 0

                if np.all(radar_data_cube_build_buffer[:5, 0, cs_index, shape_grp_cnt_index, frame_cnt_index] == 0):
                    radar_data_cube_build_buffer[:, :, cs_index, shape_grp_cnt_index, frame_cnt_index] = data_field
                    accumulated_data[key] = data_field.astype(np.uint32)
                    rep_counter[key] = 1

                elif np.all(radar_data_cube_build_buffer[:5, 0, cs_index, shape_grp_cnt_index, frame_cnt_index] != 0) and \
                        self.radar_param.sys.shape_repetition[0] > 1 and rep_counter[key] > 0:
                    rep_counter[key] += 1
                    accumulated_data[key] += data_field.astype(np.uint32)

                    if rep_counter[key] >= self.radar_param.sys.shape_repetition[0] - 1:
                        radar_data_cube_build_buffer[:, :, cs_index, shape_grp_cnt_index, frame_cnt_index] = np.asarray(accumulated_data[key] / self.radar_param.sys.shape_repetition[0], dtype=np.uint16)

                if self.prev_frame_cnt != curr_frame_cnt:
                    if self.prev_frame_cnt > self.radar_param.sys.max_frame_cnt:
                        frame_cnt = np.mod(self.prev_frame_cnt, self.radar_param.sys.max_frame_cnt)
                    else:
                        frame_cnt = self.prev_frame_cnt
                        
                    if frame_cnt > 0:
                        zero_mask = np.all(radar_data_cube_build_buffer[:4, :, :, :, frame_cnt] == 0, axis=0)
                        if np.any(zero_mask):
                            radar_data_cube_build_buffer[:, zero_mask, frame_cnt] = radar_data_cube_build_buffer[:, zero_mask, frame_cnt - 1]


                    if extracted_processing_data_queue.empty():
                        extracted_processing_data_queue.put(radar_data_cube_build_buffer[:, :, :, :, frame_cnt])

                    if self.radar_param.meas.measurement_flag:
                        self.header_dict['frame_cnt'] = frame_cnt
                        save_data_queue.put({'Data': radar_data_cube_build_buffer[:, :, :, :, frame_cnt],
                                             'Header': self.header_dict})
                    self.prev_frame_cnt = curr_frame_cnt

                    if curr_frame_cnt == 4095:
                        del radar_data_cube_build_buffer
                        radar_data_cube_build_buffer = np.zeros((self.radar_param.sys.n_samples_per_chirp[0],  # Dim 1 - Samples
                                                                 int(self.radar_param.sys.rx_active_antennas[0]),  # Dim. 2 - Number RX Antennas
                                                                 int(sum(self.radar_param.sys.tx_active_antennas)),  # Dim. 3 - Number Chirps per Shape
                                                                 int(self.radar_param.sys.shape_set_repetition),  # Dim. 4 - Shape Set Repetition
                                                                 self.radar_param.sys.max_frame_cnt),  # Dim. 5
                                                                 dtype=np.uint16)
    def _update_header_dict_to_gui(self) -> None:
        if self.prefix_header_queue.empty():
            self.header_dict['temperature'] = self._convert_sadc_data(self.header_dict['sadc_val'])
            self.header_dict['datarate'] = np.mean(self.data_values) 
            self.prefix_header_queue.put_nowait(self.header_dict)

    def _convert_sadc_data(self, sadc_val: np.uint16) -> np.float32:
        self.radar_param.mon.sadc_output_mode = 0
        self.radar_param.mon.sadc_gain = 1
        if self.radar_param.mon.sadc_output_mode == 0:
            # Temperature Conversion BGT60ATR24 Datasheet: p. 92
            if sadc_val == 0:
                return 35.13
            else:
                return np.float32(round((((sadc_val/2**10)*1.21 * self.radar_param.mon.sadc_gain)-0.7989)/0.00297, 2))
        elif self.radar_param.mon.sadc_output_mode == 1:
            pass
        else: 
            return np.float32(-42.17) # magic number 
        
