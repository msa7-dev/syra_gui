import __init__

import os 
import time
import psutil
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

        MIRA_PROCESS_PRIO = np.int8(self.config.get("MIRA_HOST_SYS_PARAMETER",
                                                    "MIRA_PROCESS_PRIO"))
        MIRA_EXTRACTING_CPU_CORE = int(self.config.get("MIRA_HOST_SYS_PARAMETER", 
                                                       "MIRA_EXTRACTING_CPU_CORE"))

        mira_data_extraction_process = psutil.Process(os.getpid())
        mira_data_extraction_process.cpu_affinity([MIRA_EXTRACTING_CPU_CORE])
        mira_data_extraction_process.nice(MIRA_PROCESS_PRIO)
        distribute_cores_to_process(mira_data_extraction_process, 1)
        setproctitle.setproctitle("Sykno - Radar Eval GUI - Extraction Process")
        radar_data_cube_build_buffer = np.zeros((self.radar_param.sys.n_samples_per_chirp[0], # Dim 1 - Samples
                                                int(self.radar_param.sys.rx_active_antennas[0]), # Dim. 2 - Number RX Antennas
                                                int(sum(self.radar_param.sys.tx_active_antennas)), # Dim. 3 - Number Chirps per Shape
                                                int(self.radar_param.sys.shape_set_repetition), # Dim. 4 - Shape Set Repetition
                                                 self.radar_param.sys.max_frame_cnt), # Dim. 5
                                                dtype=np.uint16)
        # print(radar_data_cube_build_buffer.shape)
        USB_SPI_BRIDGE_DATA_ALLOCATION = np.uint32(self.config.get("MIRA_USB_SPI_BRIDGE", 
                                                                   f"USB_SPI_BRIDGE_DATA_ALLOCATION_{self.radar_param.mon.sykno_product_name}"))
        DATA_ALLOCATION = np.uint32(USB_SPI_BRIDGE_DATA_ALLOCATION+self.radar_param.sys.n_fifo_overhead*9)

        self.package_chirp_header_index_distance = np.uint32(
            self.radar_param.sys.n_samples_per_chirp[0] * \
            (self.radar_param.sys.rx_active_antennas[0] / \
             sum(self.radar_param.sys.tx_active_antennas)) * self.radar_param.sys.allocation_factor + 9)

        header_matches = list()
        for n_headers in range(np.uint32(DATA_ALLOCATION/self.package_chirp_header_index_distance)):
            header_matches.append(self.package_chirp_header_index_distance*n_headers)
        
        self.data_values = list()
        start_time = time.time()
        self.prev_frame_cnt = np.uint16(0)
        while not process_stop_event.is_set():
            # check multiprocessing queue if there is new data available 
            if not usb_extraction_data_queue.empty():
                # get latest data_cube from radar_bridge_usb_device.raw_data_aquisition() process
                raw_fifo_data = np.asarray(usb_extraction_data_queue.get(), dtype=np.uint8) # ndarray.shape = (12288, )
            else:
                time.sleep(250e-6)
                continue
            # Append the data rate to the array
            self.data_values.append((raw_fifo_data.shape[0] * 8) / (time.time() - start_time))
            
            # Keep only the last 16 values in the array
            self.data_values = self.data_values[-256:]
            start_time = time.time()

            for header_match in header_matches:
                header_values = np.asarray(mira_extract_raw_data.prefix_header_cy(
                                           raw_fifo_data[header_match : header_match + 9]), np.uint32)
                
                # Map the array indices back to your original dictionary keys
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
                
                raw_data_slice = raw_fifo_data[header_match + 9 : header_match + self.package_chirp_header_index_distance]
                data_field = np.asarray(mira_extract_raw_data.extract_raw_data_cy(
                    raw_data_slice,
                    raw_data_slice.shape[0],
                    self.radar_param.sys.rx_active_antennas[0]), dtype=np.uint16)
                if curr_frame_cnt > self.radar_param.sys.max_frame_cnt:
                    frame_cnt = np.mod(curr_frame_cnt, self.radar_param.sys.max_frame_cnt)
                else:
                    frame_cnt = curr_frame_cnt

                shape_grp_cnt = self.header_dict['shape_grp_cnt']
                
                total_active_antennas = sum(self.radar_param.sys.tx_active_antennas)
                grp_dim_index = np.uint16(shape_grp_cnt / total_active_antennas)

                radar_data_cube_build_buffer[:,:, self.header_dict['cs'], grp_dim_index, frame_cnt] = data_field[:,:]
                # radar_data_cube_build_buffer[:,:, 1, grp_dim_index, frame_cnt] = data_field[:,:]

                # if np.all(radar_data_cube_build_buffer[:,:, self.header_dict['cs'], 
                #           np.uint16(self.header_dict['shape_grp_cnt']/sum(self.radar_param.sys.tx_active_antennas)),
                #           frame_cnt] == 0):
                #     radar_data_cube_build_buffer[:,:, self.header_dict['cs'], 
                #                                  np.uint16(self.header_dict['shape_grp_cnt']/sum(self.radar_param.sys.tx_active_antennas)),
                #                                  frame_cnt] = data_field[:,:]
                # else:
                #     combined_chrips = np.concatenate((radar_data_cube_build_buffer[np.newaxis,:,:, 
                #                                  self.header_dict['cs'], 
                #                                  np.uint16(self.header_dict['shape_grp_cnt']/sum(self.radar_param.sys.tx_active_antennas)),
                #                                  frame_cnt], data_field[np.newaxis,:,:]), axis=0, dtype=np.float32)
                #     radar_data_cube_build_buffer[:,:,
                #                                  self.header_dict['cs'], 
                #                                  np.uint16(self.header_dict['shape_grp_cnt']/sum(self.radar_param.sys.tx_active_antennas)),
                #                                  frame_cnt] = np.mean(combined_chrips, axis=0, dtype=np.float32)

           
                if self.prev_frame_cnt != curr_frame_cnt:
                    if self.prev_frame_cnt > self.radar_param.sys.max_frame_cnt:
                        frame_cnt = np.mod(self.prev_frame_cnt, self.radar_param.sys.max_frame_cnt)
                    else:
                        frame_cnt = self.prev_frame_cnt

                    if extracted_processing_data_queue.empty():
                        extracted_processing_data_queue.put(radar_data_cube_build_buffer[:,:,:,:,frame_cnt])
                    
                    if self.radar_param.meas.measurement_flag == True:
                        self.header_dict['frame_cnt'] = frame_cnt
                        save_data_queue.put({'Data': radar_data_cube_build_buffer[:,:,:,:,frame_cnt],
                                             'Header': self.header_dict})

                    self.prev_frame_cnt = curr_frame_cnt
            

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
        
