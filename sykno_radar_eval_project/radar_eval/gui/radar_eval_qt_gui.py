import __init__
import os
import sys
import time
import psutil
import platform
import numpy as np
import configparser
import setproctitle
from pathlib import Path
from loguru import logger
from threading import Thread
from typing import Dict, Tuple
from PyQt5 import uic, QtCore, QtWidgets
from radar_eval.control.controller import SYRA_CTRL_GUI
from radar_eval.radar_system.radar_system_definition import SYRA_RADAR_PARAMETER
from radar_eval.gui.gui_control import SYRA_GUI_CTRL, init_gui_window, init_gui_qtwidgets
from radar_eval.control.multiprocessing import SYRA_MULTIPROCESSOR, distribute_cores_to_process
from scipy.signal import find_peaks, convolve

# ==============================================================================
# Class Name: SYRA_MAIN_GUI
# ==============================================================================
class SYRA_MAIN_GUI(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        """
        Initialize the main GUI window and setup configurations, paths, and system properties.
        """
        super(SYRA_MAIN_GUI, self).__init__()
        self._load_config()
        self._set_ui_path()
        self._set_system_affinity()
        self._load_ui()

        logger.debug("Start Sykno MiRa Evaluation GUI")

        self._initialize_state_variables()
        self._initialize_data_structures()
        self.range_doppler_buffer = np.ndarray((544,272,4,5), dtype=np.float32)

    def _load_config(self) -> None:
        """
        Load the configuration file.
        """
        self.config = configparser.ConfigParser()
        self.config.read(__init__.SYRA_SYS_CONFIG_PATH)

    def _set_ui_path(self) -> None:
        """
        Set the UI file path for PyQt.
        """
        SYRA_UI_PYQT_FILE_PATH = self.config.get("SYRA_6024_EVAL_GUI", "SYRA_UI_PYQT_FILE_PATH")
        ui_pyqt_file_paths = [Path(SYRA_UI_PYQT_FILE_PATH).resolve(), Path(SYRA_UI_PYQT_FILE_PATH).resolve()]

        for n, path in enumerate(ui_pyqt_file_paths):
            if path.is_file():
                self.SYRA_UI_PYQT_FILE_PATH = path
                break
            elif n == len(ui_pyqt_file_paths) - 1:
                logger.error(f'Error 404: Radar GUI PyQt file not found! Searched here: {path}')
                sys.exit()

    def _set_system_affinity(self) -> None:
        """
        Set system affinity for the process if not on Windows.
        """
        if platform.system() != "Windows":
            setproctitle.setproctitle('Sykno - Radar Eval GUI - GUI Process')
            syra_eval_gui_main_process = psutil.Process(os.getpid())
            syra_eval_gui_main_process.cpu_affinity([3])
            syra_eval_gui_main_process.nice(0)
            distribute_cores_to_process(syra_eval_gui_main_process, 3)

    def _load_ui(self) -> None:
        """
        Load the UI file.
        """
        uic.loadUi(f"{self.SYRA_UI_PYQT_FILE_PATH}", self)

    def _initialize_state_variables(self) -> None:
        """
        Initialize state variables.
        """
        self.running = False
        self.syra_processor = None
        self.syra_controller = None
        self.graph_update_flag = False
        self.ups = 2
        self.fps_timer = None
        self.connect_timer = None
        self.update_gui_timer = None
        self.frame_cnt = np.uint64(0)
        self.prev_frame_cnt = 0

    def _initialize_data_structures(self) -> None:
        """
        Initialize the data structures for radar data.
        """
        self.prev_processed_radar_data_shape = {
            'Channel 1': (2, 2, 2),
            'Channel 2': (2, 2, 2),
            'Channel 3': (2, 2, 2)
        }
        self.processed_radar_data = {
            'Channel 1': np.zeros((1, 1, 1), dtype=np.float32),
            'Channel 2': np.zeros((1, 1, 1), dtype=np.float32),
            'Channel 3': np.zeros((1, 1, 1), dtype=np.float32)
        }

    def set_updates_per_sec(self, timer: QtCore.QTimer, fps: int) -> None:
        """
        Set the updates per second for a given timer.
        
        Parameters:
        - timer: QtCore.QTimer - The timer to set the update interval for.
        - fps: int - Frames per second.
        """
        timer.start(int(1000 / fps))  # Interval in milliseconds

    def syra_gui_main() -> None:
        init_gui_qtwidgets()
        app = QtWidgets.QApplication(sys.argv)
        main = SYRA_MAIN_GUI()
        app = init_gui_window(app, main)
        main.show()
        main.init_gui_controller()
        app.exec_()

    def init_gui_controller(self) -> None:
        """
        Initialize the GUI controller and related components.
        """
        self.radar_param = SYRA_RADAR_PARAMETER()
        self.gui_controller = SYRA_GUI_CTRL(self, self.radar_param)
        self.start_auto_connect()
        self.gui_version = self.config.get("DEFAULT", "VERSION")
        self.syra_gui_main_window_down_label.setText(f"Radar Eval GUI (v{self.gui_version}) | Sykno GmbH")

    def auto_connect_device(self) -> None:
        """
        Automatically connect the radar device if possible.
        """
        if self.syra_controller is None:
            self.syra_controller = SYRA_CTRL_GUI(self.radar_param)
            if self.syra_controller.syra_device is None:
                self.syra_controller = None
                return
            if self.gui_controller is None:
                return
            
            self._initialize_device()
            self.gui_controller.set_device_connected()
            self.gui_controller.update_radar_params()

    def _initialize_device(self) -> None:
        """
        Helper function to initialize the radar device.
        """
        self.gui_controller.update_gui_sensor_detected()
        self.gui_controller.update_sensor_settings(flag=False)
        self.syra_controller.syra_device.init_radar_system_parameters()

        self.firmware_version_label.setText(f"{self.radar_param.mon.product_usb.split('(')[1].replace(') |', '')}")

    def start_auto_connect(self) -> None:
        """
        Start the automatic connection timer if enabled in the configuration.
        """
        if self.radar_param.gui.auto_connect_device:
            self.connect_timer = QtCore.QTimer()
            self.connect_timer.timeout.connect(self.auto_connect_device)
            self.set_updates_per_sec(self.connect_timer, 1)

    def disconnect_device(self) -> None:
        """
        Disconnect the radar device.
        """
        if self.syra_controller and self.syra_controller.syra_device:
            self.syra_controller.syra_device.syra_bridge.deinit_stm_usb_device()
        self.syra_controller = None

    def start_stop(self) -> None:
        """
        Start or stop the processing threads based on the current state.
        """
        if not self.running:
            self._start_processing()
        else:
            self._stop_processing()

    def _start_processing(self) -> None:
        """
        Helper function to start processing.
        """
        self._set_plot_channel_order()
        self._reset_state_for_start()

        if self.syra_controller is None:
            self.syra_controller = SYRA_CTRL_GUI(self.radar_param)

        if self.syra_controller.syra_device is None and not self.radar_param.rply.replay_flag:
            self.syra_controller = None
            self.button_startstop.setText("Start")
            return
        else:
            self.button_startstop.setText("Stop")

        self._initialize_processing_components()
        self.running = True
        self.graph_update_flag = False
        self.start_time = time.time()

    def _stop_processing(self) -> None:
        """
        Helper function to stop processing.
        """
        self.button_startstop.setText("Start")
        self._stop_threads_and_reset_state()
        self._disconnect_device_and_restart_auto_connect()

    def _set_plot_channel_order(self) -> None:
        """
        Helper function to set the plot channel order based on product name.
        """
        product_name = self.radar_param.mon.sykno_product_name
        if product_name == 'MiRa6024I1A':
            self.plot_channel_order_list = ['RX1 TX1', 'RX2 TX1', 'RX3 TX1', 'RX4 TX1', 'RX1 TX2', 'RX2 TX2', 'RX3 TX2', 'RX4 TX2']
        elif product_name == 'SY60I13':
            self.plot_channel_order_list = ['RX1 TX1', 'RX2 TX1', 'RX3 TX1']
        elif product_name == 'SY60I11':
            self.plot_channel_order_list = ['RX1 TX1']
        else:
            self.plot_channel_order_list = ['RX1 TX1']

    def _reset_state_for_start(self) -> None:
        """
        Helper function to reset necessary state variables for starting.
        """
        self.button_startstop.clicked.disconnect()
        self.prev_time = 0
        self.frame_cnt = 0
        self.prev_frame_cnt = 0
        self.button_startstop.clicked.connect(self.start_stop)

    def _initialize_processing_components(self) -> None:
        """
        Helper function to initialize all components necessary for processing.
        """
        self.gui_controller.update_gui_sensor_detected()
        self.gui_controller.update_sensor_settings()
        self.syra_controller.syra_device.activate_rf_test_mode()

        self.syra_controller.reinit_controller(self.gui_controller.radar_param)
        self.syra_processor = SYRA_MULTIPROCESSOR(self.syra_controller)

        self.syra_controller.syra_device.finish_init()
        self.gui_controller.update_radar_params()
        self.syra_controller.syra_device.init_syra_frame_generation()

        self.syra_processor.start_processes()

    def _stop_threads_and_reset_state(self) -> None:
        """
        Helper function to stop threads and reset necessary state variables.
        """
        self.syra_processor.process_stop_event.set()
        self.running = False
        self.graph_update_flag = False
        time.sleep(0.125)
        self.syra_processor.stop_processes()

    def _disconnect_device_and_restart_auto_connect(self) -> None:
        """
        Helper function to disconnect the device and restart auto connect.
        """
        if self.syra_controller and self.syra_controller.syra_device:
            self.syra_controller.syra_device.syra_bridge.deinit_stm_usb_device()
        self.syra_controller = None
        self.start_auto_connect()

    def start_gui_event_timer(self) -> None:
        """
        Start the GUI event timer for updating the GUI and plot.
        """
        self._stop_existing_timers()

        self.update_gui_timer = QtCore.QTimer()
        self.update_gui_timer.timeout.connect(self.update_gui)
        self.set_updates_per_sec(self.update_gui_timer, self.ups)

        if not self.radar_param.meas.record_headless:
            self.fps_timer = QtCore.QTimer()
            self.fps_timer.timeout.connect(self.update_plot)
            self.set_updates_per_sec(self.fps_timer, self.radar_param.gui.fps)

    def _stop_existing_timers(self) -> None:
        """
        Helper function to stop existing timers if they are running.
        """
        if self.fps_timer:
            self.fps_timer.stop()
            self.fps_timer.timeout.disconnect()
        if self.update_gui_timer:
            self.update_gui_timer.stop()
            self.update_gui_timer.timeout.disconnect()

    def connect_tcp_client(self) -> None:
        return
        """
        Connect to a remote TCP client for remote control.
        """
        if not self.tcp_remote_control_checkBox.isChecked():
            return

        self.tcp_client = SYRA_TCP_CLIENT(
            self.radar_param.remt.client_ip_port[0],
            self.radar_param.remt.client_ip_port[1],
            self.radar_param.remt.client_ssh_name,
            self.radar_param.remt.client_ssh_pwd
        )
        try:
            server_thread = Thread(target=self.tcp_client.start)
            server_thread.start()
            input("Press Enter to stop the server...")
            self.tcp_client.close()
            server_thread.join()
        except KeyboardInterrupt:
            self.tcp_client.close()

    def update_gui(self) -> None:
        """
        Update the GUI components periodically based on the current radar data.
        """
        if self.running and not self.syra_processor.update_gui_info_queue.empty():
            update_info_dict = self.syra_processor.update_gui_info_queue.get_nowait()
            self._update_monitoring_info(update_info_dict)
            self._update_gui_components()

    def _update_monitoring_info(self, update_info_dict: Dict[str, str]) -> None:
        """
        Helper function to update monitoring information.
        """
        self.radar_param.mon.temperature = float(update_info_dict['temperature'])
        self.radar_param.mon.duration_frame_counter = int(update_info_dict['frame_cnt'])
        self.radar_param.mon.datarate = float(update_info_dict['datarate'])

    def _update_gui_components(self) -> None:
        """
        Helper function to update GUI components like data rate, frame count, temperature, and duration time.
        """
        self.update_datarate()
        self.update_frame_cnt()
        self.update_temperature()
        self.update_duration_time()

    def update_frame_cnt(self) -> None:
        """
        Update the label to display the current frame count.
        """
        self.frame_cnt += np.uint64(self.radar_param.sys.frames_per_second / 2)
        self.label_frame_counter.setText(str(np.uint64(self.frame_cnt)))

    def update_duration_time(self) -> None:
        """
        Update the label to display the elapsed time.
        """
        self.current_time = time.time()
        self.elapsed_time = self.current_time - self.start_time

        if self.current_time - self.prev_time >= 1:
            hours, remainder = divmod(self.elapsed_time, 3600)
            minutes, seconds = divmod(remainder, 60)
            self.radar_param.mon.duration_time = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
            self.label_duration_time.setText(self.radar_param.mon.duration_time)
            self.prev_time = self.current_time

    def update_temperature(self) -> None:
        """
        Update the label to display the current temperature.
        """
        if self.radar_param.mon.temperature >= -99:  # Random out-of-range number
            self.label_temperature.setText(f'{round(self.radar_param.mon.temperature, 2)} °C')

    def update_datarate(self) -> None:
        """
        Update the label to display the current data rate.
        """
        self.label_datarate.setText(f'{round(self.radar_param.mon.datarate * 1e-6, 2)} Mbps')

    def update_plot(self) -> None:
        """
        Update the plot with the latest processed radar data.
        """
        if self.running and not self.graph_update_flag and not self.syra_processor.process_stop_event.is_set():
            if self.syra_processor.processed_gui_data_queue.empty():
                return
            if not self.syra_processor.process_param_queue.empty():
                while not self.syra_processor.processed_gui_data_queue.empty():
                    self.syra_processor.processed_gui_data_queue.get_nowait()
                return

            processed_data_dict = self.syra_processor.processed_gui_data_queue.get(block=False)
            self.process_info = processed_data_dict['Process Info']
            self.processed_radar_data = processed_data_dict['Processed Data']

            if self.process_info['Process Name'] != self.gui_controller.tab_name_main_instance_window:
                return
            self.gui_controller.update_pipeline.call_plot_pipeline(self.process_info['Process Name'], None)
        else:
            self.graph_update_flag = False

    def check_plot_shape(self, dummy: None) -> None:
        """
        Check if the plot shape has changed and update the GUI accordingly.
        """
        if self._is_plot_shape_changed():
            self._update_previous_plot_shape()
            self.gui_controller.get_axis_x()
        else:
            self.graph_update_flag = True
        return dummy

    def _is_plot_shape_changed(self) -> bool:
        """
        Helper function to check if the plot shape has changed.
        """
        return any(
            self.processed_radar_data[channel].shape != self.prev_processed_radar_data_shape[channel]
            for channel in self.prev_processed_radar_data_shape
        )

    def _update_previous_plot_shape(self) -> None:
        """
        Helper function to update the previous plot shape.
        """
        for channel in self.prev_processed_radar_data_shape:
            self.prev_processed_radar_data_shape[channel] = self.processed_radar_data[channel].shape

    def plot_ready(self, dummy: None) -> None:
        """
        Mark the plot as ready for updating.
        """
        self.graph_update_flag = False
        return dummy


    def set_time_signal(self, dummy: None) -> None:
        """
        Set the time signal for the radar data plot.
        """
        if self.running and self.graph_update_flag:
            self._plot_time_signals()
        return dummy

    def _plot_time_signals(self) -> None:
        """
        Helper function to plot the time signals for each channel.
        """
        for plot_counter, channel in enumerate(self.plot_channel_order_list):
            self._plot_channel_time_signal(plot_counter, channel)

    def _plot_channel_time_signal(self, plot_counter: int, channel: str) -> None:
        """
        Helper function to plot the time signal for a specific channel.
        """
        if self.radar_param.gui.active_tx[0] and 'Channel 1' in self.processed_radar_data and plot_counter <= 3:
            if self.radar_param.gui.active_rx[plot_counter]:
                self._update_plot_line('Channel 1', plot_counter, channel)

        if self.radar_param.gui.active_tx[1] and 'Channel 2' in self.processed_radar_data and plot_counter > 3:
            if self.radar_param.gui.active_rx[plot_counter - 4]:
                self._update_plot_line('Channel 2', plot_counter - 4, channel)

        if self.radar_param.mon.sykno_product_name != 'SY60I11':
            data = self.processed_radar_data['Channel 3'][:]
            self.gui_controller.syra_plotter.time_signal.plotlines[f'{self.gui_controller.tab_name_time} mean'].setData(
                self.gui_controller.syra_plotter.time_axis, data)

    def _update_plot_line(self, channel: str, plot_counter: int, channel_name: str) -> None:
        """
        Helper function to update the plot line for a specific channel.
        """
        self.gui_controller.syra_plotter.time_signal.plotlines[f"{self.gui_controller.tab_name_time} {channel_name}"].setData(
            self.gui_controller.syra_plotter.time_axis,
            self.processed_radar_data[channel][:, plot_counter]
        )

    def set_spectrum(self, dummy: None) -> None:
        """
        Set the spectrum for the radar data plot.
        """
        if self.running and self.graph_update_flag:
            self._plot_spectrums()
        return dummy

    def _plot_spectrums(self) -> None:
        """
        Helper function to plot the spectrums for each channel.
        """
        for plot_counter, channel in enumerate(self.plot_channel_order_list):
            self._plot_channel_spectrum(plot_counter, channel)

    def _plot_channel_spectrum(self, plot_counter: int, channel: str) -> None:
        """
        Helper function to plot the spectrum for a specific channel.
        """
        data = None

        if self.radar_param.gui.active_tx[0] and 'Channel 1' in self.processed_radar_data and plot_counter <= 3:
            if self.radar_param.gui.active_rx[plot_counter]:
                data = self.processed_radar_data['Channel 1'][:, plot_counter]
                self._update_spectrum_plot_line(data, channel)

        if self.radar_param.gui.active_tx[1] and 'Channel 2' in self.processed_radar_data and plot_counter > 3:
            if self.radar_param.gui.active_rx[plot_counter - 4]:
                data = self.processed_radar_data['Channel 2'][:, plot_counter - 4]
                self._update_spectrum_plot_line(data, channel)

        if self.radar_param.mon.sykno_product_name != 'SY60I11':
            data = self.processed_radar_data['Channel 3'][:]
            self.gui_controller.syra_plotter.spectrum.plotlines['Spectrum mean'].setData(self.gui_controller.fft_axis, data)

    def _update_spectrum_plot_line(self, data: np.ndarray, channel_name: str) -> None:
        """
        Helper function to update the spectrum plot line for a specific channel.
        """
        self.gui_controller.syra_plotter.spectrum.plotlines[f"{self.gui_controller.tab_name_main_instance_window} {channel_name}"].setData(
            self.gui_controller.fft_axis, data)

    def set_spectrogram(self, dummy: None) -> None:
        """
        Set the spectrogram for the radar data plot.
        """
        if self.running and self.graph_update_flag:
            self._plot_spectrograms()
        return dummy

    def _plot_spectrograms(self) -> None:
        """
        Helper function to plot the spectrograms for each channel.
        """
        for plot_counter, channel in enumerate(self.plot_channel_order_list):
            if plot_counter <= 3:
                self._update_spectrogram_plot_line(f'{self.gui_controller.tab_name_main_instance_window} {channel}', 'Channel 1', plot_counter)
            elif plot_counter > 3 and plot_counter < 8:
                self._update_spectrogram_plot_line(f'{self.gui_controller.tab_name_main_instance_window} {channel}', 'Channel 1', plot_counter - 4)

    def _update_spectrogram_plot_line(self, channel_name: str=None, channel: str=None, plot_counter: int= None) -> None:
        """
        Helper function to update the spectrogram plot line for a specific channel.
        """
        self.gui_controller.syra_plotter.spectrogram.plotlines[f'{channel_name}'].setImage(
            np.transpose(np.flip(self.processed_radar_data[channel], axis=0), (1, 0, 2))[:, :, plot_counter],
            autoLevels=False
        )

    def set_range_doppler(self, dummy: None) -> None:
        """
        Set the range-Doppler plot for the radar data.
        """
        if self.running and self.graph_update_flag:
            self._plot_range_dopplers()
        return dummy

    def _plot_range_dopplers(self) -> None:
        """
        Helper function to plot the range-Doppler for each channel.
        """
        for plot_counter, channel in enumerate(self.plot_channel_order_list):
            if plot_counter <= 3:
                self._update_range_doppler_plot_line(f'{self.gui_controller.tab_name_main_instance_window} {channel}', 'Channel 1', plot_counter)
            elif plot_counter > 3 and plot_counter < 8:
                self._update_range_doppler_plot_line(f'{self.gui_controller.tab_name_main_instance_window} {channel}', 'Channel 1', plot_counter - 4)

    def _update_range_doppler_plot_line(self, channel_name: str, channel: str, plot_counter: int) -> None:
        # radar_data_buffer = self.range_doppler_buffer

        # new_radar_data = self.processed_radar_data[channel]

        # radar_data_buffer = np.roll(radar_data_buffer, shift=-1, axis=-1)

        # radar_data_buffer[:, :, :, -1] = new_radar_data
        # self.range_doppler_buffer = radar_data_buffer
        # mean_range_doppler_map = np.mean(radar_data_buffer, axis=-1)
        
        mean_range_doppler_map = self.processed_radar_data[channel]
        self.gui_controller.syra_plotter.range_doppler.plotlines[f'{channel_name}'].setImage(
            np.transpose(np.flip(mean_range_doppler_map, axis=0), (0, 1, 2))[:, :, plot_counter],
            autoLevels=False
        )

    def set_range_azimtuh(self, dummy: None) -> None:
        """
        Set the range-azimuth plot for the radar data.
        """
        if self.running and self.graph_update_flag:
            self._update_range_azimuth_plot_line('Channel 1')
        return dummy

    def set_waterfall_azimtuh(self, dummy: None) -> None:
        """
        Set the waterfall-azimuth plot for the radar data.
        """
        if self.running and self.graph_update_flag:
            self._update_range_azimuth_plot_line('Channel 1')
            self._update_spectrogram_plot_line('Waterfall Spectrogram RX1_TX1', 'Channel 2', 0)
        return dummy

    def set_range_doppler_azimtuh(self, dummy: None) -> None:
        """
        Set the range-Doppler-azimuth plot for the radar data.
        """
        if self.running and self.graph_update_flag:
            self._update_range_azimuth_plot_line('Channel 1')
            self._update_range_doppler_plot_line('Range Doppler RX1_TX1', 'Channel 2', 0)
        return dummy

    def set_waterfall_range_doppler_azimtuh(self, dummy: None) -> None:
        """
        Set the waterfall-range-Doppler-azimuth plot for the radar data.
        """
        if self.running and self.graph_update_flag:
            self._update_range_azimuth_plot_line('Channel 1')
            self._update_range_doppler_plot_line('Range Doppler RX1_TX2', 'Channel 2', 0)
            self._update_spectrogram_plot_line('Waterfall Spectrogram RX1_TX2', 'Channel 3', 0)
        return dummy

    def _update_range_azimuth_plot_line(self, channel: str) -> None:
        """
        Helper function to update the range-azimuth plot line for a specific channel.
        """
        self.gui_controller.syra_plotter.range_azimuth.plotlines[self.gui_controller.tab_name_main_instance_window].setImage(
            self.processed_radar_data[channel], autoLevels=False
        )

    def closeEvent(self, event=None) -> None:
        """
        Handle the close event for the application.
        """
        self.app_exit()
        logger.debug("Close Sykno MiRa Evaluation GUI")

    def keyPressEvent(self, event) -> None:
        """
        Handle key press events for the application.
        """
        if event.key() == QtCore.Qt.Key_Escape:  # Close app with ESC
            self.closeEvent()

    def app_exit(self) -> None:
        """
        Exit the application and clean up resources.
        """
        try:
            if self.syra_processor:
                self.syra_processor.process_stop_event.set()
        except Exception:
            pass

        self.running = False
        self.graph_update_flag = False

        if self.syra_controller and self.syra_processor:
            self.syra_processor.stop_processes()

        try:
            if self.syra_controller and self.syra_controller.syra_device:
                self.syra_controller.syra_device.syra_bridge.deinit_stm_usb_device()
        except Exception:
            pass

        self.syra_controller = None
        self.close()


if __name__ == "__main__":
    syra_gui = SYRA_MAIN_GUI()
    syra_gui.syra_gui_main()
