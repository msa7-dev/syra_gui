import __init__ 
import sys
import time
import numpy as np
import configparser
from loguru import logger
from typing import List, Optional
from PyQt5 import uic, QtCore, QtWidgets

from mira.ctrl.mira_ctrl import MIRA_CTRL_CLI
from mira.rsys.mira_radar_sys import MIRA_RADAR_PARAMETER
from mira.ctrl.mira_multiprocessing import MIRA_MULTIPROCESSOR
from mira.gui.mira_gui_ctrl import MIRA_GUI_CTRL, init_gui_window, init_gui_qtwidgets

# ==============================================================================
# Class Name: MiRa60241AMainWindow
# ==============================================================================
class MIRA_MAIN_CLI():
    def __init__(self) -> None:
        self.config = configparser.ConfigParser()
        self.config.read(__init__.MIRA_SYS_CONFIG_PATH)
        
        logger.debug(f"Start Sykno {str(self.config.get('DEFAULT', 'SYKNO_PRODUCT'))} Evaluation CLI")

        self.timestamp = ''
        self.mira_controller = None
                
        self.mira_processor = MIRA_MULTIPROCESSOR(self.mira_controller)

    def mira_cli_main(self):
        self.mira_controller = MIRA_CTRL_CLI(self.radar_param)

        if self.mira_controller is None:
            self.mira_controller = None
            return
            
        self.prev_time = 0
        self.start_time = time.time() 
        
        self.radar_param = self.mira_controller.radar_param
        self.gui_controller.insert_radar_params(self.radar_param)
        
        
        # self.init_processes_threads()
        
        self.mira_controller.mira_device.init_mira_frame_generation()
        

    def update_print(self):
        if self.running and not self.stop_event.is_set():
            if not self.update_gui_info_queue.empty():
                update_info_dict = self.update_gui_info_queue.get(block=False)
                self.bgt_temperature_sadc = update_info_dict['temperature']
                self.current_frame_counter = update_info_dict['frame_counter']
            else:
                return
            self.update_temperature()
            self.update_duration_time()
                
    def update_duration_time(self) -> None:
        self.current_time = time.time()
        self.elapsed_time = self.current_time - self.start_time
        # Check if more than 1 second has passed since the last update
        if self.current_time - self.prev_time >= 1:
            # Format the elapsed time into hh:mm:ss
            hours, remainder = divmod(self.elapsed_time, 3600)
            minutes, seconds = divmod(remainder, 60)
            self.radar_param.mon.duration_time = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
            self.label_duration_time.setText(self.radar_param.mon.duration_time)
            self.prev_time = self.current_time  # Update prev_time to the current time

    def update_temperature(self) -> None:
        if self.bgt_temperature_sadc >= -99: # Random number
            self.label_temperature.setText(f'{self.bgt_temperature_sadc} °C')
            self.set_header_queue_event.set()
        else:
            self.set_header_queue_event.set()
