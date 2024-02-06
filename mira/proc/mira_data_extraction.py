import __init__
from pathlib import Path

import os 
import time
import psutil
import numpy as np
import setproctitle
import configparser
import multiprocessing
from mira.meas.mira_save_meas import MIRA6024_SAVE_MEAS
from mira.rsys.mira_radar_sys import MIRA6024_RADAR_PARAMETER
import mira.proc.mira_cython.mira6024_extract_from_raw_data as mira6024_extract_from_raw_data

# ==============================================================================
# Class Name: MIRA6024_DATA_EXTRACTOR
# ==============================================================================
class MIRA6024_DATA_EXTRACTOR():
    def __init__(self, mira_device):
        self.config = configparser.ConfigParser()
        self.config.read(Path(__init__.MIRA_SYS_CONFIG_PATH).resolve())
        self.mira_device = mira_device
        self.radar_param: MIRA6024_RADAR_PARAMETER = mira_device.radar_param
        if self.radar_param.meas.measurement_flag == True:
            self.save_meas = MIRA6024_SAVE_MEAS(self.mira_device)

    def data_extracting_process(self, raw_fifo_data_queue: multiprocessing.Queue,
                                prefix_header_queue: multiprocessing.Queue, 
                                radar_extracted_queue: multiprocessing.Queue,
                                stop_event: multiprocessing.Event, 
                                set_header_queue_event: multiprocessing.Event,):
        self.prefix_header_queue = prefix_header_queue
        self.set_header_queue_event = set_header_queue_event
                            
        MIRA_PROCESS_PRIO = np.int8(self.config.get("MIRA_HOST_SYS_PARAMETER",
                                                    "MIRA_PROCESS_PRIO"))
        MIRA_EXTRACTING_CPU_CORE = int(self.config.get("MIRA_HOST_SYS_PARAMETER", 
                                                       "MIRA_EXTRACTING_CPU_CORE"))

        current_process = psutil.Process(os.getpid())
        current_process.cpu_affinity([MIRA_EXTRACTING_CPU_CORE])
        current_process.nice(MIRA_PROCESS_PRIO)
        setproctitle.setproctitle("Sykno - MiRa Eval GUI - Extraction Process")
        self.prev_frame_cnt = np.uint16(0)
        print(f"{self.radar_param.sys.rx_active_antennas=}, {self.radar_param.sys.tx_active_antennas=}")
        radar_data_cube_build_buffer = np.zeros((self.radar_param.sys.n_samples_per_chirp[0], # Dim 1 - Samples
                                                int(self.radar_param.sys.rx_active_antennas[0]), # Dim. 2 - Number RX Antennas
                                                int(sum(self.radar_param.sys.tx_active_antennas)), # Dim. 3 - Number Chirps per Shape
                                                self.radar_param.sys.shape_set_repetition, # Dim. 4 - Shape Set Repetition
                                                 self.radar_param.sys.max_frame_cnt), # Dim. 5
                                                dtype=np.uint16)
        
        USB_SPI_BRIDGE_DATA_ALLOCATION = np.uint32(
                self.config.get("MIRA_USB_SPI_BRIDGE", "USB_SPI_BRIDGE_DATA_ALLOCATION"))
        DATA_ALLOCATION = np.uint32(USB_SPI_BRIDGE_DATA_ALLOCATION+self.radar_param.sys.n_fifo_overhead*9)

        self.package_chirp_header_index_distance = np.uint32(
            self.radar_param.sys.n_samples_per_chirp[0] * \
            (self.radar_param.sys.rx_active_antennas[0] / \
             sum(self.radar_param.sys.tx_active_antennas)) * 3 + 9)
        
        header_matches = list()
        for n_headers in range(np.uint32(DATA_ALLOCATION/self.package_chirp_header_index_distance)):
            header_matches.append(self.package_chirp_header_index_distance*n_headers)
        print(header_matches)
        start_time = time.time()
        self.data_values = []
        while not stop_event.is_set():
            # check multiprocessing queue if there is new data available 
            if not raw_fifo_data_queue.empty():
                # get latest data_cube from mira_usb_spi_bridge.raw_data_aquisition() process
                raw_fifo_data = raw_fifo_data_queue.get(block=False) # ndarray.shape = (12288, )
            else:
                time.sleep(500e-6)
                continue
            
            # Append the data rate to the array
            self.data_values.append((raw_fifo_data.shape[0] * 8) / (time.time() - start_time))

            # Keep only the last 16 values in the array
            self.data_values = self.data_values[-128:]
            start_time = time.time()
            
            for header_match in header_matches:

                self.header_dict = mira6024_extract_from_raw_data.prefix_header(
                        raw_fifo_data[header_match : header_match + 9]) # 10 - 50 us
                self._update_header_dict_to_gui()
                curr_frame_cnt = np.uint16(self.header_dict['frame_cnt'])
                
                raw_data = raw_fifo_data[header_match + 9 : header_match +\
                                         self.package_chirp_header_index_distance]
                                
                # raw_data_chunks = raw_data.reshape(-1, 3)
                # raw_data_block_bits = np.unpackbits(raw_data_chunks, axis=1)
                # print(raw_data_block_bits.shape)
                data_field = self._extract_channels(raw_data) # 1 - 3 ms ---> with cython 10-70 us

                if curr_frame_cnt > self.radar_param.sys.max_frame_cnt:
                    frame_cnt = np.mod(curr_frame_cnt, self.radar_param.sys.max_frame_cnt)
                else:
                    frame_cnt = curr_frame_cnt
                
                if np.all(radar_data_cube_build_buffer[:,:, self.header_dict['cs'], 
                          np.uint16(self.header_dict['shape_grp_cnt']/sum(self.radar_param.sys.tx_active_antennas)),
                          frame_cnt] == 0):
                    radar_data_cube_build_buffer[:,:, self.header_dict['cs'], 
                                                 np.uint16(self.header_dict['shape_grp_cnt']/sum(self.radar_param.sys.tx_active_antennas)),
                                                 frame_cnt] = data_field[:,:]
                else:
                    combined_chrips = np.concatenate((radar_data_cube_build_buffer[np.newaxis,:,:, 
                                                 self.header_dict['cs'], 
                                                 np.uint16(self.header_dict['shape_grp_cnt']/sum(self.radar_param.sys.tx_active_antennas)),
                                                 frame_cnt], data_field[np.newaxis,:,:]), axis=0, dtype=np.float32)
                    radar_data_cube_build_buffer[:,:,
                                                 self.header_dict['cs'], 
                                                 np.uint16(self.header_dict['shape_grp_cnt']/sum(self.radar_param.sys.tx_active_antennas)),
                                                 frame_cnt] = np.mean(combined_chrips, axis=0, dtype=np.float32)
                                             
                if self.prev_frame_cnt != curr_frame_cnt:
                    if self.prev_frame_cnt > self.radar_param.sys.max_frame_cnt:
                        frame_cnt = np.mod(self.prev_frame_cnt, self.radar_param.sys.max_frame_cnt)
                    else:
                        frame_cnt = self.prev_frame_cnt

                    if radar_extracted_queue.empty():
                        radar_extracted_queue.put(radar_data_cube_build_buffer[:,:,:,:,frame_cnt])

                    if self.radar_param.meas.measurement_flag == True:
                        self.header_dict['frame_cnt'] = frame_cnt
                        self.save_meas.save_to_hdf5(
                            radar_data_cube_build_buffer[:,:,:,:,frame_cnt], 
                            self.header_dict)

                    self.prev_frame_cnt = curr_frame_cnt

    def _update_header_dict_to_gui(self) -> None:
        if self.set_header_queue_event.is_set():
            self.header_dict['temperature'] = self._convert_sadc_data(self.header_dict['sadc_val'])
            self.header_dict['datarate'] = np.mean(self.data_values) 
            self.prefix_header_queue.put(self.header_dict)
            self.set_header_queue_event.clear()

    def _convert_sadc_data(self, sadc_val: np.uint16) -> np.float32:
        self.radar_param.mon.sadc_output_mode = 0
        self.radar_param.mon.sadc_gain = 1
        if self.radar_param.mon.sadc_output_mode == 0:
            # Temperature Conversion BGT60ATR24 Datasheet: p. 92
            return np.float32(round((((sadc_val/2**10)*1.21 * self.radar_param.mon.sadc_gain)-0.7989)/0.00297, 2))
        elif self.radar_param.mon.sadc_output_mode == 1:
            pass
        else: 
            return np.float32(-42.17) # magic number 
        
    
    def _extract_channels(self, raw_data_block: np.ndarray) -> np.ndarray:
        if   self.radar_param.sys.rx_active_antennas[0] == 4:   
            return mira6024_extract_from_raw_data.extract_channels_cy(
                                raw_data_block).astype(np.uint16)
        elif self.radar_param.sys.rx_active_antennas[0] == 3:
            return mira6024_extract_from_raw_data.rx_mode_3_cy(
                                raw_data_block, self.radar_param.sys.n_samples_per_chirp[0]).astype(np.uint16)
        elif self.radar_param.sys.rx_active_antennas[0] == 2:
            return mira6024_extract_from_raw_data.rx_mode_2_cy(
                                raw_data_block, self.radar_param.sys.n_samples_per_chirp[0]).astype(np.uint16)
        elif self.radar_param.sys.rx_active_antennas[0] == 1:
            return mira6024_extract_from_raw_data.rx_mode_1_cy(
                                raw_data_block, self.radar_param.sys.n_samples_per_chirp[0]).astype(np.uint16)

    