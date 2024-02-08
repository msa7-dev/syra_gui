import __init__
import time
import h5py
import json
import pickle
import numpy as np
import configparser
from datetime import datetime
from mira.rsys.mira_radar_sys import MIRA_RADAR_PARAMETER
from mira.sens.mira_reg_cont_helper import generate_register_to_txt, \
                                          generate_register_to_readable_txt

# ==============================================================================
# Class Name: MIRA_SAVE_MEAS
# ==============================================================================
class MIRA_SAVE_MEAS():
    def __init__(self, mira_device):
        self.config = configparser.ConfigParser()
        self.config.read(__init__.MIRA_SYS_CONFIG_PATH)
        
        self.curr_time = 0
        self.prev_time = time.time()
        MIRA_MEAS_HDF5_FOLDER_PATH = self.config.get("MIRA_SAVE_MEASUREMENT",
                                                     "MIRA_MEAS_HDF5_FOLDER_PATH")
        MIRA_MEAS_FILENAME = self.config.get("MIRA_SAVE_MEASUREMENT",
                                             "MIRA_MEAS_FILENAME")
        MIRA_MEAS_META_GROUP_NAME = self.config.get("MIRA_SAVE_MEASUREMENT", 
                                                    "MIRA_MEAS_META_GROUP_NAME")
        MIRA_MEAS_META_SYS_INFO = self.config.get("MIRA_SAVE_MEASUREMENT", 
                                                  "MIRA_MEAS_META_SYS_INFO")
        MIRA_MEAS_DATASET_GROUP_NAME = self.config.get("MIRA_SAVE_MEASUREMENT", 
                                                       "MIRA_MEAS_DATASET_GROUP_NAME")
        self.MIRA_MEAS_DATASET_GROUP_NAME = self.config.get("MIRA_SAVE_MEASUREMENT", 
                                                            "MIRA_MEAS_DATASET_GROUP_NAME")
        
        self.radar_param: MIRA_RADAR_PARAMETER = mira_device.radar_param
        self.timestamp = str(datetime.now().strftime('%d_%m_%Y_%H_%M_%S'))

        self.hdf5_file_path = f'{MIRA_MEAS_HDF5_FOLDER_PATH}' + \
                              f'{MIRA_MEAS_FILENAME}_{self.timestamp}.hdf5'
                              
        reg_content_content = generate_register_to_txt(mira_device, save_to_file=False)
        reg_content_content_readable = generate_register_to_readable_txt(mira_device, save_to_file=False)
        
        with h5py.File(self.hdf5_file_path, "a") as file:
            self.metadata_group = file.create_group(MIRA_MEAS_META_GROUP_NAME)
            self.data_group = file.create_group(MIRA_MEAS_DATASET_GROUP_NAME)
            
            self.mira_config_group = self.metadata_group.create_group('mira_config')
            self.mira_config_group.attrs['mira_config'] = self.ini_to_json()
            
            self.radar_parameters_group = self.metadata_group.create_group('mira_radar_parameters')
            radar_param_data = pickle.dumps(self.radar_param)
            self.radar_parameters_group.create_dataset('mira_radar_parameters', data=np.void(radar_param_data))

            self.mira_bgt_reg_content_group = self.metadata_group.create_group('mira_bgt_reg_content')
            self.mira_bgt_reg_content_group.attrs['mira_bgt_reg_content'] = reg_content_content
            
            self.mira_bgt_reg_content_group = self.metadata_group.create_group('mira_bgt_reg_content_readable')
            self.mira_bgt_reg_content_group.attrs['mira_bgt_reg_content_readable'] = reg_content_content_readable

        self.mira_meas_dataset_frame_name = self.config.get("MIRA_SAVE_MEASUREMENT",
                                                            "MIRA_MEAS_DATASET_FRAME_NAME")
        self.dataset_cnt = -1


    def save_to_hdf5(self, frame_data_cube: np.ndarray, header_dict: dict) -> None:
        if header_dict['frame_cnt'] == 0:
            self.dataset_cnt += 1

        dataset_name = f"{self.mira_meas_dataset_frame_name}_{self.dataset_cnt:04d}_{header_dict['frame_cnt']:04d}"

        # Open the HDF5 file in append mode for each process
        with h5py.File(self.hdf5_file_path, "a") as file:
            # Check if the dataset already exists; if not, create it
            if dataset_name not in file[self.MIRA_MEAS_DATASET_GROUP_NAME]:
                # Create a new dataset within the data group
                for tx in range(2):
                    for rx in range(4):
                        for shape in range(16):
                            print(frame_data_cube[:,rx,tx,shape])
                dataset = file[str(self.MIRA_MEAS_DATASET_GROUP_NAME)].create_dataset(
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
