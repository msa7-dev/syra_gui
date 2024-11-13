import __init__
import os
import time
import h5py
import json
import psutil
import pickle
import numpy as np
import setproctitle
import configparser
import multiprocessing
from datetime import datetime
from radar_eval.radar_system.radar_system_definition import SYRA_RADAR_PARAMETER
from radar_eval.radar_sensor.radar_sensor_register_helper import generate_register_to_txt, \
                                          generate_register_to_readable_txt

# ==============================================================================
# Class Name: SYRA_SAVE_MEAS
# ==============================================================================
class SYRA_SAVE_MEAS():
    def __init__(self, syra_device):
        self.config = configparser.ConfigParser()
        self.config.read(__init__.SYRA_SYS_CONFIG_PATH)
        
        self.curr_time = 0
        self.prev_time = time.time()
        SYRA_MEAS_HDF5_FOLDER_PATH = self.config.get("SYRA_SAVE_MEASUREMENT",
                                                     "SYRA_MEAS_HDF5_FOLDER_PATH")
        SYRA_MEAS_FILENAME = self.config.get("SYRA_SAVE_MEASUREMENT",
                                             "SYRA_MEAS_FILENAME")
        SYRA_MEAS_META_GROUP_NAME = self.config.get("SYRA_SAVE_MEASUREMENT", 
                                                    "SYRA_MEAS_META_GROUP_NAME")
        SYRA_MEAS_META_SYS_INFO = self.config.get("SYRA_SAVE_MEASUREMENT", 
                                                  "SYRA_MEAS_META_SYS_INFO")
        SYRA_MEAS_DATASET_GROUP_NAME = self.config.get("SYRA_SAVE_MEASUREMENT", 
                                                       "SYRA_MEAS_DATASET_GROUP_NAME")
        self.SYRA_MEAS_DATASET_GROUP_NAME = self.config.get("SYRA_SAVE_MEASUREMENT", 
                                                            "SYRA_MEAS_DATASET_GROUP_NAME")
        
        self.radar_param: SYRA_RADAR_PARAMETER = syra_device.radar_param
        self.timestamp = str(datetime.now().strftime('%d_%m_%Y_%H_%M_%S'))

        self.hdf5_file_path = f'{SYRA_MEAS_HDF5_FOLDER_PATH}' + \
                              f'{self.radar_param.mon.sykno_product_name}_{SYRA_MEAS_FILENAME}_{self.timestamp}_' + \
                              f'{self.radar_param.meas.session_label}.hdf5'
                              
        reg_content_content = generate_register_to_txt(syra_device, save_to_file=False)
        reg_content_content_readable = generate_register_to_readable_txt(syra_device, save_to_file=False)
        
        with h5py.File(self.hdf5_file_path, "a") as file:
            self.metadata_group = file.create_group(SYRA_MEAS_META_GROUP_NAME)
            self.data_group = file.create_group(SYRA_MEAS_DATASET_GROUP_NAME)
            
            self.syra_config_group = self.metadata_group.create_group('syra_config')
            self.syra_config_group.attrs['syra_config'] = self.ini_to_json()
            
            self.radar_parameters_group = self.metadata_group.create_group('syra_radar_parameters')
            radar_param_data = pickle.dumps(self.radar_param)
            self.radar_parameters_group.create_dataset('syra_radar_parameters', data=np.void(radar_param_data))

            self.syra_bgt_reg_content_group = self.metadata_group.create_group('syra_bgt_reg_content')
            self.syra_bgt_reg_content_group.attrs['syra_bgt_reg_content'] = reg_content_content
            
            self.syra_bgt_reg_content_group = self.metadata_group.create_group('syra_bgt_reg_content_readable')
            self.syra_bgt_reg_content_group.attrs['syra_bgt_reg_content_readable'] = reg_content_content_readable

        self.syra_meas_dataset_frame_name = self.config.get("SYRA_SAVE_MEASUREMENT",
                                                            "SYRA_MEAS_DATASET_FRAME_NAME")
        self.dataset_cnt = -1


    def save_to_hdf5_process(self, save_data_queue: multiprocessing.Queue, process_stop_event: multiprocessing.Event) -> None:
        syra_data_extraction_process = psutil.Process(os.getpid())
        syra_data_extraction_process.cpu_affinity([0])
        syra_data_extraction_process.nice(0)
        setproctitle.setproctitle("Sykno - Radar Eval GUI - Save Process")
        
        while not process_stop_event.is_set():
            if not save_data_queue.empty():
                meas_save_dict = save_data_queue.get_nowait()
            else:
                time.sleep(20e-6)
                continue
            header_dict = meas_save_dict['Header']
            frame_data_cube = meas_save_dict['Data']
            
            if header_dict['frame_cnt'] == 0:
                self.dataset_cnt += 1

            dataset_name = f"{self.syra_meas_dataset_frame_name}_{self.dataset_cnt:04d}_{header_dict['frame_cnt']:04d}"

            # Open the HDF5 file in append mode for each process
            with h5py.File(self.hdf5_file_path, "a") as file:
                # Check if the dataset already exists; if not, create it
                if dataset_name not in file[self.SYRA_MEAS_DATASET_GROUP_NAME]:

                    dataset = file[str(self.SYRA_MEAS_DATASET_GROUP_NAME)].create_dataset(
                                                                      name=dataset_name,
                                                                      data=frame_data_cube,
                                                                      shape=frame_data_cube.shape,
                                                                      dtype=np.float32,
                                                                      chunks=True)

                    self.curr_time = time.time()
                    dataset.attrs['timestamp'] = self.curr_time
                    dataset.attrs['delta_time'] = self.curr_time - self.prev_time
                    dataset.attrs['shape'] = str(frame_data_cube.shape)
                    self.prev_time = self.curr_time

    def ini_to_json(self):
        # Convert INI data to a nested dictionary
        config_dict = \
            {section: dict(self.config.items(section)) for section in self.config.sections()}
        # Convert dictionary to JSON string
        return json.dumps(config_dict)
