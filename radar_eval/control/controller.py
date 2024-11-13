import __init__
import configparser
from typing import Optional
from radar_eval.radar_sensor.MiRa6024_sensor_device import SYRA_DEVICE, SYRA_RADAR_PARAMETER
from radar_eval.measurement.save_measurement_file import SYRA_SAVE_MEAS
from radar_eval.processing.radar_data_extraction import SYRA_DATA_EXTRACTOR
from radar_eval.processing.radar_data_processing import SYRA_DATA_PROCESSOR
from radar_eval.processing.radar_data_simulation import SYRA_DATA_REPLAYER


# ==============================================================================
# Class Name: SYRA_CTRL_GUI
# ==============================================================================
class SYRA_CTRL_GUI:
    def __init__(self, radar_param: SYRA_RADAR_PARAMETER) -> None:
        """
        Initializes the SYRA_CTRL_GUI class with radar parameters and prepares
        the device, data extractor, and data processor based on the operation mode.
        """
        self.config: configparser.ConfigParser = self._load_config()
        self.radar_param: SYRA_RADAR_PARAMETER = radar_param
        self.syra_device: Optional[SYRA_DEVICE] = None
        self.data_extractor: Optional[SYRA_DATA_EXTRACTOR] = None
        self.data_replayer: Optional[SYRA_DATA_REPLAYER] = None
        self.data_processor: SYRA_DATA_PROCESSOR = SYRA_DATA_PROCESSOR(radar_param)
        self.save_meas: Optional[SYRA_SAVE_MEAS] = None

        self._initialize_device()

    def _load_config(self) -> configparser.ConfigParser:
        """
        Loads the configuration from the specified system path.

        Returns:
            configparser.ConfigParser: The loaded configuration parser object.
        """
        config = configparser.ConfigParser()
        config.read(__init__.SYRA_SYS_CONFIG_PATH)
        return config

    def _initialize_device(self, reinit: bool=False) -> None:
        """
        Initializes the radar device and associated data handlers based on the
        replay flag in the radar parameters.
        """
        if not self.radar_param.rply.replay_flag:
            if self.syra_device is None:  # SYRA USB Operation Mode
                self.syra_device = SYRA_DEVICE(self.radar_param)
            if not self.syra_device.init:
                self.syra_device = None
                return
            if self.syra_device.syra_bridge.used_usb_product_id == 'e404':
                return

            self.syra_device.radar_param = self.radar_param
            self.data_extractor = SYRA_DATA_EXTRACTOR(self.syra_device)
        else:  # SYRA Replay Operation Mode
            self.data_replayer = SYRA_DATA_REPLAYER()

        if self.radar_param.meas.measurement_flag and self.syra_device and not reinit:
            self.save_meas = SYRA_SAVE_MEAS(self.syra_device)

    def reinit_controller(self, radar_param: SYRA_RADAR_PARAMETER) -> None:
        """
        Reinitializes the controller with new radar parameters.

        Args:
            radar_param (SYRA_RADAR_PARAMETER): The new radar parameters.
        """
        self.radar_param = radar_param
        self._initialize_device(reinit=True)
        self.data_processor = SYRA_DATA_PROCESSOR(radar_param)


# ==============================================================================
# Class Name: SYRA_CTRL_CLI
# ==============================================================================
class SYRA_CTRL_CLI:
    def __init__(self, radar_param: SYRA_RADAR_PARAMETER) -> None:
        """
        Initializes the SYRA_CTRL_CLI class with radar parameters and prepares
        the device, data extractor, and data processor based on the operation mode.
        """
        self.config: configparser.ConfigParser = self._load_config()
        self.syra_device: Optional[SYRA_DEVICE] = None
        self.data_extractor: Optional[SYRA_DATA_EXTRACTOR] = None
        self.data_replayer: Optional[SYRA_DATA_REPLAYER] = None
        self.data_processor: SYRA_DATA_PROCESSOR = SYRA_DATA_PROCESSOR(radar_param)

        self._initialize_device(radar_param)

    def _load_config(self) -> configparser.ConfigParser:
        """
        Loads the configuration from the specified system path.

        Returns:
            configparser.ConfigParser: The loaded configuration parser object.
        """
        config = configparser.ConfigParser()
        config.read(__init__.SYRA_SYS_CONFIG_PATH)
        return config

    def _initialize_device(self, radar_param: SYRA_RADAR_PARAMETER) -> None:
        """
        Initializes the radar device and associated data handlers based on the
        replay flag in the radar parameters.

        Args:
            radar_param (SYRA_RADAR_PARAMETER): The radar parameters for the device.
        """
        if not radar_param.rply.replay_flag:  # SYRA USB Operation Mode
            self.syra_device = SYRA_DEVICE(radar_param)
            self.data_extractor = SYRA_DATA_EXTRACTOR(self.syra_device)
        else:  # SYRA Replay Operation Mode
            self.data_replayer = SYRA_DATA_REPLAYER()


# ==============================================================================
# Class Name: SYRA_CTRL_REMT
# ==============================================================================
class SYRA_CTRL_REMT:
    def __init__(self, radar_param: SYRA_RADAR_PARAMETER) -> None:
        """
        Initializes the SYRA_CTRL_REMT class with radar parameters and prepares
        the device, data extractor, and data processor based on the operation mode.
        """
        self.config: configparser.ConfigParser = self._load_config()
        self.syra_device: Optional[SYRA_DEVICE] = None
        self.data_extractor: Optional[SYRA_DATA_EXTRACTOR] = None
        self.data_replayer: Optional[SYRA_DATA_REPLAYER] = None
        self.data_processor: SYRA_DATA_PROCESSOR = SYRA_DATA_PROCESSOR(radar_param)

        self._initialize_device(radar_param)

    def _load_config(self) -> configparser.ConfigParser:
        """
        Loads the configuration from the specified system path.

        Returns:
            configparser.ConfigParser: The loaded configuration parser object.
        """
        config = configparser.ConfigParser()
        config.read(__init__.SYRA_SYS_CONFIG_PATH)
        return config

    def _initialize_device(self, radar_param: SYRA_RADAR_PARAMETER) -> None:
        """
        Initializes the radar device and associated data handlers based on the
        replay flag in the radar parameters.

        Args:
            radar_param (SYRA_RADAR_PARAMETER): The radar parameters for the device.
        """
        if not radar_param.rply.replay_flag:  # SYRA USB Operation Mode
            if radar_param.remt.client_flag or not radar_param.remt.remote_flag:
                self.syra_device = SYRA_DEVICE(radar_param)
                if self.syra_device.syra_bridge.device:
                    self.data_extractor = SYRA_DATA_EXTRACTOR(self.syra_device)
        else:  # SYRA Replay Operation Mode
            self.data_replayer = SYRA_DATA_REPLAYER()
