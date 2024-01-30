import __init__
from pathlib import Path

import os 
import time
import psutil
import numpy as np
import configparser
import multiprocessing
import queue
from mira.rsys.mira_radar_sys import MIRA6024_RADAR_PARAMETER

# ==============================================================================
# Class Name: MIRA6024_DATA_PLAYER
# ==============================================================================
class MIRA6024_DATA_SIMULATOR():
    def __init__(self, radar_param):
        self.mira_device = None
        pass
    def data_simulating_process(self, prefix_header_queue: multiprocessing.Queue, 
                                radar_data_extraced_queue: multiprocessing.Queue,
                                stop_event: multiprocessing.Event,
                                set_header_queue_event: multiprocessing.Event,
                                ):
        
        MIRA_PROCESS_PRIO = np.int8(self.config.get("MIRA_HOST_SYS_PARAMETER",
                                                    "MIRA_PROCESS_PRIO"))
        MIRA_EXTRACTING_CPU_CORE = int(self.config.get("MIRA_HOST_SYS_PARAMETER", 
                                                       "MIRA_EXTRACTING_CPU_CORE"))

        current_process = psutil.Process(os.getpid())
        current_process.cpu_affinity([MIRA_EXTRACTING_CPU_CORE])
        
        if os.name == 'nt':  # Windows
            # current_process.nice(psutil.HIGH_PRIORITY_CLASS)
            pass
        else:  # Assume Unix/Linux
            current_process.nice(MIRA_PROCESS_PRIO)
        

        while not stop_event.is_set():
            # check multiprocessing queue if there is new data available 
            try:
                # get latest data_cube from mira_usb_spi_bridge.raw_data_aquisition() process
                raw_fifo_data = raw_fifo_data_queue.get(block=False) # ndarray.shape = (12288, )
                hdf5_load_dataset, header_dict 
            except queue.Empty:
                time.sleep(250e-6)
                continue         
            
            if set_header_queue_event.is_set():
                header_dict['temperature'] = self.convert_sadc_data(header_dict['sadc_val'])
                prefix_header_queue.put(header_dict)
                set_header_queue_event.clear()
                    
                radar_data_extraced_queue.put(hdf5_loaded_frame)
                

    def convert_sadc_data(self, sadc_val: np.uint16) -> None:
        if self.radar_param.mon.sadc_output_mode == 0:
            # Temperature Conversion BGT60ATR24 Datasheet: p. 92
            return round((((sadc_val/2**10)*1.21 * self.radar_param.mon.sadc_gain)-0.7989)/0.00297, 2)
        elif self.radar_param.mon.sadc_output_mode == 1:
            pass
        else: 
            return np.float16(-42.17) # magic number 
        

    def load_meta_data_from_hdf5(self):
        pass 