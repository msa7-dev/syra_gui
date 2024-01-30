import __init__
import numpy as np
import configparser

from mira.bgt.mira_device_bgt import MIRA_DEVICE
from mira.proc.mira_data_extraction import MIRA6024_DATA_EXTRACTOR
from mira.proc.mira_data_processing import MIRA6024_DATA_PROCESSOR
from mira.proc.mira_data_simulation import MIRA6024_DATA_SIMULATOR
from mira.com.mira_tcp_client import MIRA_TCP_CLIENT
from mira.bgt.mira_device_bgt import MIRA6024_RADAR_PARAMETER
# ==============================================================================
# Class Name: MIRA6024_CTRL_GUI
# ==============================================================================
class MIRA6024_CTRL_GUI:
    def __init__(self, radar_param):
        self.config = configparser.ConfigParser()
        self.config.read(__init__.MIRA_SYS_CONFIG_PATH)
        self.radar_param: MIRA6024_RADAR_PARAMETER = radar_param
        
        if self.radar_param.rply.replay_flag == False: # MIRA USB Operation Mode
            # if self.radar_param.remt.client_flag == True or \
                # self.radar_param.remt.remote_flag == False:
            self.mira_device = MIRA_DEVICE(self.radar_param)
            
            if self.mira_device.init == False:
                return
            else:
                self.init_CTRL()
                self.data_extrator = MIRA6024_DATA_EXTRACTOR(self.mira_device)

            # 
        # elif radar_param.rply.replay_flag == True: # MIRA Replay Operation Mode
            # self.data_simulator = MIRA6024_DATA_SIMULATOR(self.radar_param)
            # self.mira_device = self.data_simulator.mira_device
            # if self.mira_device is None:
                # return 
        self.data_processor = MIRA6024_DATA_PROCESSOR(self.radar_param)
        
# TODO remove and clean up
    def init_CTRL(self) -> None:
        self.set_header_prefix()
        self.get_frame()
        self.set_n_fifo_overhead()
        
    def set_n_fifo_overhead(self) -> None:
        USB_SPI_BRIDGE_DATA_ALLOCATION = int(self.config.get("MIRA_USB_SPI_BRIDGE", 
                                                             "USB_SPI_BRIDGE_DATA_ALLOCATION")) 
        self.radar_param.sys.n_fifo_overhead = np.uint8(USB_SPI_BRIDGE_DATA_ALLOCATION/(self.radar_param.sys.n_samples_per_chirp[0]*3*(4/2))) # TODO 4
        self.mira_device.mira_bridge.spi_set_n_fifo_overhead(self.radar_param.sys.n_fifo_overhead)
      
    def set_spi_high_speed(self) -> None:
        self.mira_device._sfctl_reg.MISO_HS_RD = 1
        
    def set_header_prefix(self) -> None:
        self.mira_device._sfctl_reg.PREFIX_EN = 1

    def get_frame(self) -> None:
        self.radar_param.sys.num_chirps_frame = self.radar_param.sys.shape_repetition * self.radar_param.sys.shape_set_repetition
        print(self.radar_param.sys.num_chirps_frame)
        self.radar_param.sys.frame_samples = self.radar_param.sys.frame_chirps * self.radar_param.sys.n_samples_per_chirp[0] 
        self.radar_param.sys.fifo_per_chirp = self.radar_param.sys.n_samples_per_chirp[0] / 1024
        
        USB_SPI_BRIDGE_DATA_ALLOCATION = int(self.config.get("MIRA_USB_SPI_BRIDGE", 
                                                             "USB_SPI_BRIDGE_DATA_ALLOCATION")) 
        self.radar_param.sys.n_chirps_per_data_read = USB_SPI_BRIDGE_DATA_ALLOCATION / (3 * sum(self.radar_param.sys.n_samples_per_chirp))
        self.radar_param.sys.n_readings_per_frame = sum(self.radar_param.sys.shape_repetition) / self.radar_param.sys.n_chirps_per_data_read

    def set_sadc_temp(self) -> None:
        self.mira_device._sadc_ctrl_reg.SADC_CHSEL = 0
        self.mira_device._sadc_ctrl_reg.SADC_START = 1
        
    def set_hp_filter(self, 
                      vga_gain: int=0,
                      hp_gain: int=0,
                      hp_fc: int=0,
                      rx_ch: int=-1,
                      shape_id: int=-1) -> None:
        
        for ch_shift in range(4):
            if rx_ch == ch_shift + 1 or rx_ch == -1:
                for shape_shift in range(4):
                    if shape_id == shape_shift + 1 or shape_id == -1:
                        reg = getattr(self.mira_device, f"_csu{shape_shift + 1}_2_reg")
                        reg.HP_GAIN = hp_gain << ch_shift
                        reg.VGA_GAIN1 = vga_gain
                        reg.HPF_SEL1 = hp_fc


# ==============================================================================
# Class Name: MIRA6024_CTRL_CLI
# ==============================================================================
class MIRA6024_CTRL_CLI:
    def __init__(self, radar_param):
        self.config = configparser.ConfigParser()
        self.config.read(__init__.MIRA_SYS_CONFIG_PATH)
        
        if radar_param.meas.measurement_flag == False: # MIRA USB Operation Mode
            self.mira_device = MIRA_DEVICE()
            self.data_extrator = MIRA6024_DATA_EXTRACTOR(self.mira_device)
        elif radar_param.meas.measurement_flag == True: # MIRA Replay Operation Mode
            self.data_simulator = MIRA6024_DATA_SIMULATOR(radar_param)

        if self.mira_device.mira_bridge.device is None:
            return
        
        self.data_processor = MIRA6024_DATA_PROCESSOR(self.mira_device.radar_param)

class MIRA6024_CTRL_REMT:
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
                    self.data_extrator = MIRA6024_DATA_EXTRACTOR(self.mira_device)
        self.mira_tcp_client = MIRA_TCP_CLIENT()
        pass
 