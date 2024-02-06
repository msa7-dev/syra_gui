import __init__ 
import sys
import time
import numpy as np
import configparser
# import setproctitle
from loguru import logger
from threading import Thread
from typing import List, Optional
from PyQt5 import uic, QtCore, QtWidgets
from mira.ctrl.mira_ctrl import MIRA6024_CTRL_GUI
from mira.com.mira_tcp_client import MIRA_TCP_CLIENT
from mira.rsys.mira_radar_sys import MIRA6024_RADAR_PARAMETER
from mira.ctrl.mira_multiprocessing import MIRA_MULTIPROCESSOR
from mira.gui.mira_gui_ctrl import MIRA6024_GUI_CTRL, init_gui_window, init_gui_qtwidgets

# ==============================================================================
# Class Name: MIRA_MAIN_GUI
# ==============================================================================
class MIRA_MAIN_GUI(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super(MIRA_MAIN_GUI, self).__init__()
        self.config = configparser.ConfigParser()
        self.config.read(__init__.MIRA_SYS_CONFIG_PATH)
        
        MIRA_UI_PYQT_FILE_PATH = self.config.get("MIRA_6024_EVAL_GUI",
                                                 "MIRA_UI_PYQT_FILE_PATH")

        # setproctitle.setproctitle('Sykno - MiRa Eval GUI - GUI Process')
        uic.loadUi(f"{MIRA_UI_PYQT_FILE_PATH}", self)

        logger.debug(f"Start Sykno {str(self.config.get('DEFAULT', 'SYKNO_PRODUCT'))} Evaluation GUI")

        self.running = False
        self.mira_processor = None
        self.mira_controller = None
        self.graph_update_flag = False
        
        self.ups = 2
        self.fps_timer = None
        self.connect_timer = None
        self.update_gui_timer = None
        
        self.prev_processed_radar_data_shape = {'Channel 1': (2,2,2),
                                                'Channel 2': (2,2,2)}
        self.processed_radar_data = {'Channel 1': np.zeros((1,1,1), dtype=np.float32),
                                     'Channel 2': np.zeros((1,1,1), dtype=np.float32)}
        
        self.plot_channel_order_list = ['RX1 TX1', 'RX2 TX1', 'RX3 TX1', 'RX4 TX1',
                                        'RX1 TX2', 'RX2 TX2', 'RX3 TX2', 'RX4 TX2']

    def set_updates_per_sec(self, timer: QtCore.QTimer, fps: int) -> None:
        timer.start(int(1000 / fps))  # Interval in milliseconds

    def init_gui_controller(self):
        self.radar_param = MIRA6024_RADAR_PARAMETER()
        self.gui_controller = MIRA6024_GUI_CTRL(self, self.radar_param)
        self.gui_controller.update_radar_params()
        self.start_auto_connect()
            
    def mira_gui_main() -> None:
        init_gui_qtwidgets()
        app = QtWidgets.QApplication(sys.argv)
        main = MIRA_MAIN_GUI()
        app = init_gui_window(app, main)
        main.show()
        main.init_gui_controller()
        app.exec_()
        
    # Start and stop processing threads
    def start_stop(self) -> None:
        if not self.running:
            self.button_startstop.clicked.disconnect()
            self.button_startstop.clicked.connect(self.start_stop)
            
            if self.mira_controller is None:
                self.mira_controller = MIRA6024_CTRL_GUI(self.radar_param)

            if self.mira_controller.mira_device.mira_bridge.device is None:
                self.mira_controller = None
                self.button_startstop.setText("Start")
                return
            else:
                self.button_startstop.setText("Stop")
            
            self.prev_time = 0
            self.start_time = time.time() 
            self.mira_processor = MIRA_MULTIPROCESSOR(self.mira_controller)
            
            self.gui_controller.get_axis_x()
            self.gui_controller.update_bgt_hp_filter()
            self.gui_controller.update_radar_params()
            self.mira_controller.mira_device.activate_rf_test_mode()
            self.mira_controller.mira_device.init_mira_frame_generation()
            self.mira_processor.start_processes()

            self.running = True
            self.graph_update_flag = False

        elif self.running:
            
            self.button_startstop.clicked.disconnect()
            self.button_startstop.setText("Start")

            self.mira_processor.stop_event.set()
            self.running = False
            self.graph_update_flag = False
            self.mira_processor.stop_processes()

            self.mira_controller.mira_device.mira_bridge.deinit_stm_usb_device()
            self.mira_controller = None
            
            self.button_startstop.clicked.connect(self.start_stop)
            self.start_auto_connect()
        else:
            return
        
    def start_auto_connect(self) -> None:
        if self.radar_param.gui.auto_connect_device:
            self.connect_timer = QtCore.QTimer()
            self.connect_timer.timeout.connect(self.auto_connect_device)
            self.set_updates_per_sec(self.connect_timer, 1)
            
    def disconnect_device(self) -> None:
        self.mira_controller.mira_device.mira_bridge.deinit_stm_usb_device()
        self.mira_controller = None
            
    def auto_connect_device(self) -> None:
        if self.mira_controller is None:
            self.mira_controller = MIRA6024_CTRL_GUI(self.radar_param)
        if self.mira_controller.mira_device.mira_bridge.device is None:
            self.mira_controller = None
            return
        self.connect_timer.stop()
        self.connect_timer.timeout.disconnect()
        self.gui_controller.set_device_connected()
        self.gui_controller.update_radar_params()
        
    def start_gui_event_timer(self) -> None:
        if self.fps_timer is not None:
            self.fps_timer.stop()
            self.fps_timer.timeout.disconnect()
        if self.update_gui_timer is not None:
            self.update_gui_timer.stop()
            self.update_gui_timer.timeout.disconnect()

        self.update_gui_timer = QtCore.QTimer()
        self.update_gui_timer.timeout.connect(self.update_gui)
        self.set_updates_per_sec(self.update_gui_timer, self.ups)
        
        if not self.radar_param.meas.record_headless:
            self.fps_timer = QtCore.QTimer()
            self.fps_timer.timeout.connect(self.update_plot)
            self.set_updates_per_sec(self.fps_timer, self.radar_param.gui.fps)
        else: 
            self.fps_timer = None
        
    def connect_tcp_client(self) -> None:
        if not self.tcp_remote_control_checkBox.isChecked():
            return
        
        self.tcp_client = MIRA_TCP_CLIENT(self.radar_param.remt.client_ip_port[0],
                                          self.radar_param.remt.client_ip_port[1],
                                          self.radar_param.remt.client_ssh_name,
                                          self.radar_param.remt.client_ssh_pwd)
        try:
            server_thread = Thread(target=self.tcp_client.start)
            server_thread.start()
            input("Press Enter to stop the server...")
            self.tcp_client.close()
            server_thread.join()
        except KeyboardInterrupt:
            self.tcp_client.close()

    def update_gui(self) -> None:
        if self.running:
            if not self.mira_processor.update_gui_info_queue.empty():
                update_info_dict = self.mira_processor.update_gui_info_queue.get(block=False)
                self.radar_param.mon.temperature = float(update_info_dict['temperature'])
                self.radar_param.mon.duration_frame_counter = str(update_info_dict['frame_cnt'])
                self.radar_param.mon.datarate = float(update_info_dict['datarate'])
            else:
                return
            self.updata_datarate()
            self.update_frame_cnt()
            self.update_temperature()
            self.update_duration_time()
        else:
            return
            
    def update_frame_cnt(self) -> None:
        self.label_frame_counter.setText(self.radar_param.mon.duration_frame_counter)
    
    def update_duration_time(self) -> None:
        self.current_time = time.time()
        self.elapsed_time = self.current_time - self.start_time
        # Check if more than 1 second has passed since the last update
        if self.current_time - self.prev_time >= 1:
            # Format the elapsed time into hh:mm:ss
            hours, remainder = divmod(self.elapsed_time, 3600)
            minutes, seconds = divmod(remainder, 60)
            self.radar_param.mon.duration_time = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
            self.label_duration_time.setText(f"{self.radar_param.mon.duration_time}")
            self.prev_time = self.current_time  # Update prev_time to the current time

    def update_temperature(self) -> None:
        if self.radar_param.mon.temperature >= -99: # Random out of range number
            self.label_temperature.setText(f'{round(self.radar_param.mon.temperature, 2)} °C')
            self.mira_processor.set_header_queue_event.set()
        else:
            self.mira_processor.set_header_queue_event.set()
    
    def updata_datarate(self) -> None:
        self.label_datarate.setText(f'{round(self.radar_param.mon.datarate*1e-6, 2)} Mbps')

    def update_plot(self) -> None:
        if self.running and \
           not self.graph_update_flag and \
           not self.mira_processor.stop_event.is_set():
            if self.mira_processor.radar_plot_map_queue.empty():
                return None
            if not self.mira_processor.process_param_queue.empty():
                while not self.mira_processor.radar_plot_map_queue.empty():
                    self.mira_processor.radar_plot_map_queue.get_nowait()
                return None

            processed_data_dict = self.mira_processor.radar_plot_map_queue.get(block=False)

            self.process_info = processed_data_dict['Process Info']
            self.processed_radar_data = processed_data_dict['Processed Data']

            if self.process_info['Process Name'] != \
                self.gui_controller.tab_name_main_instance_window:
                return None
            self.gui_controller.update_pipeline.call_plot_pipeline(
                f"{self.process_info['Process Name']}", None)
        else:
            self.graph_update_flag = False

    def check_plot_shape(self, dummy: None) -> None:
        if self.processed_radar_data['Channel 1'].shape != \
           self.prev_processed_radar_data_shape['Channel 1'] or \
           self.processed_radar_data['Channel 2'].shape != \
           self.prev_processed_radar_data_shape['Channel 2']:
            self.prev_processed_radar_data_shape['Channel 1'] = \
                self.processed_radar_data['Channel 1'].shape
            self.prev_processed_radar_data_shape['Channel 2'] = \
                self.processed_radar_data['Channel 2'].shape
            self.gui_controller.get_axis_x()
            return
        self.graph_update_flag = True
        return dummy

    def plot_ready(self, dummy: None) -> None:
        self.graph_update_flag = False
        return dummy

    def set_time_signal(self, dummy: None) -> None:
        if self.running and self.graph_update_flag:
            for plot_counter, channel in enumerate(self.plot_channel_order_list):
                if self.radar_param.gui.active_tx[0] \
                    and 'Channel 1' in self.processed_radar_data \
                        and plot_counter <= 3:
                    if  self.radar_param.gui.active_rx[plot_counter]:
                        self.gui_controller.mira_plotter.time_signal.plotlines[
                            f"{self.gui_controller.tab_name_time} {channel}"].setData(
                            self.gui_controller.mira_plotter.time_axis,
                            self.processed_radar_data['Channel 1'][:, plot_counter])

                if self.radar_param.gui.active_tx[1] \
                    and 'Channel 2' in self.processed_radar_data \
                    and plot_counter > 3:
                    if  self.radar_param.gui.active_rx[plot_counter-4]:
                        self.gui_controller.mira_plotter.time_signal.plotlines[
                            f"{self.gui_controller.tab_name_time} {channel}"].setData(
                            self.gui_controller.mira_plotter.time_axis,
                            self.processed_radar_data['Channel 2'][:, plot_counter-4])
        return dummy
    
    def set_spectrum(self, dummy: None) -> None:
        if self.running and self.graph_update_flag:
            for plot_counter, channel in enumerate(self.plot_channel_order_list):
                if self.radar_param.gui.active_tx[0] \
                   and 'Channel 1' in self.processed_radar_data \
                   and plot_counter <= 3:
                    if  self.radar_param.gui.active_rx[plot_counter]:
                        self.gui_controller.mira_plotter.spectrum.plotlines[
                            f"{self.gui_controller.tab_name_main_instance_window} {channel}"].setData(
                            self.gui_controller.fft_axis, 
                            self.processed_radar_data['Channel 1'][:, plot_counter])

                if self.radar_param.gui.active_tx[1] \
                   and 'Channel 2' in self.processed_radar_data \
                   and plot_counter > 3:
                    if  self.radar_param.gui.active_rx[plot_counter-4]:
                        self.gui_controller.mira_plotter.spectrum.plotlines[
                            f"{self.gui_controller.tab_name_main_instance_window} {channel}"].setData(
                            self.gui_controller.fft_axis, 
                            self.processed_radar_data['Channel 2'][:, plot_counter-4])
            return dummy
            
    def set_spectrogram(self, dummy: None) -> None:
        if self.running and self.graph_update_flag:
            for plot_counter, channel in enumerate(self.plot_channel_order_list):
                if plot_counter <= 3:
                    self.gui_controller.mira_plotter.spectrogram.plotlines[
                    f'{self.gui_controller.tab_name_main_instance_window} {channel}'].setImage(
                    np.transpose(np.flip(self.processed_radar_data['Channel 1'], axis=0), 
                                 (1, 0, 2))[:, :, plot_counter], autoLevels=False)
                
                if plot_counter > 3 and plot_counter < 8:
                  self.gui_controller.mira_plotter.spectrogram.plotlines[
                      f'{self.gui_controller.tab_name_main_instance_window} {channel}'].setImage(
                      np.transpose(np.flip(self.processed_radar_data['Channel 1'], axis=0), 
                                   (1, 0, 2))[:, :, plot_counter-4], autoLevels=False)
        return dummy
        
    def set_range_doppler(self, dummy: None) -> None:
        if self.running and self.graph_update_flag:
            for plot_counter, channel in enumerate(self.plot_channel_order_list):
                if plot_counter <= 3:
                    self.gui_controller.mira_plotter.range_doppler.plotlines[
                        f'{self.gui_controller.tab_name_main_instance_window} {channel}'].setImage(
                        np.transpose(np.flip(self.processed_radar_data['Channel 1'], axis=0),
                                     (0, 1, 2))[:, :, plot_counter], autoLevels=False)
                
                if plot_counter > 3 and plot_counter < 8:
                    self.gui_controller.mira_plotter.range_doppler.plotlines[
                        f'{self.gui_controller.tab_name_main_instance_window} {channel}'].setImage(
                        np.transpose(np.flip(self.processed_radar_data['Channel 1'], axis=0),
                                     (0, 1, 2))[:, :, plot_counter-4], autoLevels=False)
        return dummy
        
    def set_range_azimtuh(self, dummy: None) -> None:
        if self.running == True and self.graph_update_flag:
            self.gui_controller.mira_plotter.range_azimuth.plotlines[
                self.gui_controller.tab_name_main_instance_window].setImage(
                np.abs(self.processed_radar_data['Channel 1']), autoLevels=True)
        return dummy
        
    def set_waterfall_azimtuh(self, dummy: None) -> None:
        if self.running == True and self.graph_update_flag:
            self.gui_controller.mira_plotter.range_azimuth.plotlines[
                self.gui_controller.tab_name_main_instance_window].setImage(
                self.processed_radar_data['Channel 1'], autoLevels=True)
            self.gui_controller.mira_plotter.spectrogram.plotlines[
                'Waterfall Spectrogram RX1_TX1'].setImage(
                np.transpose(np.flip(self.processed_radar_data['Channel 2'], axis=0),
                             (1,0,2))[:,:,0], autoLevels=False)
        return dummy
        
    def set_range_doppler_azimtuh(self, dummy: None) -> None:
        if self.running == True and self.graph_update_flag:
            self.gui_controller.mira_plotter.range_azimuth.plotlines[
                self.gui_controller.tab_name_main_instance_window].setImage(
                self.processed_radar_data['Channel 1'], autoLevels=True)
            
            self.gui_controller.mira_plotter.range_doppler.plotlines[
                'Range Doppler RX1_TX1'].setImage(
                np.transpose(np.flip(self.processed_radar_data['Channel 2'],
                                     axis=0), (0,1,2))[:,:,0], autoLevels=False)
        return dummy

    def closeEvent(self, event=None):
        self.app_exit()
        logger.debug(f"Close Sykno {str(self.config.get('DEFAULT', 'SYKNO_PRODUCT'))} Evaluation GUI")
    
        # Hotkeys for closing the window (ESC)
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:  # close app with ESC
            self.closeEvent()

    def app_exit(self):
        try:
            self.mira_processor.stop_event.set()
        except:
            pass
        self.running = False
        self.graph_update_flag = False
        
        if self.mira_controller is not None and \
           self.mira_processor is not None:
            self.mira_processor.stop_processes()

        try:
            self.mira_controller.mira_device.mira_bridge.deinit_stm_usb_device()
        except:
            pass
        
        self.mira_controller = None

        self.close()
