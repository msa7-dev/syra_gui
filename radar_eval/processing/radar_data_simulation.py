import __init__
import os
import time
import psutil
import numpy as np
import setproctitle
import configparser
import multiprocessing
from pathlib import Path
from datetime import datetime
from radar_eval.measurement.hdf5_controller import SYRA_HDF5_CTRL

class SYRA_DATA_REPLAYER:
    def __init__(self, hdf5_filename='./radar_eval/measurement/hdf5/SY60I13_Measurement_24_07_2024_17_03_47_Default_Session.hdf5'):
        self.config = configparser.ConfigParser()
        self.config.read(__init__.SYRA_SYS_CONFIG_PATH)
        self.hdf5_ctrl = SYRA_HDF5_CTRL(Path(hdf5_filename).resolve())
        self.data_index = 0
        
        # Load radar parameters from the HDF5 file
        self.hdf5_ctrl.load_metadata()  # Load all metadata
        self.radar_param = self.hdf5_ctrl.unpickle_metadata()  # Load radar parameters
        
        self.frame_duration = 1 / self.radar_param.sys.frames_per_second  # Calculate frame duration

    def extract_frame_number(self, dataset_name):
        """Extract the frame number from the dataset name."""
        parts = dataset_name.split('_')
        return int(parts[-1])

    def data_replaying_process(self, usb_extraction_data_queue: multiprocessing.Queue,
                               prefix_header_queue: multiprocessing.Queue,
                               extracted_processing_data_queue: multiprocessing.Queue,
                               save_data_queue: multiprocessing.Queue,
                               stop_event: multiprocessing.Event,
                               set_header_queue_event: multiprocessing.Event):
        SYRA_PROCESS_PRIO = np.int8(self.config.get("SYRA_HOST_SYS_PARAMETER", "SYRA_PROCESS_PRIO"))
        SYRA_EXTRACTING_CPU_CORE = int(self.config.get("SYRA_HOST_SYS_PARAMETER", "SYRA_EXTRACTING_CPU_CORE"))

        current_process = psutil.Process(os.getpid())
        current_process.cpu_affinity([SYRA_EXTRACTING_CPU_CORE])
        current_process.nice(SYRA_PROCESS_PRIO)

        radar_data_cube_build_buffer = np.zeros((self.radar_param.sys.n_samples_per_chirp[0],  # Dim 1 - Samples
                                                int(self.radar_param.sys.rx_active_antennas[0]),  # Dim 2 - Number RX Antennas
                                                int(sum(self.radar_param.sys.tx_active_antennas)),  # Dim 3 - Number Chirps per Shape
                                                int(self.radar_param.sys.shape_set_repetition),  # Dim 4 - Shape Set Repetition
                                                self.radar_param.sys.max_frame_cnt),  # Dim 5
                                                dtype=np.uint16)

        start_time = time.time()
        self.prev_frame_cnt = np.uint16(0)

        while not stop_event.is_set():
            frame_start_time = time.time()  # Record the start time of the frame

            dataset_names = self.hdf5_ctrl.list_all_datasets()
            if self.data_index >= len(dataset_names):
                self.data_index = 0  # Reset to loop over the data if end is reached
            
            dataset_name = dataset_names[self.data_index]
            dataset_path = f'/{dataset_name}'

            data_cube, attrs = self.hdf5_ctrl.read_dataset_with_attributes(dataset_path)
            if data_cube is not None and attrs is not None:
                frame_number = self.extract_frame_number(dataset_name)
                radar_data_cube_build_buffer[:, :, :, :, frame_number] = data_cube

                if extracted_processing_data_queue.empty():
                    extracted_processing_data_queue.put(radar_data_cube_build_buffer[:, :, :, :, frame_number])

                if self.radar_param.meas.measurement_flag:
                    save_data_queue.put({'Data': radar_data_cube_build_buffer[:, :, :, :, frame_number], 
                                         'Header': attrs})

            self.data_index += 1

            frame_end_time = time.time()  # Record the end time of the frame
            elapsed_time = frame_end_time - frame_start_time

            # Sleep for the remaining time to match the frame duration
            if elapsed_time < self.frame_duration:
                time.sleep(self.frame_duration - elapsed_time)

def print_hdf5_file_contents(file_path):
    with h5py.File(file_path, 'r') as file:
        def print_attrs(name, obj):
            print(f"{name}")
            for key, val in obj.attrs.items():
                print(f"  Attribute: {key} = {val}")

        file.visititems(print_attrs)
