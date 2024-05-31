import psutil
import multiprocessing
from radar_eval.radar_system.radar_system_definition import MIRA_RADAR_PARAMETER

class MIRA_MULTIPROCESSOR():
    def __init__(self, mira_controller) -> None:
        self.radar_param: MIRA_RADAR_PARAMETER = mira_controller.radar_param
        self.mira_controller = mira_controller
        self._init_data_queues()
        self._init_signal_events()
        self._init_processes()
        
    def _init_data_queues(self) -> None:
        self.usb_extraction_data_queue = multiprocessing.Queue()
        self.update_gui_info_queue = multiprocessing.Queue()
        self.extracting_data_queue = multiprocessing.Queue()
        self.save_data_queue = multiprocessing.Queue()
        self.extracted_processing_data_queue = multiprocessing.Queue()
        self.processed_gui_data_queue = multiprocessing.Queue()
        self.radar_gui_para_queue = multiprocessing.Queue()
        self.process_param_queue = multiprocessing.Queue()
        
        self.data_queues = [self.usb_extraction_data_queue, self.update_gui_info_queue, 
                            self.extracting_data_queue, self.extracted_processing_data_queue,
                            self.processed_gui_data_queue, self.radar_gui_para_queue,
                            self.process_param_queue, self.save_data_queue]
    
    def _init_signal_events(self) -> None:
        self.process_stop_event = multiprocessing.Event()
        self.process_stop_event.clear()
        
    def _init_processes(self) -> None:
        if self.radar_param.meas.measurement_flag and \
           self.mira_controller.mira_device.mira_bridge.device is not None:
            # Data Aquisition Process - BGT Raw Data via USB Bridge
            self.data_save_process = multiprocessing.Process(
                name='MiRa_Meas_Save_Process',
                target=self.mira_controller.save_meas.save_to_hdf5_process,
                args=(self.save_data_queue,
                      self.process_stop_event))
            self.data_save_process.daemon = True
        else:
            self.data_save_process = None
        
        if self.radar_param.remt.remote_flag == False or \
           self.radar_param.remt.client_flag == True and \
           self.mira_controller.mira_device.mira_bridge.device is not None:
            # Data Aquisition Process - BGT Raw Data via USB Bridge
            self.data_aquisition_process = multiprocessing.Process(
                name='MiRa_USB_Aquisition_Process',
                target=self.mira_controller.mira_device.mira_bridge.raw_data_aquisition_process,
                args=(self.usb_extraction_data_queue,
                      self.process_stop_event))
            self.data_aquisition_process.daemon = True
        else:
            self.data_aquisition_process = None
        
        if self.radar_param.remt.remote_flag == False or \
           self.radar_param.remt.client_flag == True:
            # Data Extracting Process - Extracting BGT Raw Data into Header, RX-Channels
            self.data_extracting_process = multiprocessing.Process(
                name='MiRa_Extracting_Process',
                target=self.mira_controller.data_extrator.data_extracting_process, 
                args=(self.usb_extraction_data_queue, 
                      self.update_gui_info_queue,
                      self.extracted_processing_data_queue,
                      self.save_data_queue,
                      self.process_stop_event))
            self.data_extracting_process.daemon = True
        else:
            self.data_extracting_process = None
        
        if self.mira_controller.radar_param.rply.replay_flag == True:
            # Data Simulating Process - Loads measurement file and puts it in data queue to data processing
            self.data_simulating_process = multiprocessing.Process(
                name='MiRa_Simulating_Process',
                target=self.mira_controller.data_simulator.data_simulating_process, 
                args=(self.usb_extraction_data_queue, 
                      self.update_gui_info_queue,
                      self.extracted_processing_data_queue,
                      self.process_stop_event))
            self.data_extracting_process.daemon = True
        else:
            self.data_simulating_process = None
        
        if self.mira_controller.radar_param.remt.remote_flag == True and \
           self.mira_controller.radar_param.remt.client_flag == True:
            # Data Transmitting Process - Handles the client endpoint of the remote TCP connection
            self.data_transmitting_process = multiprocessing.Process(
                name='MiRa_Remote_Transmitting_Process',
                target=self.mira_controller.data_processor.data_processing_process, 
                args=(self.extracted_processing_data_queue, 
                      self.processed_gui_data_queue,
                      self.process_param_queue,
                      self.process_stop_event))
            self.data_processing_process.daemon = True
        else:
            self.data_transmitting_process = None

        if self.mira_controller.radar_param.remt.remote_flag == True and \
           self.mira_controller.radar_param.remt.client_flag == False:
            # Data Receiving Process - Handles the host endpoint of the remote TCP connection
            self.data_receiving_process = multiprocessing.Process(
                name='MiRa_Remote_Receiving_Process',
                target=self.mira_controller.data_processor.data_processing_process, 
                args=(self.extracted_processing_data_queue,
                      self.processed_gui_data_queue,
                      self.process_param_queue,
                      self.process_stop_event))
            self.data_processing_process.daemon = True
        else:
            self.data_receiving_process = None
        
        if self.mira_controller.radar_param.remt.client_flag == False:
            # Data Processing Process - Performing Preprocessing and Radar Data Cube calculations
            self.data_processing_process = multiprocessing.Process(
                name='MiRa_Data_Processing_Process',
                target=self.mira_controller.data_processor.data_processing_process, 
                args=(self.extracted_processing_data_queue, 
                      self.processed_gui_data_queue,
                      self.process_param_queue,
                      self.process_stop_event))
            self.data_processing_process.daemon = True
        else:
            self.data_processing_process = None
        
        self.processes = [self.data_extracting_process,
                          self.data_processing_process, 
                          self.data_receiving_process,
                          self.data_transmitting_process,
                          self.data_simulating_process,
                          self.data_save_process,
                          self.data_aquisition_process]
        
    def start_processes(self) -> None:
        for process in self.processes:
            if process is not None:
                process.start()
            else:
                continue
            
    def stop_processes(self) -> None:
        for i, process in enumerate(self.processes):
            if process is not None:
                process.terminate()
                process.join()

            self.processes[i] = None

def distribute_cores_to_process(process: multiprocessing.Process, process_id):
    total_cores = psutil.cpu_count(logical=True)
    # Reserved cores are 0, 1, 2, and 3 for process_1, process_2, process_3, and process_4
    reserved_cores = {0, 1, 2, 3}
    free_cores = [core for core in range(total_cores) if core not in reserved_cores]

    # Only process_1, process_2, and process_3 should receive additional cores
    if process_id in [1, 2, 3]:
        # Calculate the number of free cores to distribute to each of the first three processes
        cores_per_process = len(free_cores) // 3
        index = process_id - 1  # Adjusting index since process_id starts from 1
        additional_cores = free_cores[index*cores_per_process:(index+1)*cores_per_process]
        # Set the new affinity for the process including the additional cores
        current_affinity = process.cpu_affinity()
        new_affinity = list(set(current_affinity + additional_cores))  # Remove duplicates if any
        process.cpu_affinity(new_affinity)
