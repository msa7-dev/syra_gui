import __init__
import configparser
# from radar_eval.com.mira_tcp_client import MIRA_TCP_CLIENT
from radar_eval.radar_sensor.MiRa6024_sensor_device import MIRA_DEVICE
from radar_eval.radar_sensor.MiRa6024_sensor_device import MIRA_RADAR_PARAMETER
from radar_eval.measurement.save_measurement_file import MIRA_SAVE_MEAS
from radar_eval.processing.radar_data_extraction import MIRA_DATA_EXTRACTOR
from radar_eval.processing.radar_data_processing import MIRA_DATA_PROCESSOR
from radar_eval.processing.radar_data_simulation import MIRA_DATA_REPLAYER

# ==============================================================================
# Class Name: MIRA_CTRL_GUI
# ==============================================================================
class MIRA_CTRL_GUI:
    def __init__(self, radar_param: MIRA_RADAR_PARAMETER) -> None:
        self.config = configparser.ConfigParser()
        self.config.read(__init__.MIRA_SYS_CONFIG_PATH)
        self.radar_param = radar_param
        self.mira_device = None
        
        if self.radar_param.rply.replay_flag == False: # MIRA USB Operation Mode
            self.mira_device = MIRA_DEVICE(self.radar_param)
            if self.mira_device.init == False:
                self.mira_device = None

    def reinit_controller(self, radar_param: MIRA_RADAR_PARAMETER) -> None:
        self.radar_param = radar_param
        if self.radar_param.rply.replay_flag == False:
            self.mira_device.radar_param = radar_param
            self.data_extrator = MIRA_DATA_EXTRACTOR(self.mira_device)
        else:
            self.data_replayer = MIRA_DATA_REPLAYER()
        
        self.data_processor = MIRA_DATA_PROCESSOR(radar_param)
        if self.radar_param.meas.measurement_flag and self.mira_device:
            self.save_meas = MIRA_SAVE_MEAS(self.mira_device)

# ==============================================================================
# Class Name: MIRA_CTRL_CLI
# ==============================================================================
class MIRA_CTRL_CLI:
    def __init__(self, radar_param):
        self.config = configparser.ConfigParser()
        self.config.read(__init__.MIRA_SYS_CONFIG_PATH)
        
        if radar_param.rply.replay_flag == False: # MIRA USB Operation Mode
            self.mira_device = MIRA_DEVICE(radar_param)
            self.data_extrator = MIRA_DATA_EXTRACTOR(self.mira_device)
        else: # MIRA Replay Operation Mode
            self.data_replayer = MIRA_DATA_REPLAYER()
            self.mira_device = None  # No device needed for replay mode

        self.data_processor = MIRA_DATA_PROCESSOR(radar_param)

# ==============================================================================
# Class Name: MIRA_CTRL_REMT
# ==============================================================================
class MIRA_CTRL_REMT:
    def __init__(self, radar_param):
        self.config = configparser.ConfigParser()
        self.config.read(__init__.MIRA_SYS_CONFIG_PATH)
        
        if radar_param.rply.replay_flag == False: # MIRA USB Operation Mode
            if radar_param.remt.client_flag == True or \
               radar_param.remt.remote_flag == False:
                self.mira_device = MIRA_DEVICE(radar_param)
                if self.mira_device.mira_bridge.device is None:
                    return
                else:
                    self.data_extrator = MIRA_DATA_EXTRACTOR(self.mira_device)
        else: # MIRA Replay Operation Mode
            self.data_replayer = MIRA_DATA_REPLAYER()
            self.mira_device = None  # No device needed for replay mode

        # self.mira_tcp_client = MIRA_TCP_CLIENT()
