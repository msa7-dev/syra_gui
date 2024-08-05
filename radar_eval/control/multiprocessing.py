import psutil
import platform
from radar_eval.radar_system.radar_system_definition import MIRA_RADAR_PARAMETER

if platform.system() == "Windows":
    import threading as mp
    import queue
    Process = mp.Thread
    Queue = queue
    Event = mp.Event
else:
    import multiprocessing as mp
    Process = mp.Process
    Queue = mp.Queue
    Event = mp.Event

from radar_eval.radar_system.radar_system_definition import MIRA_RADAR_PARAMETER

class MIRA_MULTIPROCESSOR():
    def __init__(self, mira_controller) -> None:
        self.radar_param: MIRA_RADAR_PARAMETER = mira_controller.radar_param
        self.mira_controller = mira_controller
        self._init_data_queues()
        self._init_signal_events()
        self._init_processes()
        
    def _init_data_queues(self) -> None:
        self.usb_extraction_data_queue = Queue()
        self.update_gui_info_queue = Queue()
        self.extracting_data_queue = Queue()
        self.save_data_queue = Queue()
        self.extracted_processing_data_queue = Queue()
        self.processed_gui_data_queue = Queue()
        self.radar_gui_para_queue = Queue()
        self.process_param_queue = Queue()
        
        self.data_queues = [self.usb_extraction_data_queue, self.update_gui_info_queue, 
                            self.extracting_data_queue, self.extracted_processing_data_queue,
                            self.processed_gui_data_queue, self.radar_gui_para_queue,
                            self.process_param_queue, self.save_data_queue]
    
    def _init_signal_events(self) -> None:
        self.process_stop_event = Event()
        self.process_stop_event.clear()
        
    def _init_processes(self) -> None:
        if self.radar_param.meas.measurement_flag and            self.mira_controller.mira_device.mira_bridge.device is not None:
            self.data_save_process = Process(
                name='MiRa_Meas_Save_Process',
                target=self.mira_controller.save_meas.save_to_hdf5_process,
                args=(self.save_data_queue,
                      self.process_stop_event))
        else:
            self.data_save_process = None
        
        if (self.radar_param.remt.remote_flag == False or            self.radar_param.remt.client_flag == True) and            self.mira_controller.mira_device is not None:
            self.data_aquisition_process = Process(
                name='MiRa_USB_Aquisition_Process',
                target=self.mira_controller.mira_device.mira_bridge.raw_data_aquisition_process,
                args=(self.usb_extraction_data_queue,
                      self.process_stop_event))
        else:
            self.data_aquisition_process = None
        
        if self.radar_param.rply.replay_flag:
            self.data_replaying_process = Process(
                name='MiRa_Replaying_Process',
                target=self.mira_controller.data_replayer.data_replaying_process, 
                args=(self.usb_extraction_data_queue, 
                      self.update_gui_info_queue,
                      self.extracted_processing_data_queue,
                      self.save_data_queue,
                      self.process_stop_event,
                      self.radar_gui_para_queue))
            self.data_extracting_process = None
        else:
            self.data_extracting_process = Process(
                name='MiRa_Extracting_Process',
                target=self.mira_controller.data_extrator.data_extracting_process, 
                args=(self.usb_extraction_data_queue, 
                      self.update_gui_info_queue,
                      self.extracted_processing_data_queue,
                      self.save_data_queue,
                      self.process_stop_event))
            self.data_replaying_process = None
        
        if self.radar_param.remt.remote_flag and            self.radar_param.remt.client_flag:
            self.data_transmitting_process = Process(
                name='MiRa_Remote_Transmitting_Process',
                target=self.mira_controller.data_processor.data_processing_process, 
                args=(self.extracted_processing_data_queue, 
                      self.processed_gui_data_queue,
                      self.process_param_queue,
                      self.process_stop_event))
        else:
            self.data_transmitting_process = None

        if self.radar_param.remt.remote_flag and            not self.radar_param.remt.client_flag:
            self.data_receiving_process = Process(
                name='MiRa_Remote_Receiving_Process',
                target=self.mira_controller.data_processor.data_processing_process, 
                args=(self.extracted_processing_data_queue,
                      self.processed_gui_data_queue,
                      self.process_param_queue,
                      self.process_stop_event))
        else:
            self.data_receiving_process = None
        
        if not self.radar_param.remt.client_flag:
            self.data_processing_process = Process(
                name='MiRa_Data_Processing_Process',
                target=self.mira_controller.data_processor.data_processing_process, 
                args=(self.extracted_processing_data_queue, 
                      self.processed_gui_data_queue,
                      self.process_param_queue,
                      self.process_stop_event))
        else:
            self.data_processing_process = None
        
        self.processes = [self.data_extracting_process,
                          self.data_replaying_process,
                          self.data_processing_process, 
                          self.data_receiving_process,
                          self.data_transmitting_process,
                          self.data_save_process,
                          self.data_aquisition_process]
        
    def start_processes(self) -> None:
        for process in self.processes:
            if process is not None:
                process.start()
            
    def stop_processes(self) -> None:
        for i, process in enumerate(self.processes):
            if process is not None:
                process.terminate()
                process.join()

            self.processes[i] = None

def distribute_cores_to_process(process: mp.Process, process_id):
    
    if platform.system() != "Windows":  # Only adjust affinity if not on Windows
        total_cores = psutil.cpu_count(logical=True)
        reserved_cores = {0, 1, 2, 3}
        free_cores = [core for core in range(total_cores) if core not in reserved_cores]

        if process_id in [1, 2, 3]:
            cores_per_process = len(free_cores) // 3
            index = process_id - 1
            additional_cores = free_cores[index*cores_per_process:(index+1)*cores_per_process]
            current_affinity = process.cpu_affinity()
            new_affinity = list(set(current_affinity + additional_cores))
            process.cpu_affinity(new_affinity)
