import psutil
import platform
from typing import Optional, List, Tuple
from radar_eval.radar_system.radar_system_definition import SYRA_RADAR_PARAMETER

if platform.system() == "Windows":
    import threading as mp
    import queue
    Process = mp.Thread
    Queue = queue.Queue
    Event = mp.Event
else:
    import multiprocessing as mp
    Process = mp.Process
    Queue = mp.Queue
    Event = mp.Event


class SYRA_MULTIPROCESSOR:
    def __init__(self, syra_controller) -> None:
        self.radar_param: SYRA_RADAR_PARAMETER = syra_controller.radar_param
        self.syra_controller = syra_controller
        self._init_data_queues()
        self._init_signal_events()
        self._init_processes()

    def _init_data_queues(self) -> None:
        """Initialize the data queues for inter-process communication."""
        self.usb_extraction_data_queue = Queue()
        self.update_gui_info_queue = Queue()
        self.extracting_data_queue = Queue()
        self.save_data_queue = Queue()
        self.extracted_processing_data_queue = Queue()
        self.processed_gui_data_queue = Queue()
        self.radar_gui_para_queue = Queue()
        self.process_param_queue = Queue()

        self.data_queues = [
            self.usb_extraction_data_queue, self.update_gui_info_queue,
            self.extracting_data_queue, self.extracted_processing_data_queue,
            self.processed_gui_data_queue, self.radar_gui_para_queue,
            self.process_param_queue, self.save_data_queue
        ]

    def _init_signal_events(self) -> None:
        """Initialize signal events for controlling the processes."""
        self.process_stop_event = Event()
        self.process_stop_event.clear()

    def _init_processes(self) -> None:
        """Initialize all necessary processes based on the current radar parameters."""
        self.data_save_process = self._init_data_save_process()
        self.data_aquisition_process = self._init_data_acquisition_process()
        self.data_extracting_process, self.data_replaying_process = self._init_data_extraction_or_replay_process()
        self.data_transmitting_process = self._init_data_transmitting_process()
        self.data_receiving_process = self._init_data_receiving_process()
        self.data_processing_process = self._init_data_processing_process()

        self.processes: List[Optional[Process]] = [
            self.data_extracting_process, self.data_replaying_process,
            self.data_processing_process, self.data_receiving_process,
            self.data_transmitting_process, self.data_save_process,
            self.data_aquisition_process
        ]

    def _init_data_save_process(self) -> Optional[Process]:
        """Initialize the data saving process if required."""
        if self.radar_param.meas.measurement_flag and self.syra_controller.syra_device.syra_bridge.device is not None:
            return Process(
                name='MiRa_Meas_Save_Process',
                target=self.syra_controller.save_meas.save_to_hdf5_process,
                args=(self.save_data_queue, self.process_stop_event)
            )
        return None

    def _init_data_acquisition_process(self) -> Optional[Process]:
        """Initialize the data acquisition process if required."""
        if (not self.radar_param.remt.remote_flag or self.radar_param.remt.client_flag) and self.syra_controller.syra_device is not None:
            return Process(
                name='MiRa_USB_Aquisition_Process',
                target=self.syra_controller.syra_device.syra_bridge.raw_data_acquisition_process,
                args=(self.usb_extraction_data_queue, self.process_stop_event)
            )
        return None

    def _init_data_extraction_or_replay_process(self) -> Tuple[Optional[Process], Optional[Process]]:
        """Initialize either the data extracting or data replaying process."""
        if self.radar_param.rply.replay_flag:
            return None, Process(
                name='MiRa_Replaying_Process',
                target=self.syra_controller.data_replayer.data_replaying_process,
                args=(
                    self.usb_extraction_data_queue, self.update_gui_info_queue,
                    self.extracted_processing_data_queue, self.save_data_queue,
                    self.process_stop_event, self.radar_gui_para_queue
                )
            )
        else:
            return Process(
                name='MiRa_Extracting_Process',
                target=self.syra_controller.data_extractor.data_extracting_process,
                args=(
                    self.usb_extraction_data_queue, self.update_gui_info_queue,
                    self.extracted_processing_data_queue, self.save_data_queue,
                    self.process_stop_event
                )
            ), None

    def _init_data_transmitting_process(self) -> Optional[Process]:
        """Initialize the data transmitting process if required."""
        if self.radar_param.remt.remote_flag and self.radar_param.remt.client_flag:
            return Process(
                name='MiRa_Remote_Transmitting_Process',
                target=self.syra_controller.data_processor.data_processing_process,
                args=(
                    self.extracted_processing_data_queue, self.processed_gui_data_queue,
                    self.process_param_queue, self.process_stop_event
                )
            )
        return None

    def _init_data_receiving_process(self) -> Optional[Process]:
        """Initialize the data receiving process if required."""
        if self.radar_param.remt.remote_flag and not self.radar_param.remt.client_flag:
            return Process(
                name='MiRa_Remote_Receiving_Process',
                target=self.syra_controller.data_processor.data_processing_process,
                args=(
                    self.extracted_processing_data_queue, self.processed_gui_data_queue,
                    self.process_param_queue, self.process_stop_event
                )
            )
        return None

    def _init_data_processing_process(self) -> Optional[Process]:
        """Initialize the data processing process if required."""
        if not self.radar_param.remt.client_flag:
            return Process(
                name='MiRa_Data_Processing_Process',
                target=self.syra_controller.data_processor.data_processing_process,
                args=(
                    self.extracted_processing_data_queue, self.processed_gui_data_queue,
                    self.process_param_queue, self.process_stop_event
                )
            )
        return None

    def start_processes(self) -> None:
        """Start all initialized processes."""
        for process in self.processes:
            if process is not None:
                process.start()

    def stop_processes(self) -> None:
        """Stop all running processes and clean up resources."""
        for i, process in enumerate(self.processes):
            if process is not None:
                process.terminate()
                process.join()
                self.processes[i] = None


def distribute_cores_to_process(process: Process, process_id: int) -> None:
    """Distribute CPU cores to processes, except on Windows."""
    if platform.system() != "Windows":
        total_cores = psutil.cpu_count(logical=True)
        reserved_cores = {0, 1, 2, 3}  # Reserved for OS and critical tasks
        free_cores = [core for core in range(total_cores) if core not in reserved_cores]

        if process_id in [1, 2, 3]:
            cores_per_process = len(free_cores) // 3
            index = process_id - 1
            additional_cores = free_cores[index * cores_per_process:(index + 1) * cores_per_process]
            current_affinity = process.cpu_affinity()
            new_affinity = list(set(current_affinity + additional_cores))
            process.cpu_affinity(new_affinity)
