import __init__
import numpy as np
from loguru import logger
from scipy.constants import c
from mira.sens.mira_reg_cont_helper import *
import mira.sens.mira6024_reg_def as BGT_REG
import mira.sens.mira_reg_cont_bgt as MIRA6024_CONTENT
from mira.com.mira_usb_spi_bridge import MIRA_USB_SPI_BRIDGE
from mira.rsys.mira_radar_sys  import MIRA_RADAR_PARAMETER

class MIRA_DEVICE:
    def __init__(self, radar_param: MIRA_RADAR_PARAMETER):
        self.radar_param = radar_param
        clear_log_file()
        self.init = True
        self.mira_bridge = MIRA_USB_SPI_BRIDGE(self)

        if self.mira_bridge.device is None:
            self.init = False
            return 
        else:
            self.init_device_content()
                
        for attr in self.CONTENT:
            register_instance = self.CONTENT.get(f"{attr}", 0)
            set_bgt_dev_register(register_instance)
            register_instance.CONVERT
            
        self.mira_bridge.init_fifo_overhead()

        generate_register_to_txt(self, save_to_file=True)
        generate_register_to_readable_txt(self, save_to_file=True)
        for reg in self.pll_1_shape_regs:
            reg.CONVERT
        bgt_register_checker = check_sensor_register(self)
        logger.debug(f"Sensor register check: {'Pass' if bgt_register_checker else 'Fail'}")
        
        self.init_radar_system_parameters()
        if bgt_register_checker != True:
            self.init = False
            return 
            
    def init_device_content(self):
        self._main_reg = MIRA6024_CONTENT.BGT_MAIN(self)
        self._adc0_reg = MIRA6024_CONTENT.BGT_ADC0(self)
        self._chip_version_reg = MIRA6024_CONTENT.BGT_CHIP_VERSION(self)
        self._stat1_reg = MIRA6024_CONTENT.BGT_STAT1(self)
        self._pacr1_reg = MIRA6024_CONTENT.BGT_PACR1(self)
        self._pacr2_reg = MIRA6024_CONTENT.BGT_PACR2(self)
        self._sfctl_reg = MIRA6024_CONTENT.BGT_SFCTL(self)
        self._sadc_ctrl_reg = MIRA6024_CONTENT.BGT_SADC_CTRL(self)
        
        self._csi_0_reg  = MIRA6024_CONTENT.BGT_CSX_0(self, BGT_REG.CSX_0_REG.CSI_0_ADR)
        self._csds_0_reg = MIRA6024_CONTENT.BGT_CSX_0(self, BGT_REG.CSX_0_REG.CSDS_0_ADR)
        self._csu1_0_reg = MIRA6024_CONTENT.BGT_CSX_0(self, BGT_REG.CSX_0_REG.CSU1_0_ADR)
        self._csd1_0_reg = MIRA6024_CONTENT.BGT_CSX_0(self, BGT_REG.CSX_0_REG.CSD1_0_ADR)
        self._csu2_0_reg = MIRA6024_CONTENT.BGT_CSX_0(self, BGT_REG.CSX_0_REG.CSU2_0_ADR)
        self._csd2_0_reg = MIRA6024_CONTENT.BGT_CSX_0(self, BGT_REG.CSX_0_REG.CSD2_0_ADR)
        self._csu3_0_reg = MIRA6024_CONTENT.BGT_CSX_0(self, BGT_REG.CSX_0_REG.CSU3_0_ADR)
        self._csd3_0_reg = MIRA6024_CONTENT.BGT_CSX_0(self, BGT_REG.CSX_0_REG.CSD3_0_ADR)
        self._csu4_0_reg = MIRA6024_CONTENT.BGT_CSX_0(self, BGT_REG.CSX_0_REG.CSU4_0_ADR)
        self._csd4_0_reg = MIRA6024_CONTENT.BGT_CSX_0(self, BGT_REG.CSX_0_REG.CSD4_0_ADR)
        self.csu_0_regs = [self._csu1_0_reg, self._csu2_0_reg, self._csu3_0_reg, self._csu4_0_reg]
        self.csd_0_regs = [self._csd1_0_reg, self._csd2_0_reg, self._csd3_0_reg, self._csd4_0_reg]
        
        self._csi_1_reg  = MIRA6024_CONTENT.BGT_CSX_1(self, BGT_REG.CSX_1_REG.CSI_1_ADR)
        self._csds_1_reg = MIRA6024_CONTENT.BGT_CSX_1(self, BGT_REG.CSX_1_REG.CSDS_1_ADR)
        self._csu1_1_reg = MIRA6024_CONTENT.BGT_CSX_1(self, BGT_REG.CSX_1_REG.CSU1_1_ADR)
        self._csd1_1_reg = MIRA6024_CONTENT.BGT_CSX_1(self, BGT_REG.CSX_1_REG.CSD1_1_ADR)
        self._csu2_1_reg = MIRA6024_CONTENT.BGT_CSX_1(self, BGT_REG.CSX_1_REG.CSU2_1_ADR)
        self._csd2_1_reg = MIRA6024_CONTENT.BGT_CSX_1(self, BGT_REG.CSX_1_REG.CSD2_1_ADR)
        self._csu3_1_reg = MIRA6024_CONTENT.BGT_CSX_1(self, BGT_REG.CSX_1_REG.CSU3_1_ADR)
        self._csd3_1_reg = MIRA6024_CONTENT.BGT_CSX_1(self, BGT_REG.CSX_1_REG.CSD3_1_ADR)
        self._csu4_1_reg = MIRA6024_CONTENT.BGT_CSX_1(self, BGT_REG.CSX_1_REG.CSU4_1_ADR)
        self._csd4_1_reg = MIRA6024_CONTENT.BGT_CSX_1(self, BGT_REG.CSX_1_REG.CSD4_1_ADR)
        self.csu_1_regs = [self._csu1_1_reg, self._csu2_1_reg, self._csu3_1_reg, self._csu4_1_reg]
        self.csd_1_regs = [self._csd1_1_reg, self._csd2_1_reg, self._csd3_1_reg, self._csd4_1_reg]
        
        self._csi_2_reg  = MIRA6024_CONTENT.BGT_CSX_2(self, BGT_REG.CSX_2_REG.CSI_2_ADR)
        self._csds_2_reg = MIRA6024_CONTENT.BGT_CSX_2(self, BGT_REG.CSX_2_REG.CSDS_2_ADR)
        self._csu1_2_reg = MIRA6024_CONTENT.BGT_CSX_2(self, BGT_REG.CSX_2_REG.CSU1_2_ADR)
        self._csd1_2_reg = MIRA6024_CONTENT.BGT_CSX_2(self, BGT_REG.CSX_2_REG.CSD1_2_ADR)
        self._csu2_2_reg = MIRA6024_CONTENT.BGT_CSX_2(self, BGT_REG.CSX_2_REG.CSU2_2_ADR)
        self._csd2_2_reg = MIRA6024_CONTENT.BGT_CSX_2(self, BGT_REG.CSX_2_REG.CSD2_2_ADR)
        self._csu3_2_reg = MIRA6024_CONTENT.BGT_CSX_2(self, BGT_REG.CSX_2_REG.CSU3_2_ADR)
        self._csd3_2_reg = MIRA6024_CONTENT.BGT_CSX_2(self, BGT_REG.CSX_2_REG.CSD3_2_ADR)
        self._csu4_2_reg = MIRA6024_CONTENT.BGT_CSX_2(self, BGT_REG.CSX_2_REG.CSU4_2_ADR)
        self._csd4_2_reg = MIRA6024_CONTENT.BGT_CSX_2(self, BGT_REG.CSX_2_REG.CSD4_2_ADR)
        self.csu_2_regs = [self._csu1_2_reg, self._csu2_2_reg, self._csu3_2_reg, self._csu4_2_reg]
        self.csd_2_regs = [self._csd1_2_reg, self._csd2_2_reg, self._csd3_2_reg, self._csd4_2_reg]
        
        self._csci_reg  = MIRA6024_CONTENT.BGT_CSCX(self, BGT_REG.CSCX_REG.CSCI_ADR)
        self._cscds_reg = MIRA6024_CONTENT.BGT_CSCX(self, BGT_REG.CSCX_REG.CSCDS_ADR)
        self._csc1_reg  = MIRA6024_CONTENT.BGT_CSCX(self, BGT_REG.CSCX_REG.CSC1_ADR)
        self._csc2_reg  = MIRA6024_CONTENT.BGT_CSCX(self, BGT_REG.CSCX_REG.CSC2_ADR)
        self._csc3_reg  = MIRA6024_CONTENT.BGT_CSCX(self, BGT_REG.CSCX_REG.CSC3_ADR)
        self._csc4_reg  = MIRA6024_CONTENT.BGT_CSCX(self, BGT_REG.CSCX_REG.CSC4_ADR)
        self.csc_shape_regs = [self._csc1_reg, self._csc2_reg, self._csc3_reg, self._csc4_reg]
        
        self._ccr0_reg = MIRA6024_CONTENT.BGT_CCR0(self)
        self._ccr1_reg = MIRA6024_CONTENT.BGT_CCR1(self)
        self._ccr2_reg = MIRA6024_CONTENT.BGT_CCR2(self)
        self._ccr3_reg = MIRA6024_CONTENT.BGT_CCR3(self)
        self.ccr_shape_regs = [self._ccr0_reg, self._ccr1_reg, self._ccr2_reg, self._ccr3_reg]
        
        self._pll1_0 = MIRA6024_CONTENT.BGT_PLLX_0(self, BGT_REG.PLLX_0_REG.PLL1_0_ADR)
        self._pll2_0 = MIRA6024_CONTENT.BGT_PLLX_0(self, BGT_REG.PLLX_0_REG.PLL2_0_ADR)
        self._pll3_0 = MIRA6024_CONTENT.BGT_PLLX_0(self, BGT_REG.PLLX_0_REG.PLL3_0_ADR)
        self._pll4_0 = MIRA6024_CONTENT.BGT_PLLX_0(self, BGT_REG.PLLX_0_REG.PLL4_0_ADR)
        self.pll_0_shape_regs = [self._pll1_0, self._pll2_0, self._pll3_0, self._pll4_0]
        
        self._pll1_1 = MIRA6024_CONTENT.BGT_PLLX_1(self, BGT_REG.PLLX_1_REG.PLL1_1_ADR)
        self._pll2_1 = MIRA6024_CONTENT.BGT_PLLX_1(self, BGT_REG.PLLX_1_REG.PLL2_1_ADR)
        self._pll3_1 = MIRA6024_CONTENT.BGT_PLLX_1(self, BGT_REG.PLLX_1_REG.PLL3_1_ADR)
        self._pll4_1 = MIRA6024_CONTENT.BGT_PLLX_1(self, BGT_REG.PLLX_1_REG.PLL4_1_ADR)
        self.pll_1_shape_regs = [self._pll1_1, self._pll2_1, self._pll3_1, self._pll4_1]
        
        self._pll1_2 = MIRA6024_CONTENT.BGT_PLLX_2(self, BGT_REG.PLLX_2_REG.PLL1_2_ADR)
        self._pll2_2 = MIRA6024_CONTENT.BGT_PLLX_2(self, BGT_REG.PLLX_2_REG.PLL2_2_ADR)
        self._pll3_2 = MIRA6024_CONTENT.BGT_PLLX_2(self, BGT_REG.PLLX_2_REG.PLL3_2_ADR)
        self._pll4_2 = MIRA6024_CONTENT.BGT_PLLX_2(self, BGT_REG.PLLX_2_REG.PLL4_2_ADR)
        self.pll_2_shape_regs = [self._pll1_2, self._pll2_2, self._pll3_2, self._pll4_2]
        
        self._pll1_3 = MIRA6024_CONTENT.BGT_PLLX_3(self, BGT_REG.PLLX_3_REG.PLL1_3_ADR)
        self._pll2_3 = MIRA6024_CONTENT.BGT_PLLX_3(self, BGT_REG.PLLX_3_REG.PLL2_3_ADR)
        self._pll3_3 = MIRA6024_CONTENT.BGT_PLLX_3(self, BGT_REG.PLLX_3_REG.PLL3_3_ADR)
        self._pll4_3 = MIRA6024_CONTENT.BGT_PLLX_3(self, BGT_REG.PLLX_3_REG.PLL4_3_ADR)
        self.pll_3_shape_regs = [self._pll1_3, self._pll2_3, self._pll3_3, self._pll4_3]
        
        self._pll1_4 = MIRA6024_CONTENT.BGT_PLLX_4(self, BGT_REG.PLLX_4_REG.PLL1_4_ADR)
        self._pll2_4 = MIRA6024_CONTENT.BGT_PLLX_4(self, BGT_REG.PLLX_4_REG.PLL2_4_ADR)
        self._pll3_4 = MIRA6024_CONTENT.BGT_PLLX_4(self, BGT_REG.PLLX_4_REG.PLL3_4_ADR)
        self._pll4_4 = MIRA6024_CONTENT.BGT_PLLX_4(self, BGT_REG.PLLX_4_REG.PLL4_4_ADR)
        self.pll_4_shape_regs = [self._pll1_4, self._pll2_4, self._pll3_4, self._pll4_4]
        
        self._pll1_5 = MIRA6024_CONTENT.BGT_PLLX_5(self, BGT_REG.PLLX_5_REG.PLL1_5_ADR)
        self._pll2_5 = MIRA6024_CONTENT.BGT_PLLX_5(self, BGT_REG.PLLX_5_REG.PLL2_5_ADR)
        self._pll3_5 = MIRA6024_CONTENT.BGT_PLLX_5(self, BGT_REG.PLLX_5_REG.PLL3_5_ADR)
        self._pll4_5 = MIRA6024_CONTENT.BGT_PLLX_5(self, BGT_REG.PLLX_5_REG.PLL4_5_ADR)
        self.pll_5_shape_regs = [self._pll1_5, self._pll2_5, self._pll3_5, self._pll4_5]
        
        self._pll1_6 = MIRA6024_CONTENT.BGT_PLLX_6(self, BGT_REG.PLLX_6_REG.PLL1_6_ADR)
        self._pll2_6 = MIRA6024_CONTENT.BGT_PLLX_6(self, BGT_REG.PLLX_6_REG.PLL2_6_ADR)
        self._pll3_6 = MIRA6024_CONTENT.BGT_PLLX_6(self, BGT_REG.PLLX_6_REG.PLL3_6_ADR)
        self._pll4_6 = MIRA6024_CONTENT.BGT_PLLX_6(self, BGT_REG.PLLX_6_REG.PLL4_6_ADR)
        self.pll_6_shape_regs = [self._pll1_6, self._pll2_6, self._pll3_6, self._pll4_6]
        
        self._pll1_7 = MIRA6024_CONTENT.BGT_PLLX_7(self, BGT_REG.PLLX_7_REG.PLL1_7_ADR)
        self._pll2_7 = MIRA6024_CONTENT.BGT_PLLX_7(self, BGT_REG.PLLX_7_REG.PLL2_7_ADR)
        self._pll3_7 = MIRA6024_CONTENT.BGT_PLLX_7(self, BGT_REG.PLLX_7_REG.PLL3_7_ADR)
        self._pll4_7 = MIRA6024_CONTENT.BGT_PLLX_7(self, BGT_REG.PLLX_7_REG.PLL4_7_ADR)
        self.pll_7_shape_regs = [self._pll1_7, self._pll2_7, self._pll3_7, self._pll4_7]
          
        self._rft0_reg = MIRA6024_CONTENT.BGT_RFT0(self)
        self._dft0_reg = MIRA6024_CONTENT.BGT_DFT0(self)
        self._dft1_reg = MIRA6024_CONTENT.BGT_DFT1(self)
        self._pll_dft0_reg = MIRA6024_CONTENT.BGT_PLL_DFT0(self)
        self._stat0_reg = MIRA6024_CONTENT.BGT_STAT0(self)
        self._sadc_result_reg = MIRA6024_CONTENT.BGT_SADC_RESULT(self)
        self._fstat_reg = MIRA6024_CONTENT.BGT_FSTAT(self)
        self._chip_id_1_reg = MIRA6024_CONTENT.BGT_CHIP_ID_1(self)
        self._chip_id_2_reg = MIRA6024_CONTENT.BGT_CHIP_ID_2(self)

    def set_spi_high_speed(self) -> None:
        self._sfctl_reg.MISO_HS_RD = 1
        
    def set_header_prefix(self) -> None:
        self._sfctl_reg.PREFIX_EN = 1
        
    def init_mira_frame_generation(self) -> None:
        self.mira_bridge.spi_bgt_finished_init()
        if self.radar_param.sys.rf_test_mode_en:
            self._main_reg.FSM_RESET = 1
            self._adc0_reg.TRIG_MADC = 1
        
        self._main_reg.FRAME_START = 1 # BGT start frame generation
        
    def activate_rf_test_mode(self) -> None:
        if self.radar_param.sys.rf_test_mode_en:
            self._rft0_reg.RFTSIGCLK_DIV = int((80*1e6)/self.radar_param.sys.rf_test_ton)
            self._rft0_reg.RFTSIGCLK_DIV_EN = 1
            self._sfctl_reg.LFSR_EN = 1
        else:
            return
        
        if self.radar_param.sys.rf_test_mode_en_channels[0]:
            self._rft0_reg.TEST_SIG_IF1_EN = 1
        if self.radar_param.sys.rf_test_mode_en_channels[1]:
            self._rft0_reg.TEST_SIG_IF2_EN = 1
        if self.radar_param.sys.rf_test_mode_en_channels[2]:
            self._rft0_reg.TEST_SIG_IF3_EN = 1
        if self.radar_param.sys.rf_test_mode_en_channels[3]:
            self._rft0_reg.TEST_SIG_IF4_EN = 1

    def init_radar_system_parameters(self) -> None:
        self.radar_param.sys.n_frames_range_doppler = 1
        self.radar_param.sys.sampling_interval_time = 1/self.radar_param.sys.sampling_frequency
        self.radar_param.sys.mid_frequency = self.radar_param.sys.start_frequency \
                                             + (self.radar_param.sys.ramp_bandwidth / 2)
        self.radar_param.sys.lambda_freq = c / self.radar_param.sys.mid_frequency

        self.delta_range = np.float32(c / (2 * self.radar_param.sys.ramp_bandwidth[0]))
        self.radar_param.sys.max_dsp_freq = self.radar_param.sys.sampling_frequency / 2  # Nyquist Frequency 
        self.radar_param.sys.min_range = (c * (self.radar_param.sys.bgt_hp_fc[0]
                                              if self.radar_param.sys.bgt_hp_fc[0]
                                               > self.radar_param.dsp.hp_filter_cutoff
                                              else self.radar_param.dsp.hp_filter_cutoff)) \
                                          / (self.radar_param.sys.ramp_slope[0] * 2) # minimum detectable range
        self.radar_param.sys.max_range = c * self.radar_param.sys.max_dsp_freq \
                                          / (self.radar_param.sys.ramp_slope[0] * 2)

        timing_once_each_frame = self.radar_param.sys.t_wkup + self.radar_param.sys.t_fed + self.radar_param.sys.t_init0 + self.radar_param.sys.t_init1
        const_timings_each_chirp = self.radar_param.sys.t_start + self.radar_param.sys.t_end
        chirp_timings = [(self.radar_param.sys.t_ed[0] + self.radar_param.sys.ramp_time[0]),
                         (self.radar_param.sys.t_ed[1] + self.radar_param.sys.ramp_time[1])]
        shape_timings = self.radar_param.sys.t_sed[0] * self.radar_param.sys.shape_set_repetition \
                      + self.radar_param.sys.t_sed[1] * (self.radar_param.sys.shape_set_repetition-1)
        
        self.radar_param.sys.frame_duration = timing_once_each_frame + shape_timings +\
                                          ((((const_timings_each_chirp + chirp_timings[0]) * self.radar_param.sys.shape_repetition[0])) + \
                                            ((const_timings_each_chirp + chirp_timings[1]) * self.radar_param.sys.shape_repetition[1])) * self.radar_param.sys.shape_set_repetition
        print(f'{self.radar_param.sys.frame_duration=}')
        self.radar_param.sys.frames_per_second = (1/self.radar_param.sys.frame_duration)
 
        print(self.radar_param.sys.pulse_repetition_time) 
        self.radar_param.sys.pulse_repetition_time = chirp_timings[0] + const_timings_each_chirp + self.radar_param.sys.t_sed[0]
        print(self.radar_param.sys.pulse_repetition_time) 
        self.radar_param.sys.coherent_pulse_interval = self.radar_param.sys.pulse_repetition_time + chirp_timings[1] + const_timings_each_chirp + chirp_timings[0] + const_timings_each_chirp + self.radar_param.sys.t_sed[1]
        print(self.radar_param.sys.coherent_pulse_interval) 

        self.radar_param.sys.max_velocity = np.float32(self.radar_param.sys.lambda_freq[0] \
                                                        / (4 * self.radar_param.sys.pulse_repetition_time))
        
        self.radar_param.sys.resolution_velocity = \
            np.float32(self.radar_param.sys.lambda_freq[0] \
                        / (4 * self.radar_param.sys.coherent_pulse_interval * 2))
        self.calc_system_parameters()
        
    def calc_system_parameters(self):
        self.radar_param.sys.max_velocity = np.float32(self.radar_param.sys.lambda_freq / (4 * self.radar_param.sys.pulse_repetition_time))
        self.radar_param.sys.resolution_range = np.float32(c / (2 * self.radar_param.sys.ramp_bandwidth[0]))
        self.radar_param.sys.max_dsp_freq = np.float32(self.radar_param.sys.sampling_frequency / 2) 
        self.radar_param.sys.min_range = np.float32(c * self.radar_param.dsp.hp_filter_cutoff / (2 * self.radar_param.sys.ramp_slope[0]))
        self.radar_param.sys.max_range = np.float32(c * self.radar_param.sys.max_dsp_freq / (2 * self.radar_param.sys.ramp_slope[0]))  
        self.radar_param.sys.resolution_velocity = \
            np.float32(self.radar_param.sys.lambda_freq / (4 * self.radar_param.sys.coherent_pulse_interval *2))
            
    @property
    def CONTENT(self):
        return build_content(self)
