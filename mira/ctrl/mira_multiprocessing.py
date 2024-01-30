import multiprocessing
from mira.ctrl.mira_ctrl import MIRA6024_CTRL_GUI
from mira.rsys.mira_radar_sys import MIRA6024_RADAR_PARAMETER

class MIRA_MULTIPROCESSOR():
    def __init__(self, mira_controller: MIRA6024_CTRL_GUI) -> None:
        self.radar_param: MIRA6024_RADAR_PARAMETER = mira_controller.radar_param
        self.mira_controller = mira_controller
        self._init_data_queues()
        self._init_signal_events()
        self._init_processes()
        
    def _init_data_queues(self) -> None:
        self.raw_data_queue = multiprocessing.Queue()
        self.update_gui_info_queue = multiprocessing.Queue()
        self.extracting_data_queue = multiprocessing.Queue()
        self.radar_data_cube_queue = multiprocessing.Queue()
        self.radar_plot_map_queue = multiprocessing.Queue()
        self.radar_gui_para_queue = multiprocessing.Queue()
        self.process_param_queue = multiprocessing.Queue()
        
        self.data_queues = [self.raw_data_queue, self.update_gui_info_queue, 
                            self.extracting_data_queue, self.radar_data_cube_queue,
                            self.radar_plot_map_queue, self.radar_gui_para_queue,
                            self.process_param_queue]
    
    def _init_signal_events(self) -> None:
        self.wait_event = multiprocessing.Event()
        self.stop_event = multiprocessing.Event()
        self.set_header_queue_event = multiprocessing.Event()
        self.set_header_queue_event.set()
        self.stop_event.clear()
        
    def _init_processes(self) -> None:
        if self.radar_param.remt.remote_flag == False or \
           self.radar_param.remt.client_flag == True and \
           self.mira_controller.mira_device.mira_bridge.device is not None:
            # Data Aquisition Process - BGT Raw Data via USB Bridge
            self.data_aquisition_process = multiprocessing.Process(
                target=self.mira_controller.mira_device.mira_bridge.raw_data_aquisition_process,
                args=(self.raw_data_queue,
                      self.stop_event))
            self.data_aquisition_process.daemon = True
        else:
            self.data_aquisition_process = None
        
        if self.radar_param.remt.remote_flag == False or \
           self.radar_param.remt.client_flag == True:
            # Data Extracting Process - Extracting BGT Raw Data into Header, RX-Channels
            self.data_extracting_process = multiprocessing.Process(
                target=self.mira_controller.data_extrator.data_extracting_process, 
                args=(self.raw_data_queue, 
                      self.update_gui_info_queue,
                      self.radar_data_cube_queue,
                      self.stop_event, 
                      self.set_header_queue_event))
            self.data_extracting_process.daemon = True
        else:
            self.data_extracting_process = None
        
        if self.mira_controller.radar_param.rply.replay_flag == True:
            # Data Simulating Process - Loads measurement file and puts it in data queue to data processing
            self.data_simulating_process = multiprocessing.Process(
                target=self.mira_controller.data_simulator.data_simulating_process, 
                args=(self.raw_data_queue, 
                      self.update_gui_info_queue,
                      self.radar_data_cube_queue,
                      self.stop_event, 
                      self.set_header_queue_event))
            self.data_extracting_process.daemon = True
        else:
            self.data_simulating_process = None
        
        if self.mira_controller.radar_param.remt.remote_flag == True and \
           self.mira_controller.radar_param.remt.client_flag == True:
            # Data Transmitting Process - Handles the client endpoint of the remote TCP connection
            self.data_transmitting_process = multiprocessing.Process(
                target=self.mira_controller.data_processor.data_processing_process, 
                args=(self.radar_data_cube_queue, 
                      self.radar_plot_map_queue,
                      self.process_param_queue,
                      self.stop_event))
            self.data_processing_process.daemon = True
        else:
            self.data_transmitting_process = None

        if self.mira_controller.radar_param.remt.remote_flag == True and \
           self.mira_controller.radar_param.remt.client_flag == False:
            # Data Receiving Process - Handles the host endpoint of the remote TCP connection
            self.data_receiving_process = multiprocessing.Process(
                target=self.mira_controller.data_processor.data_processing_process, 
                args=(self.radar_data_cube_queue,
                      self.radar_plot_map_queue,
                      self.process_param_queue,
                      self.stop_event))
            self.data_processing_process.daemon = True
        else:
            self.data_receiving_process = None
        
        if self.mira_controller.radar_param.remt.client_flag == False:
            # Data Processing Process - Performing Preprocessing and Radar Data Cube calculations
            self.data_processing_process = multiprocessing.Process(
                target=self.mira_controller.data_processor.data_processing_process, 
                args=(self.radar_data_cube_queue, 
                      self.radar_plot_map_queue,
                      self.process_param_queue,
                      self.stop_event))
            self.data_processing_process.daemon = True
        else:
            self.data_processing_process = None
        
        self.processes = [self.data_processing_process, 
                          self.data_extracting_process,
                          self.data_transmitting_process,
                          self.data_receiving_process,
                          self.data_aquisition_process,
                          self.data_simulating_process]
        
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

