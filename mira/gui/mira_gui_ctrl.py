import __init__
import json
import configparser
import pyqtgraph as pg
from pathlib import Path
from loguru import logger
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPalette, QColor

from mira.gui.mira_browser import MIRA_BROWSER
from mira.gui.mira_plot_gui import MIRA_PLOTTER
from mira.rsys.mira_radar_sys import MIRA_RADAR_PARAMETER
from mira.gui.mira_gui_cfg import MIRA_WIDGET_VALUES, MIRA_FUNC_PIPELINE

# ==============================================================================
# Class Name: MIRA_GUI_CTRL
# ==============================================================================
class MIRA_GUI_CTRL():
    def __init__(self, qt_self, radar_param: MIRA_RADAR_PARAMETER) -> None:
        self.config = configparser.ConfigParser()
        self.config.read(__init__.MIRA_SYS_CONFIG_PATH)

        self.qt_self = qt_self
        self.radar_param: MIRA_RADAR_PARAMETER = radar_param
        self.prev_select_axis_x = ''
        self.widget_values = MIRA_WIDGET_VALUES()
        self.bgt_reg_browser = MIRA_BROWSER(self.qt_self, "bgt_reg_browser")
        self.meas_in_path_browser = MIRA_BROWSER(self.qt_self, "mira_meas_in_browser")
        self.meas_out_path_browser = MIRA_BROWSER(self.qt_self, "mira_meas_out_browser")
        self.mira_plotter = MIRA_PLOTTER(self.qt_self)
        self.update_pipeline = MIRA_FUNC_PIPELINE(self.qt_self)
        self.init_gui_widgets()
        
    def init_gui_widgets(self):
        self.identify_tab()
        self.rst_value_labels()
        self.init_value_check_box()
        self.init_connect_check_box()
        self.init_values_combo_box()
        self.init_connect_buttons()
        self.init_connect_tab()
        self.init_connect_combo_box()
        self.get_dsp_hp_parameters()
        self.get_window_func()
        self.get_padding_length()
        self.get_spectrum_rx_tx()
        self.get_min_max_dbfs()
        self.get_measurement_duration()
        self.get_recording_n_frames()
        self.get_waterfall_time()
        self.get_hp_rx()
        self.get_bgt_hp_fc()
        self.get_bgt_hp_gain()
        self.get_bgt_vga_gain()
        self.get_gui_fps()
        self.handle_usb_auto_connect_state()
        self.set_mira_session_label()
        self.set_mira_project()
        
    def update_radar_params(self) -> None:
        self.set_value_labels()
        self.update_processing_parameters()
        
    def init_connect_buttons(self):
        
        self.qt_self.button_startstop.clicked.connect(self.qt_self.start_stop)
        self.qt_self.browse_register_path_button.clicked.connect(self.bgt_reg_browser.open_path_browser)
        self.qt_self.browse_meas_in_path_button.clicked.connect(self.meas_in_path_browser.open_path_browser)
        self.qt_self.browse_meas_out_path_button.clicked.connect(self.meas_out_path_browser.open_path_browser)
        self.qt_self.mira_project_button.clicked.connect(self.set_mira_project)
        self.qt_self.browse_meas_data_label_button.clicked.connect(self.set_mira_session_label)
        self.qt_self.load_default_tcp_settings_button.clicked.connect(self.set_remote_tcp_default_settings)
        self.qt_self.remote_tcp_connect_button.clicked.connect(self.start_tcp_connection)
        self.qt_self.usb_device_connect_button.clicked.connect(self.qt_self.auto_connect_device)

    def init_values_combo_box(self):
        self.qt_self.combo_box_select_axis_x.addItems(self.widget_values.axis_unit_select_list)
        self.qt_self.combo_box_set_max_axis_x.addItems(self.widget_values.axis_range_select_list)
        self.qt_self.combo_box_window_func.addItems(self.widget_values.window_func_list)
        self.qt_self.combo_box_padding_len.addItems(self.widget_values.padding_len_list)
        self.qt_self.combo_box_bgt_vga_gain.addItems(self.widget_values.vga_gain_list)
        self.qt_self.combo_box_bgt_hp_fc.addItems(self.widget_values.bgt_hp_fc_list)
        self.qt_self.combo_box_bgt_hp_gain.addItems(self.widget_values.bgt_hp_gain_list)
        self.qt_self.combo_box_dsp_hp_filter_order.addItems(self.widget_values.dsp_hp_filter_order_list)
        self.qt_self.combo_box_dsp_hp_filter_type.addItems(self.widget_values.dsp_hp_filter_type_list)
        self.qt_self.combo_box_dsp_hp_filter_cutoff.addItems(self.widget_values.dsp_hp_filter_cutoff_list)
        self.qt_self.combo_box_measurement_duration.addItems(self.widget_values.measurement_duration_list)
        self.qt_self.combo_box_recording_n_frames.addItems(self.widget_values.recodring_n_frames_list)
        self.qt_self.combo_box_set_min_dbfs.addItems(self.widget_values.plot_select_mv_min_raw_data_list)
        self.qt_self.combo_box_set_max_dbfs.addItems(self.widget_values.plot_select_mv_min_raw_data_list)
        self.qt_self.combo_box_if_test_ton.addItems(self.widget_values.if_test_ton_list)
        self.qt_self.combo_box_waterfall_time.addItems(self.widget_values.waterfall_spectrogram_time_list)
        self.qt_self.combo_box_error_correction_files.addItems(self.widget_values.antenna_specific_error_correction_files_list)
        self.qt_self.combo_box_gui_fps.addItems(self.widget_values.gui_fps_list)
        
    def init_connect_combo_box(self):
        self.qt_self.combo_box_bgt_vga_gain.currentTextChanged.connect(self.get_bgt_vga_gain)
        self.qt_self.combo_box_bgt_hp_gain.currentTextChanged.connect(self.get_bgt_hp_gain)
        self.qt_self.combo_box_bgt_hp_fc.currentTextChanged.connect(self.get_bgt_hp_fc)
        self.qt_self.combo_box_dsp_hp_filter_order.currentTextChanged.connect(self.get_dsp_hp_parameters)
        self.qt_self.combo_box_dsp_hp_filter_type.currentTextChanged.connect(self.get_dsp_hp_parameters)
        self.qt_self.combo_box_dsp_hp_filter_cutoff.currentTextChanged.connect(self.get_dsp_hp_parameters)
        self.qt_self.combo_box_select_axis_x.currentTextChanged.connect(self.get_axis_x)
        self.qt_self.combo_box_set_max_axis_x.currentTextChanged.connect(self.get_max_axis_x)
        self.qt_self.combo_box_window_func.currentTextChanged.connect(self.get_window_func)
        self.qt_self.combo_box_padding_len.currentTextChanged.connect(self.get_padding_length)
        self.qt_self.combo_box_measurement_duration.currentTextChanged.connect(self.get_measurement_duration)
        self.qt_self.combo_box_recording_n_frames.currentTextChanged.connect(self.get_recording_n_frames)
        self.qt_self.combo_box_set_min_dbfs.currentTextChanged.connect(self.get_min_max_dbfs)
        self.qt_self.combo_box_set_max_dbfs.currentTextChanged.connect(self.get_min_max_dbfs)
        self.qt_self.combo_box_waterfall_time.currentTextChanged.connect(self.get_waterfall_time)
        self.qt_self.combo_box_if_test_ton.currentTextChanged.connect(self.get_rf_test_mode)
        self.qt_self.combo_box_gui_fps.currentTextChanged.connect(self.get_gui_fps)
        
    def init_connect_tab(self):
        self.qt_self.tab_plots.currentChanged.connect(self.identify_tab)
        self.qt_self.tab_time.currentChanged.connect(self.identify_tab)
        self.qt_self.tab_spectrogram.currentChanged.connect(self.identify_tab)
        self.qt_self.tab_range_doppler.currentChanged.connect(self.identify_tab)
        

    def set_value_labels(self):
        self.qt_self.label_duration_time.setText(f'{self.radar_param.mon.duration_time}')
        self.qt_self.label_temperature.setText(f'{round(float(self.radar_param.mon.temperature), 2)} °C')
        self.qt_self.label_datarate.setText(f'{round(float(self.radar_param.mon.datarate)*1e-6, 2)}')
        self.qt_self.label_frame_counter.setText(f'{int(self.radar_param.mon.duration_frame_counter)}')
        self.qt_self.label_shape_repetition.setText(f'{int(self.radar_param.sys.shape_set_repetition)}')
        self.qt_self.label_rx_tx_mode.setText(f'{int(self.radar_param.sys.rx_active_antennas[0])} / ' +
                                              f'{int(sum(self.radar_param.sys.tx_active_antennas))}')
        self.qt_self.label_tx_power.setText(f'{int(self.radar_param.sys.tx_power[0][0])} / {int(self.radar_param.sys.tx_power[1][1])} dBm')
        self.qt_self.label_sampling_frequency.setText(f'{round(float(self.radar_param.sys.sampling_frequency*1e-6), 5)} MHz')
        self.qt_self.label_chrip_sample.setText(str(int(self.radar_param.sys.n_samples_per_chirp[0])))
        self.qt_self.label_frequency.setText(f'{round(float(self.radar_param.sys.start_frequency[0] * 1e-9), 2)} - '+
                                             f'{round(float(self.radar_param.sys.end_frequency[0] * 1e-9), 2)} GHz')
        self.qt_self.label_ramp_time.setText(f'{round(float(self.radar_param.sys.ramp_time[0] * 1e6), 2)} µs')
        self.qt_self.label_bandwidth.setText(f'{round(float(self.radar_param.sys.ramp_bandwidth[0] * 1e-9), 2)} GHz')
        self.qt_self.label_ramp_slope.setText(f'{round(float(self.radar_param.sys.ramp_slope[0] * 1e-12), 2)} MHz/µs')
        self.qt_self.label_chirp_time.setText(f'{round(float(self.radar_param.sys.chirp_time[0]), 2)} ms')
        self.qt_self.label_frame_duration.setText(f'{round(float(self.radar_param.sys.frame_duration)*1e3, 2)} ms')
        self.qt_self.label_frames_per_second.setText(f'{round(float(self.radar_param.sys.frames_per_second), 2)} fps')
        
        # Range Labels
        self.qt_self.label_range_resolution.setText(f'{round(float(self.radar_param.sys.resolution_range*1e3), 2)} mm')
        self.qt_self.label_min_range.setText(f'{round(float(self.radar_param.sys.min_range), 2)} m')
        self.qt_self.label_max_range.setText(f'{round(float(self.radar_param.sys.max_range), 2)} m')
        
        # Velocity Labels
        self.qt_self.label_velocity_resolution.setText(f' {self.radar_param.sys.resolution_velocity[0]}')
        self.qt_self.label_min_velocity.setText(f'{round(float(-self.radar_param.sys.max_velocity[0]), 2)} m/s')
        self.qt_self.label_max_velocity.setText(f'{round(float(self.radar_param.sys.max_velocity[0]), 2)} m/s')
        self.qt_self.sensor_id_plainTextEdit.setPlainText(f'{self.radar_param.mon.chip_id}')
        # self.qt_self.sensor_id_plainTextEdit.setDisabled(True)
        
    
    def rst_value_labels(self):
        self.qt_self.label_duration_time.setText(f'1')
        self.qt_self.label_temperature.setText(f'')
        self.qt_self.label_datarate.setText(f'')
        self.qt_self.label_frame_counter.setText(f'')
        self.qt_self.label_shape_repetition.setText(f'')
        self.qt_self.label_rx_tx_mode.setText(f'')
        self.qt_self.label_tx_power.setText(f'')
        self.qt_self.label_tx2_power.setText(f'')
        self.qt_self.label_sampling_frequency.setText(f'')
        self.qt_self.label_chrip_sample.setText(f'')
        self.qt_self.label_frequency.setText(f'')
        self.qt_self.label_bandwidth.setText(f'')
        self.qt_self.label_ramp_time.setText(f'')
        self.qt_self.label_ramp_slope.setText(f'')
        self.qt_self.label_chirp_time.setText(f'')
        self.qt_self.label_frame_duration.setText(f'')
        self.qt_self.label_frames_per_second.setText(f'')
        self.qt_self.label_range_resolution.setText(f'')
        self.qt_self.label_min_range.setText(f'')
        self.qt_self.label_max_range.setText(f'')
        
        self.qt_self.label_velocity_resolution.setText(f'')
        self.qt_self.label_max_velocity.setText(f'')
        self.qt_self.label_min_velocity.setText(f'')
        self.qt_self.sensor_id_plainTextEdit.setPlainText(f'')

    def init_value_check_box(self):
        self.qt_self.check_box_replay.setChecked(False)
        self.qt_self.check_box_record.setChecked(False)
        
        self.qt_self.usb_connection_checkBox.setChecked(True)
        self.qt_self.usb_auto_connect_checkBox.setChecked(True)
        self.qt_self.usb_device_connect_button.setDisabled(True)
        self.qt_self.tcp_remote_control_checkBox.setChecked(False)
        self.qt_self.tcp_remote_control_checkBox.setDisabled(True)
        self.qt_self.load_default_tcp_settings_button.setDisabled(True)
        self.qt_self.remote_tcp_connect_button.setDisabled(True)
        
        self.qt_self.browse_register_path_button.setDisabled(True)
        self.qt_self.browse_meas_out_path_button.setDisabled(True)
        self.qt_self.browse_meas_data_label_button.setDisabled(True)
        self.qt_self.combo_box_measurement_duration.setDisabled(True)
        self.qt_self.combo_box_recording_n_frames.setDisabled(True)
        self.qt_self.combo_box_repeat_recording_n.setDisabled(True)
        self.qt_self.headless_recording_check_box.setDisabled(True)

        self.qt_self.browse_meas_in_path_button.setDisabled(True)

        self.qt_self.check_box_hp_rx1.setChecked(True)
        self.qt_self.check_box_hp_rx2.setChecked(True)
        self.qt_self.check_box_hp_rx3.setChecked(True)
        self.qt_self.check_box_hp_rx4.setChecked(True)
        
        self.qt_self.check_box_spectrum_tx1.setChecked(True)
        self.qt_self.check_box_spectrum_tx2.setChecked(True)
        
        self.qt_self.check_box_spectrum_rx1.setChecked(True)
        self.qt_self.check_box_spectrum_rx2.setChecked(True)
        self.qt_self.check_box_spectrum_rx3.setChecked(True)
        self.qt_self.check_box_spectrum_rx4.setChecked(True)
        
        self.qt_self.check_box_rf_test_en.setChecked(False)
        self.qt_self.check_box_rf_test_en_rx1.setChecked(False)
        self.qt_self.check_box_rf_test_en_rx2.setChecked(False)
        self.qt_self.check_box_rf_test_en_rx3.setChecked(False)
        self.qt_self.check_box_rf_test_en_rx4.setChecked(False)

    def handle_replay_state(self) -> None:
        if self.qt_self.check_box_replay.isChecked():
            self.qt_self.check_box_record.setChecked(False)
            self.qt_self.check_box_record.setDisabled(True)
            self.qt_self.browse_meas_in_path_button.setDisabled(False)

            self.radar_param.meas.measurement_flag = 0
            self.radar_param.rply.replay_flag = 1
        else:
            self.qt_self.check_box_record.setDisabled(False)
            self.qt_self.browse_meas_in_path_button.setDisabled(True)

    def handle_record_state(self) -> None:
        if self.qt_self.check_box_record.isChecked():
            self.qt_self.check_box_replay.setChecked(False)
            self.qt_self.check_box_replay.setDisabled(True)
            self.qt_self.browse_register_path_button.setDisabled(False)
            self.qt_self.browse_meas_out_path_button.setDisabled(False)
            self.qt_self.browse_meas_data_label_button.setDisabled(False)
            self.qt_self.combo_box_measurement_duration.setDisabled(False)
            self.qt_self.combo_box_recording_n_frames.setDisabled(False)
            self.qt_self.combo_box_repeat_recording_n.setDisabled(False)
            self.qt_self.headless_recording_check_box.setDisabled(False)
            self.radar_param.meas.measurement_flag = 1
            self.radar_param.rply.replay_flag = 0
            self.qt_self.disconnect_device()
            self.qt_self.start_auto_connect()
        else:
            self.qt_self.check_box_replay.setDisabled(False)
            self.qt_self.browse_register_path_button.setDisabled(True)
            self.qt_self.browse_meas_out_path_button.setDisabled(True)
            self.qt_self.browse_meas_data_label_button.setDisabled(True)
            self.qt_self.combo_box_measurement_duration.setDisabled(True)
            self.qt_self.combo_box_recording_n_frames.setDisabled(True)
            self.qt_self.combo_box_repeat_recording_n.setDisabled(True)
            self.qt_self.headless_recording_check_box.setDisabled(True)
    
    def handle_usb_auto_connect_state(self) -> None:
        if self.qt_self.usb_auto_connect_checkBox.isChecked():
            self.radar_param.gui.auto_connect_device = True
            self.qt_self.usb_device_connect_button.setDisabled(True)
        else:
            self.radar_param.gui.auto_connect_device = False
            self.qt_self.usb_device_connect_button.setDisabled(False)

    
    def handle_usb_connection_state(self) -> None:
        if self.qt_self.usb_connection_checkBox.isChecked():
            self.qt_self.usb_auto_connect_checkBox.setDisabled(False)
            self.qt_self.usb_device_connected_label.setDisabled(False)
            self.qt_self.tcp_remote_control_checkBox.setChecked(False)
            self.qt_self.usb_device_connect_button.setDisabled(False)
            self.qt_self.remote_tcp_connect_button.setDisabled(True)
            self.qt_self.tcp_remote_control_checkBox.setDisabled(True)
            self.qt_self.load_default_tcp_settings_button.setDisabled(True)
        else:
            self.qt_self.usb_auto_connect_checkBox.setChecked(False)
            self.qt_self.usb_auto_connect_checkBox.setDisabled(True)
            self.qt_self.usb_device_connect_button.setDisabled(True)
            self.qt_self.usb_device_connected_label.setDisabled(True)
            self.qt_self.remote_tcp_connect_button.setDisabled(True)
            self.qt_self.load_default_tcp_settings_button.setDisabled(True)
            self.qt_self.tcp_remote_control_checkBox.setDisabled(False)

    def handle_tcp_connection_state(self) -> None:
        if self.qt_self.tcp_remote_control_checkBox.isChecked():
            self.qt_self.usb_connection_checkBox.setChecked(False)
            self.qt_self.usb_connection_checkBox.setDisabled(True)
            self.qt_self.usb_auto_connect_checkBox.setChecked(False)
            self.qt_self.usb_auto_connect_checkBox.setDisabled(True)
            self.qt_self.usb_device_connect_button.setDisabled(True)
            self.qt_self.usb_device_connected_label.setDisabled(True)
            self.qt_self.load_default_tcp_settings_button.setDisabled(False)
            self.qt_self.remote_tcp_connect_button.setDisabled(False)
        else:
            self.qt_self.usb_connection_checkBox.setDisabled(False)
            self.qt_self.usb_auto_connect_checkBox.setDisabled(False)
            self.qt_self.usb_device_connect_button.setDisabled(False)
            self.qt_self.usb_device_connected_label.setDisabled(False)
            self.qt_self.load_default_tcp_settings_button.setDisabled(True)
            self.qt_self.remote_tcp_connect_button.setDisabled(True)
            
    def init_connect_check_box(self):
        self.qt_self.check_box_replay.stateChanged.connect(self.handle_replay_state)
        self.qt_self.check_box_record.stateChanged.connect(self.handle_record_state)
        
        self.qt_self.usb_auto_connect_checkBox.stateChanged.connect(self.handle_usb_auto_connect_state)
        self.qt_self.usb_connection_checkBox.stateChanged.connect(self.handle_usb_connection_state)
        self.qt_self.tcp_remote_control_checkBox.stateChanged.connect(self.handle_tcp_connection_state)
        self.qt_self.headless_recording_check_box.stateChanged.connect(self.get_headless_recording_state)
        self.qt_self.check_box_hp_rx1.stateChanged.connect(self.get_hp_rx)
        self.qt_self.check_box_hp_rx2.stateChanged.connect(self.get_hp_rx)
        self.qt_self.check_box_hp_rx3.stateChanged.connect(self.get_hp_rx)
        self.qt_self.check_box_hp_rx4.stateChanged.connect(self.get_hp_rx)
        
        self.qt_self.check_box_spectrum_tx1.stateChanged.connect(self.get_spectrum_rx_tx)
        self.qt_self.check_box_spectrum_tx2.stateChanged.connect(self.get_spectrum_rx_tx)
        
        self.qt_self.check_box_spectrum_rx1.stateChanged.connect(self.get_spectrum_rx_tx)
        self.qt_self.check_box_spectrum_rx2.stateChanged.connect(self.get_spectrum_rx_tx)
        self.qt_self.check_box_spectrum_rx3.stateChanged.connect(self.get_spectrum_rx_tx)
        self.qt_self.check_box_spectrum_rx4.stateChanged.connect(self.get_spectrum_rx_tx)
        
        self.qt_self.check_box_rf_test_en.stateChanged.connect(self.get_rf_test_mode)
        self.qt_self.check_box_rf_test_en_rx1.stateChanged.connect(self.get_rf_test_mode)
        self.qt_self.check_box_rf_test_en_rx2.stateChanged.connect(self.get_rf_test_mode)
        self.qt_self.check_box_rf_test_en_rx3.stateChanged.connect(self.get_rf_test_mode)
        self.qt_self.check_box_rf_test_en_rx4.stateChanged.connect(self.get_rf_test_mode)
            
    def set_device_connected(self) -> None:
        if self.radar_param.mon.chip_version_digital_id != '' and \
           self.radar_param.mon.chip_version_rf_id != '':
            self.qt_self.usb_device_connected_label.setText(f'{self.radar_param.mon.chip_version_digital_id}, {self.radar_param.mon.chip_version_rf_id}')
        else:
            self.qt_self.usb_device_connected_label.setText(f'No Device')
        
    def set_mira_project(self) -> None:
        mira_project = self.qt_self.mira_project_plainTextEdit.toPlainText()
        self.radar_param.gui.project_name = str(mira_project)
        self.bgt_reg_browser.reinit(mira_project)
        self.meas_in_path_browser.reinit(mira_project)
        self.meas_out_path_browser.reinit(mira_project)

    def set_mira_session_label(self) -> None:
        self.radar_param.meas.session_label = self.qt_self.session_label_plainTextEdit.toPlainText()
              
    def reinit_qt_widget_plots(self) -> None:
        self.clear_plots()
        plot_axis_max_value = self.radar_param.sys.plot_axis_max_value
        time_axis_max = (self.radar_param.sys.sampling_interval_time * \
                          self.radar_param.sys.n_samples_per_chirp[0])

        time_axis_max = self.radar_param.sys.ramp_time[0]
        
        if self.tab_name_main_instance_window == 'Time':
            self.mira_plotter.time_signal.set_plot_limits((0, time_axis_max*1e6), 
                                                          (self.radar_param.sys.plot_axis_min_dbfs, 
                                                           self.radar_param.sys.plot_axis_max_dbfs))
        
        if self.tab_name_main_instance_window == 'Spectrum':
            self.mira_plotter.spectrum.set_plot_limits((0, plot_axis_max_value), 
                                                       (self.radar_param.sys.plot_axis_min_dbfs, 
                                                        self.radar_param.sys.plot_axis_max_dbfs))
        
        if self.tab_name_main_instance_window == 'Waterfall Spectrogram' or \
           self.tab_name_main_instance_window == 'Waterfall Azimuth':
            self.mira_plotter.spectrogram.set_transform((0, plot_axis_max_value),
                                                        (-self.radar_param.sys.waterfall_spectrogram_time, 0),
                                                        (self.radar_param.sys.plot_axis_min_dbfs,
                                                         self.radar_param.sys.plot_axis_max_dbfs), 
                                                        self.qt_self.processed_radar_data['Channel 1'].shape \
                                                              if self.tab_name_main_instance_window == 'Waterfall Spectrogram' \
                                                              else self.qt_self.processed_radar_data['Channel 2'].shape)
        
        if self.tab_name_main_instance_window == 'Range Doppler' or \
           self.tab_name_main_instance_window == 'Range Doppler Azimuth':
            self.mira_plotter.range_doppler.set_transform((0, plot_axis_max_value),
                                                          (-self.radar_param.sys.max_velocity[0],
                                                           self.radar_param.sys.max_velocity[0]),
                                                          (self.radar_param.sys.plot_axis_min_dbfs,
                                                           self.radar_param.sys.plot_axis_max_dbfs),
                                                          self.qt_self.processed_radar_data['Channel 1'].shape \
                                                              if self.tab_name_main_instance_window == 'Range Doppler' \
                                                              else self.qt_self.processed_radar_data['Channel 2'].shape)
        
        if self.tab_name_main_instance_window == 'Range Azimuth' or \
           self.tab_name_main_instance_window == 'Waterfall Azimuth' or \
           self.tab_name_main_instance_window == 'Range Doppler Azimuth':  
            self.mira_plotter.range_azimuth.set_transform((0, plot_axis_max_value), 
                                                          (-90, 90),
                                                          (self.radar_param.sys.plot_axis_min_dbfs,
                                                           self.radar_param.sys.plot_axis_max_dbfs),
                                                          self.qt_self.processed_radar_data['Channel 1'].shape)
        
    def clear_plots(self) -> None:
        
        for _, plot in self.mira_plotter.time_signal.plotlines.items():
            plot.clear()
 
        for _, plot in self.mira_plotter.spectrum.plotlines.items():
            plot.clear()

        self.mira_plotter.spectrogram.clear_plot()
        self.mira_plotter.range_doppler.clear_plot()
        self.mira_plotter.range_azimuth.clear_plot()




    def build_process_param_queue(self) -> dict:
        process_param_queue_dict = {
            "main_tab_index": self.tab_name_main_instance_window,
            "time_tab_index": self.tab_name_time,
            "spectrogram_tab_index": self.tab_name_spectrogram,
            "range_doppler_tab_index": self.tab_name_range_doppler,
            "padding_length": self.radar_param.dsp.padding_len,
            "dsp_hp_filter_params": {
                "order": self.radar_param.dsp.hp_filter_order,
                "type": self.radar_param.dsp.hp_filter_type,
                "cutoff": self.radar_param.dsp.hp_filter_cutoff
            },
            "window_function": self.radar_param.dsp.window_func,
            "system_params": {
                'waterfall_spectrogram_time': self.radar_param.sys.waterfall_spectrogram_time,
                "plot_axis_max_value": self.radar_param.sys.plot_axis_max_value,
                "current_selected_axis_unit": self.radar_param.sys.curr_select_axis_unit,
            }
        }
        return process_param_queue_dict
    
    def identify_tab(self):
        self.tab_index_main_instance_window = self.qt_self.tab_plots.currentIndex()
        self.tab_index_time = self.qt_self.tab_time.currentIndex()
        self.tab_index_spectrogram = self.qt_self.tab_spectrogram.currentIndex()
        self.tab_index_range_doppler = self.qt_self.tab_range_doppler.currentIndex()
        
        self.tab_name_time = 'Raw Data'
        self.tab_name_spectrogram = 'TX1'
        self.tab_name_range_doppler = 'TX1'

        self.qt_self.combo_box_set_min_dbfs.clear()
        self.qt_self.combo_box_set_max_dbfs.clear()
        self.qt_self.combo_box_set_min_dbfs.clear()
        self.qt_self.combo_box_set_max_dbfs.clear()
        if self.tab_index_main_instance_window > 0:
            self.qt_self.combo_box_set_min_dbfs.addItems(self.widget_values.plot_select_dbfs_min_list)
            self.qt_self.combo_box_set_max_dbfs.addItems(self.widget_values.plot_select_dbfs_max_list)

        if self.tab_index_main_instance_window == 0:
            logger.debug(f"Switch to Tab: Time - Index: {self.tab_index_main_instance_window}")
            self.tab_name_main_instance_window = 'Time'
            if self.tab_index_time == 0:
                logger.debug("Switch to Tab: Time Raw Data")
                self.tab_name_time = 'Raw Data'
                self.qt_self.combo_box_set_min_dbfs.addItems(self.widget_values.plot_select_mv_min_raw_data_list)
                self.qt_self.combo_box_set_max_dbfs.addItems(self.widget_values.plot_select_mv_max_raw_data_list)
            elif self.tab_index_time == 1:
                logger.debug("Switch to Tab: Time DSP Output")
                self.tab_name_time = 'DSP Output'
                self.qt_self.combo_box_set_min_dbfs.addItems(self.widget_values.plot_select_mv_min_dsp_data_list)
                self.qt_self.combo_box_set_max_dbfs.addItems(self.widget_values.plot_select_mv_max_dsp_data_list)
                
        elif self.tab_index_main_instance_window == 1: 
            logger.debug(f"Switch to Tab: Spectrum")
            self.tab_name_main_instance_window = 'Spectrum'
            
        elif self.tab_index_main_instance_window == 2:
            logger.debug(f"Switch to Tab: Waterfall Spectrogram - Index: {self.tab_index_main_instance_window}")
            self.tab_name_main_instance_window = 'Waterfall Spectrogram'
            
            if self.tab_index_spectrogram == 0:
                logger.debug("Switch to Tab: Waterfall Spectrogram TX1")
                self.tab_name_spectrogram = 'TX1'
            elif self.tab_index_spectrogram == 1:
                logger.debug("Switch to Tab: Waterfall Spectrogram TX2")
                self.tab_name_spectrogram = 'TX2'
                
        elif self.tab_index_main_instance_window == 3:
            logger.debug(f"Switch to Tab: Range Doppler - Index: {self.tab_index_main_instance_window}")
            self.tab_name_main_instance_window = 'Range Doppler'
            
            if self.tab_index_range_doppler == 0:
                logger.debug("Switch to Tab: Range Doppler TX1")
                self.tab_name_range_doppler = 'TX1'
            elif self.tab_index_range_doppler == 1:
                logger.debug("Switch to Tab: Range Doppler TX2")
                self.tab_name_range_doppler = 'TX2'
            
        elif self.tab_index_main_instance_window == 4:
            logger.debug(f"Switch to Tab: Range Azimuth - Index: {self.tab_index_main_instance_window}")
            self.tab_name_main_instance_window = 'Range Azimuth'
            
        elif self.tab_index_main_instance_window == 5:
            logger.debug(f"Switch to Tab: Waterfall | Azimuth - Index: {self.tab_index_main_instance_window}")
            self.tab_name_main_instance_window = 'Waterfall Azimuth'
        
        elif self.tab_index_main_instance_window == 6:
            logger.debug(f"Switch to Tab: Range Doppler | Azimuth - Index: {self.tab_index_main_instance_window}")
            self.tab_name_main_instance_window = 'Range Doppler Azimuth'

        self.graph_update_flag = False
        self.update_processing_parameters()
        self.get_axis_x()
                
    def get_axis_x(self):
        self.radar_param.sys.curr_select_axis_unit = self.qt_self.combo_box_select_axis_x.currentText()
        self.curr_select_axis_x = self.qt_self.combo_box_select_axis_x.currentText()
        self.curr_set_max_axis_x = self.qt_self.combo_box_set_max_axis_x.currentText()

        if self.curr_select_axis_x == 'freq':
            if self.curr_select_axis_x != self.prev_select_axis_x:
                self.qt_self.combo_box_set_max_axis_x.clear()
                self.qt_self.combo_box_set_max_axis_x.addItems(self.widget_values.axis_freq_select_list)
                self.prev_select_axis_x = self.curr_select_axis_x
                self.radar_param.sys.curr_select_axis_unit = self.curr_select_axis_x
                
            self.fft_axis = self.mira_plotter.calc_plot_axis()['freq_axis']
            self.get_max_axis_x()
            
        elif self.curr_select_axis_x == 'range': 
            if self.curr_select_axis_x != self.prev_select_axis_x:
                self.qt_self.combo_box_set_max_axis_x.clear()
                self.qt_self.combo_box_set_max_axis_x.addItems(self.widget_values.axis_range_select_list)
                self.prev_select_axis_x = self.curr_select_axis_x
                self.radar_param.sys.curr_select_axis_unit = self.curr_select_axis_x
                
            self.fft_axis = self.mira_plotter.calc_plot_axis()['range_axis'] 
            self.get_max_axis_x()
            self.qt_self.plot_spectrum.setYRange(self.radar_param.sys.plot_axis_min_dbfs,
                                                 self.radar_param.sys.plot_axis_max_dbfs)
            
    def get_max_axis_x(self):
        self.curr_select_axis_x = self.qt_self.combo_box_select_axis_x.currentText()
        self.curr_set_max_axis_x = self.qt_self.combo_box_set_max_axis_x.currentText()

        if self.curr_select_axis_x == 'freq':
            if self.curr_set_max_axis_x == 'fmax':
                self.radar_param.sys.plot_axis_max_value = \
                    self.radar_param.sys.max_dsp_freq*1e-3
            elif self.curr_set_max_axis_x != '':
                self.radar_param.sys.plot_axis_max_value = \
                    float(self.curr_set_max_axis_x.split(' ')[0])
            else:
                return
        elif self.curr_select_axis_x == 'range':
            if self.curr_set_max_axis_x == 'rmax':
                self.radar_param.sys.plot_axis_max_value = \
                    self.radar_param.sys.max_range
            elif self.curr_set_max_axis_x != '':
                self.radar_param.sys.plot_axis_max_value = \
                    int(self.curr_set_max_axis_x.split(' ')[0])
            else:
                return
        self.reinit_qt_widget_plots()
        self.update_processing_parameters()

    def get_window_func(self):
        self.radar_param.dsp.window_func = self.qt_self.combo_box_window_func.currentText()
        self.update_processing_parameters()
        
    def get_padding_length(self):
        self.radar_param.dsp.padding_len = int(self.qt_self.combo_box_padding_len.currentText())
        self.get_axis_x()
        self.update_processing_parameters()
    
    def get_bgt_vga_gain(self):
        curr_bgt_vga_gain = self.qt_self.combo_box_bgt_vga_gain.currentText()        
        self.radar_param.sys.bgt_vga_gain[0] = int(int(curr_bgt_vga_gain.split(' ')[0])/5)
        self.update_bgt_hp_filter()

    def get_bgt_hp_gain(self):
        curr_bgt_hp_gain = self.qt_self.combo_box_bgt_hp_gain.currentText()
        bgt_hp_gain = int(curr_bgt_hp_gain.split(' ')[0])

        # encode register value - see REG CSX_2 
        # BGT Datasheet p. 51ff 
        if bgt_hp_gain == 18:
            self.radar_param.sys.bgt_hp_gain[0] = 1
        elif bgt_hp_gain == 30:
            self.radar_param.sys.bgt_hp_gain[0] = 0

        self.update_bgt_hp_filter()
        
    def get_bgt_hp_fc(self):
        curr_bgt_hp_fc = self.qt_self.combo_box_bgt_hp_fc.currentText()
        bgt_hp_fc = int(curr_bgt_hp_fc.split(' ')[0])

        # encode register value - see REG CSX_2 
        # BGT Datasheet p. 51ff
        if bgt_hp_fc == 20:
            self.radar_param.sys.bgt_hp_fc[0] = 0
        elif bgt_hp_fc == 45:
            self.radar_param.sys.bgt_hp_fc[0] = 1
        elif bgt_hp_fc == 70:
            self.radar_param.sys.bgt_hp_fc[0] = 2
        elif bgt_hp_fc == 80:
            self.radar_param.sys.bgt_hp_fc[0] = 3
        self.update_bgt_hp_filter()
        
    def get_measurement_duration(self) -> None:
        measurement_duration_text = self.qt_self.combo_box_measurement_duration.currentText()
        measurement_duration_unit = 's'
        if measurement_duration_text != 'Inf.':
            measurement_duration_value, measurement_duration_unit = measurement_duration_text.split(' ')
        else:
            measurement_duration_value = 0
        measurement_duration_value = int(measurement_duration_value)
        if measurement_duration_unit == 's':
            measurement_duration_value = measurement_duration_value
        elif measurement_duration_unit == 'min':
            measurement_duration_value *= 60
        elif measurement_duration_unit == 'h':
            measurement_duration_value *= 3600
        self.radar_param.meas.recording_duration = int(measurement_duration_value)
    
    def get_headless_recording_state(self) -> None:
        if self.qt_self.headless_recording_check_box.isChecked():
            self.radar_param.meas.record_headless = True
        else:
            self.radar_param.meas.record_headless = False
        self.get_gui_fps()
        print(self.radar_param.meas.record_headless)
            
    def get_recording_n_frames(self) -> None:
        recording_n_frames_text = self.qt_self.combo_box_measurement_duration.currentText()
        if recording_n_frames_text == 'Inf.':
            recording_n_frames_text = 0
        self.radar_param.meas.recording_n_frames = int(recording_n_frames_text)
    
    def get_min_max_dbfs(self) -> None:
        min_dbfs = self.qt_self.combo_box_set_min_dbfs.currentText()
        max_dbfs = self.qt_self.combo_box_set_max_dbfs.currentText()
    
        try:
            self.radar_param.sys.plot_axis_min_dbfs = int(min_dbfs.split(' ')[0]) if min_dbfs.strip() else 20 
            self.radar_param.sys.plot_axis_max_dbfs = int(max_dbfs.split(' ')[0]) if max_dbfs.strip() else -100  
        except ValueError as e:
            self.radar_param.sys.plot_axis_min_dbfs = 20
            self.radar_param.sys.plot_axis_max_dbfs = -100 
    
        self.get_axis_x()
        
    def get_waterfall_time(self) -> None:
        waterfall_time_text = self.qt_self.combo_box_waterfall_time.currentText()
        waterfall_time_value, waterfall_time_unit = waterfall_time_text.split(' ')
        if waterfall_time_unit == 'min':
            waterfall_time_value = int(waterfall_time_value) * 60
        else:
            waterfall_time_value = int(waterfall_time_value)
            
        self.radar_param.sys.waterfall_spectrogram_time = waterfall_time_value
        self.get_axis_x()

    def get_rf_test_mode(self) -> None:
        rf_test_ton_text = self.qt_self.combo_box_if_test_ton.currentText()
        rf_test_ton_value, rf_test_ton_unit = rf_test_ton_text.split(' ')
        self.radar_param.sys.rf_test_ton = int(rf_test_ton_value) * 1e3
        self.radar_param.sys.rf_test_mode_en = self.qt_self.check_box_rf_test_en.isChecked()
        self.radar_param.sys.rf_test_mode_en_channels[0] = self.qt_self.check_box_rf_test_en_rx1.isChecked()
        self.radar_param.sys.rf_test_mode_en_channels[1] = self.qt_self.check_box_rf_test_en_rx2.isChecked()
        self.radar_param.sys.rf_test_mode_en_channels[2] = self.qt_self.check_box_rf_test_en_rx3.isChecked()
        self.radar_param.sys.rf_test_mode_en_channels[3] = self.qt_self.check_box_rf_test_en_rx4.isChecked()

    def set_hp_filter(self, vga_gain: int, hp_gain: int, hp_fc: int, rx_select: int):
        if self.qt_self.running == True or self.qt_self.mira_controller is None:
            return
        self.qt_self.mira_controller.mira_device._csu1_2_reg.set_hp_filter(vga_gain, hp_gain, hp_fc, rx_select)
        self.qt_self.mira_controller.mira_device._csu2_2_reg.set_hp_filter(vga_gain, hp_gain, hp_fc, rx_select)
        self.qt_self.mira_controller.mira_device._csu3_2_reg.set_hp_filter(vga_gain, hp_gain, hp_fc, rx_select)
        self.qt_self.mira_controller.mira_device._csu4_2_reg.set_hp_filter(vga_gain, hp_gain, hp_fc, rx_select)
    
        self.qt_self.mira_controller.mira_device._csd1_2_reg.set_hp_filter(vga_gain, hp_gain, hp_fc, rx_select)
        self.qt_self.mira_controller.mira_device._csd2_2_reg.set_hp_filter(vga_gain, hp_gain, hp_fc, rx_select)
        self.qt_self.mira_controller.mira_device._csd3_2_reg.set_hp_filter(vga_gain, hp_gain, hp_fc, rx_select)
        self.qt_self.mira_controller.mira_device._csd4_2_reg.set_hp_filter(vga_gain, hp_gain, hp_fc, rx_select)

    def update_bgt_hp_filter(self):
        if self.radar_param.gui.hp_ch_rx[0]:
            self.set_hp_filter(self.radar_param.sys.bgt_vga_gain[0],
                               self.radar_param.sys.bgt_hp_gain[0],
                               self.radar_param.sys.bgt_hp_fc[0], 1)
        else:
            self.set_hp_filter(0, 0, 0, 1)
   
        if self.radar_param.gui.hp_ch_rx[1]:
            self.set_hp_filter(self.radar_param.sys.bgt_vga_gain[0],
                               self.radar_param.sys.bgt_hp_gain[0],
                               self.radar_param.sys.bgt_hp_fc[0], 2)
        else:
            self.set_hp_filter(0, 0, 0, 2)

        if self.radar_param.gui.hp_ch_rx[2]:
            self.set_hp_filter(self.radar_param.sys.bgt_vga_gain[0],
                               self.radar_param.sys.bgt_hp_gain[0],
                               self.radar_param.sys.bgt_hp_fc[0], 3)
        else:
            self.set_hp_filter(0, 0, 0, 3)

        if self.radar_param.gui.hp_ch_rx[3]:
            self.set_hp_filter(self.radar_param.sys.bgt_vga_gain[0],
                               self.radar_param.sys.bgt_hp_gain[0],
                               self.radar_param.sys.bgt_hp_fc[0], 4)
        else:            
            self.set_hp_filter(0, 0, 0, 4)
            
    def get_gui_fps(self) -> None:
        self.radar_param.gui.fps = int(self.qt_self.combo_box_gui_fps.currentText())
        self.qt_self.start_gui_event_timer()
        
    def start_tcp_connection(self) -> None:
        self.set_remote_tcp_settings()
        self.qt_self.connect_tcp_client()
        
    def set_remote_tcp_default_settings(self) -> None:
        MIRA_TCP_CLIENT_IP = self.config.get('MIRA_REMOTE_SETTINGS', 'MIRA_TCP_CLIENT_IP')
        MIRA_TCP_CLIENT_PORT = self.config.get('MIRA_REMOTE_SETTINGS', 'MIRA_TCP_CLIENT_PORT')
        MIRA_SSH_CLIENT_NAME = self.config.get('MIRA_REMOTE_SETTINGS', 'MIRA_SSH_CLIENT_NAME')
        MIRA_SSH_CLIENT_PWD = self.config.get('MIRA_REMOTE_SETTINGS', 'MIRA_SSH_CLIENT_PWD')
        self.radar_param.remt.client_ip_port = [MIRA_TCP_CLIENT_IP, MIRA_TCP_CLIENT_PORT]
        self.radar_param.remt.client_ssh_name = MIRA_SSH_CLIENT_NAME
        self.radar_param.remt.client_ssh_pwd = MIRA_SSH_CLIENT_PWD
        self.qt_self.client_ip_port_plainTextEdit.setPlainText(f'{MIRA_TCP_CLIENT_IP}:{MIRA_TCP_CLIENT_PORT}')
        self.qt_self.client_ssh_name_plainTextEdit.setPlainText(MIRA_SSH_CLIENT_NAME)
        self.qt_self.client_ssh_pwd_plainTextEdit.setPlainText(MIRA_SSH_CLIENT_PWD)
    
    def set_remote_tcp_settings(self) -> None:
        self.set_client_ip_port()
        self.set_client_ssh_name()
        self.set_client_ssh_pwd()
    
    def set_client_ip_port(self) -> None:
        client_ip_port = self.qt_self.client_ip_port_plainTextEdit.toPlainText()
        split_ip_port = str(client_ip_port).split(':')
        self.radar_param.remt.client_ip_port = split_ip_port
        
    def set_client_ssh_name(self) -> None:
        self.radar_param.remt.client_ssh_name = \
            self.qt_self.client_ssh_name_plainTextEdit.toPlainText()
    
    def set_client_ssh_pwd(self) -> None:
        self.radar_param.remt.client_ssh_pwd = \
            self.qt_self.client_ssh_pwd_plainTextEdit.toPlainText()
    
    def get_spectrum_rx_tx(self):
        self.radar_param.gui.active_tx[0] = self.qt_self.check_box_spectrum_tx1.isChecked()
        self.radar_param.gui.active_tx[1] = self.qt_self.check_box_spectrum_tx2.isChecked()
        self.radar_param.gui.active_rx[0] = self.qt_self.check_box_spectrum_rx1.isChecked()
        self.radar_param.gui.active_rx[1] = self.qt_self.check_box_spectrum_rx2.isChecked()
        self.radar_param.gui.active_rx[2] = self.qt_self.check_box_spectrum_rx3.isChecked()
        self.radar_param.gui.active_rx[3] = self.qt_self.check_box_spectrum_rx4.isChecked()
        self.reset_plotline()
        
    def reset_plotline(self):
        self.mira_plotter.time_signal.reset_plot_lines()
        self.mira_plotter.spectrum.reset_plot_lines()
    
    def get_hp_rx(self):
        self.radar_param.gui.hp_ch_rx[0] = self.qt_self.check_box_hp_rx1.isChecked()
        self.radar_param.gui.hp_ch_rx[1] = self.qt_self.check_box_hp_rx2.isChecked()
        self.radar_param.gui.hp_ch_rx[2] = self.qt_self.check_box_hp_rx3.isChecked()
        self.radar_param.gui.hp_ch_rx[3] = self.qt_self.check_box_hp_rx4.isChecked()
        self.update_bgt_hp_filter()
    
    
    def get_dsp_hp_parameters(self):
        self.radar_param.dsp.hp_filter_order = int(self.qt_self.combo_box_dsp_hp_filter_order.currentText())
        self.radar_param.dsp.hp_filter_type = self.qt_self.combo_box_dsp_hp_filter_type.currentText()
        dsp_hp_filter_cutoff = self.qt_self.combo_box_dsp_hp_filter_cutoff.currentText()
        self.radar_param.dsp.hp_filter_cutoff = int(dsp_hp_filter_cutoff.split(' ')[0])*1e3
        self.update_processing_parameters()
    
    def update_processing_parameters(self):
        if self.qt_self.mira_processor is not None:
            while not self.qt_self.mira_processor.process_param_queue.empty():
                self.qt_self.mira_processor.process_param_queue.get_nowait()
            self.qt_self.mira_processor.process_param_queue.put(self.build_process_param_queue())

def load_palette_from_json(file_path: Path):
    with open(file_path, 'r') as file:
        json_palette = json.load(file)
        return json_palette

def create_palette_from_json(json_palette) -> QPalette:
    palette = QPalette()

    color_mapping = {
        "Window": QPalette.Window,
        "WindowText": QPalette.WindowText,
        "Base": QPalette.Base,
        "AlternateBase": QPalette.AlternateBase,
        "ToolTipBase": QPalette.ToolTipBase,
        "ToolTipText": QPalette.ToolTipText,
        "Text": QPalette.Text,
        "Button": QPalette.Button,
        "ButtonText": QPalette.ButtonText,
        "BrightText": QPalette.BrightText,
        "Link": QPalette.Link,
        "Highlight": QPalette.Highlight,
        "HighlightedText": QPalette.HighlightedText,
        "DisabledWindowText": (QPalette.Disabled, QPalette.WindowText),
        "DisabledButtonText": (QPalette.Disabled, QPalette.ButtonText),
        "DisabledText": (QPalette.Disabled, QPalette.Text),
    }
    
    for key, value in color_mapping.items():
        color_hex = json_palette.get(key)
        if color_hex:
            color = QColor(color_hex)
            if isinstance(value, tuple):
                # Set color for disabled state
                palette.setColor(value[0], value[1], color)
            else:
                # Set color for normal state
                palette.setColor(value, color)

    return palette

def init_gui_qtwidgets() -> None:
    pg.setConfigOptions(useOpenGL=True, antialias=True)
    QtWidgets.QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)  # Enable high-DPI scaling
    QtWidgets.QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)  # Use high-DPI icons    
    QtWidgets.QApplication.setHighDpiScaleFactorRoundingPolicy(
        QtCore.Qt.HighDpiScaleFactorRoundingPolicy.PassThrough,)
    
def init_gui_window(app_instance, main_instance) -> QtWidgets.QApplication:
    config = configparser.ConfigParser()
    config.read(__init__.MIRA_SYS_CONFIG_PATH)
    
    app = app_instance
    screen = app.primaryScreen()
    rect = screen.geometry()
    width = rect.width()
    height = rect.height()

    print(width, height)
    if width >= 1400:
        font_offset = 0
    if width >= 2000:
        font_offset = 2
    # Create a temporary widget to get the current font settings
    temp_widget = QtWidgets.QLabel()
    current_font = temp_widget.font()
    
    # Check if the font size is set in points or pixels
    if current_font.pointSize() > 0:
        current_font_size = current_font.pointSize()
    else:
        current_font_size = current_font.pixelSize()
    
    # Adjust the font size by the offset
    new_font_size = current_font_size + font_offset
    
    # Apply the new font size globally
    app.setStyleSheet(f"QWidget {{ font-size: {new_font_size}pt; }}")

    MIRA_GUI_COLOR_PALETTE_PATH = config.get("MIRA_6024_EVAL_GUI", 
                                             "MIRA_GUI_COLOR_PALETTE_PATH")
    app.setStyle("Fusion")
    available_styles = QtWidgets.QStyleFactory.keys()
    json_palette = load_palette_from_json(Path(MIRA_GUI_COLOR_PALETTE_PATH))
    palette = create_palette_from_json(json_palette)
    app.setPalette(palette)
    
    MIRA_GUI_SCREEN_SIZE_MIN = config.get("MIRA_6024_EVAL_GUI", 
                                        "MIRA_GUI_SCREEN_SIZE_MIN")
    MIRA_GUI_SCREEN_SIZE_MIN = tuple(int(part.strip()) 
                                    for part in MIRA_GUI_SCREEN_SIZE_MIN.split(','))
    MIRA_GUI_FULL_SCREEN = str(config.get("MIRA_6024_EVAL_GUI", 
                                        "MIRA_GUI_FULL_SCREEN"))
    MIRA_GUI_START_MAXIMIZED = str(config.get("MIRA_6024_EVAL_GUI", 
                                            "MIRA_GUI_START_MAXIMIZED")) 
    
    main_instance.setMinimumSize(QtCore.QSize(*MIRA_GUI_SCREEN_SIZE_MIN))  # Minimum size
    main_instance.setMaximumSize(QSize(3840, 2160))  # Maximum size (4k resolution)
    # main_instance.setMaximumSize(QtCore.QSize(width, height))  
    if MIRA_GUI_FULL_SCREEN == 'True':
        main_instance.showFullScreen()
    elif MIRA_GUI_START_MAXIMIZED == 'True':
        main_instance.showMaximized()
    else:
        main_instance.showNormal()
    return app


