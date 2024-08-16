import __init__
import ctypes
from loguru import logger
import numpy as np
import radar_eval.radar_sensor.MiRa6024_register_defintion as BGT_REG
from radar_eval.radar_system.radar_system_definition import MIRA_RADAR_PARAMETER
from radar_eval.communication.radar_bridge_usb_device import MIRA_USB_SPI_BRIDGE
from radar_eval.radar_sensor.radar_sensor_register_helper import set_reg_val, build_content

# ==============================================================================
# Class Name: BGT_MAIN
# ==============================================================================
class BGT_MAIN:
    def __init__(self, device):
        self._LDO_MODE = None 
        self._LOAD_STRENGTH = None 
        self._MADC_BG_CLK_DIV = None 
        self._SADC_BG_CLK_DIV = None 
        self._CW_MODE = None  
        self._TR_WKUP_MUL = None
        self._TR_WKUP = None  
        self._FIFO_RESET = None
        self._FSM_RESET = None 
        self._SW_RESET = None  
        self._FRAME_START = None
        
        self.usb_spi_bridge: MIRA_USB_SPI_BRIDGE = device.mira_bridge
        self.radar_param: MIRA_RADAR_PARAMETER = device.radar_param
        self.REG_DEF = BGT_REG.MAIN_REG
    
    @property
    def LDO_MODE(self):
        return self._LDO_MODE

    @LDO_MODE.setter
    def LDO_MODE(self, value):
        self._LDO_MODE = value
        set_reg_val(self)

    @property
    def LOAD_STRENGTH(self):
        return self._LOAD_STRENGTH

    @LOAD_STRENGTH.setter
    def LOAD_STRENGTH(self, value):
        self._LOAD_STRENGTH = value
        set_reg_val(self)

    @property
    def MADC_BG_CLK_DIV(self):
        return self._MADC_BG_CLK_DIV

    @MADC_BG_CLK_DIV.setter
    def MADC_BG_CLK_DIV(self, value):
        self._MADC_BG_CLK_DIV = value
        set_reg_val(self)

    @property
    def SADC_BG_CLK_DIV(self):
        return self._SADC_BG_CLK_DIV

    @SADC_BG_CLK_DIV.setter
    def SADC_BG_CLK_DIV(self, value):
        self._SADC_BG_CLK_DIV = value
        set_reg_val(self)

    @property
    def CW_MODE(self):
        return self._CW_MODE

    @CW_MODE.setter
    def CW_MODE(self, value):
        self._CW_MODE = value
        set_reg_val(self)

    @property
    def TR_WKUP_MUL(self):
        return self._TR_WKUP_MUL

    @TR_WKUP_MUL.setter
    def TR_WKUP_MUL(self, value):
        self._TR_WKUP_MUL = value
        set_reg_val(self)

    @property
    def TR_WKUP(self):
        return self._TR_WKUP

    @TR_WKUP.setter
    def TR_WKUP(self, value):
        self._TR_WKUP = value
        set_reg_val(self)
        self.get_wakeup_time()
        
    def get_wakeup_time(self):
        # T_WKUP = (TR_WKUP x 2^TR_WKUP_MUL x 8 + TR_WKUP_MUL +3) x TSYS_CLK
        self.radar_param.sys.t_wkup = (self._TR_WKUP * 2**self._TR_WKUP_MUL * 8 + self._TR_WKUP_MUL + 3) * (1/80e6)
        
    def calculate_wakeup_registers(self, target_t_wu=1e-3, tsys_clk=1/80e6):
        min_error = float('inf')
        best_tr_wkup_mul = None
        best_tr_wkup = None

        # Iterate over integer values of TR_WKUP_MUL
        for tr_wkup_mul in range(16):  # Assuming TR_WKUP_MUL is 4-bit (0 to 15)
            # Iterate over integer values of TR_WKUP
            for tr_wkup in range(1, 256):  # Assuming TR_WKUP is 8-bit (1 to 255)
                # Calculate T_WU for the current values
                calculated_t_wu = (tr_wkup * 2**tr_wkup_mul * 8 + tr_wkup_mul + 3) * tsys_clk

                # Compute the absolute error from the target T_WU
                error = abs(calculated_t_wu - target_t_wu)

                # Update the best parameters if the current error is smaller
                if error < min_error:
                    min_error = error
                    best_tr_wkup_mul = tr_wkup_mul
                    best_tr_wkup = tr_wkup

        return best_tr_wkup_mul, best_tr_wkup
    
    @property
    def FIFO_RESET(self):
        return self._FIFO_RESET

    @FIFO_RESET.setter
    def FIFO_RESET(self, value):
        self._FIFO_RESET = value
        set_reg_val(self)

    @property
    def FSM_RESET(self):
        return self._FSM_RESET

    @FSM_RESET.setter
    def FSM_RESET(self, value):
        self._FSM_RESET = value
        set_reg_val(self)
        self._FSM_RESET = 0

    @property
    def SW_RESET(self):
        return self._SW_RESET

    @SW_RESET.setter
    def SW_RESET(self, value):
        self._SW_RESET = value
        set_reg_val(self)
        self._SW_RESET = 0
        
    @property
    def FRAME_START(self):
        return self._FRAME_START

    @FRAME_START.setter
    def FRAME_START(self, value):
        self._FRAME_START = value
        set_reg_val(self)
        self._FRAME_START = 0
        
    def convert_all_values(self):
        self.get_wakeup_time()
        
    @property
    def CONTENT(self):
        return build_content(self)
    
    @property
    def CONVERT(self):
        return self.convert_all_values()


# ==============================================================================
# Class Name: BGT_ADC0
# ==============================================================================
class BGT_ADC0:
    def __init__(self, device):
        self._ADC_DIV = None 
        self._BG_CHOP_EN = None 
        self._ADC_OVERS_CFG = None 
        self._TRIG_MADC = None
        self._MSB_CTRL = None
        self._TRACK_CFG = None
        self._BG_TC_TRIM = None 
        self._DSCAL = None
        self._STC = None 
        
        self.usb_spi_bridge: MIRA_USB_SPI_BRIDGE = device.mira_bridge
        self.radar_param: MIRA_RADAR_PARAMETER = device.radar_param
        self.REG_DEF = BGT_REG.ADC0_REG
          
    @property
    def ADC_DIV(self):
        return self._ADC_DIV

    @ADC_DIV.setter
    def ADC_DIV(self, value):
        self._ADC_DIV = value
        set_reg_val(self)

    def calc_sampling_frequency(self) -> None:
        self.radar_param.sys.sampling_frequency = np.float32(80*1e6 / (self._ADC_DIV+np.finfo(float).eps)) # TODO : const clk 
        pass
    
    def set_sampling_frequency(self, sample_rate) -> None:
        self.radar_param.sys.sampling_frequency = sample_rate
        self.ADC_DIV = np.uint16(80*1e6/sample_rate)
        
    @property
    def BG_CHOP_EN(self):
        return self._BG_CHOP_EN

    @BG_CHOP_EN.setter
    def BG_CHOP_EN(self, value):
        self._BG_CHOP_EN = value
        set_reg_val(self)

    @property
    def ADC_OVERS_CFG(self):
        return self._ADC_OVERS_CFG

    @ADC_OVERS_CFG.setter
    def ADC_OVERS_CFG(self, value):
        self._ADC_OVERS_CFG = value
        set_reg_val(self)

    @property
    def TRIG_MADC(self):
        return self._TRIG_MADC

    @TRIG_MADC.setter
    def TRIG_MADC(self, value):
        self._TRIG_MADC = value
        set_reg_val(self)

    @property
    def MSB_CTRL(self):
        return self._MSB_CTRL

    @MSB_CTRL.setter
    def MSB_CTRL(self, value):
        self._MSB_CTRL = value
        set_reg_val(self)

    @property
    def TRACK_CFG(self):
        return self._TRACK_CFG

    @TRACK_CFG.setter
    def TRACK_CFG(self, value):
        self._TRACK_CFG = value
        set_reg_val(self)

    @property
    def BG_TC_TRIM(self):
        return self._BG_TC_TRIM

    @BG_TC_TRIM.setter
    def BG_TC_TRIM(self, value):
        self._BG_TC_TRIM = value
        set_reg_val(self)

    @property
    def DSCAL(self):
        return self._DSCAL

    @DSCAL.setter
    def DSCAL(self, value):
        self._DSCAL = value
        set_reg_val(self)

    @property
    def STC(self):
        return self._STC

    @STC.setter
    def STC(self, value):
        self._STC = value
        set_reg_val(self)
    
    def convert_all_values(self):
        self.calc_sampling_frequency()
        
    @property
    def CONTENT(self):
        return build_content(self)
    
    @property
    def CONVERT(self):
        return self.convert_all_values()


# ==============================================================================
# Class Name: BGT_CHIP_VERSION
# ==============================================================================
class BGT_CHIP_VERSION:
    def __init__(self, device):
        self.DIGITAL_ID = None
        self.RF_ID = None
        
        self.usb_spi_bridge: MIRA_USB_SPI_BRIDGE = device.mira_bridge
        self.radar_param: MIRA_RADAR_PARAMETER = device.radar_param

        self.REG_DEF = BGT_REG.CHIP_VERSION_REG
        
    @property
    def DIGITAL_ID(self):
        return self._DIGITAL_ID

    @DIGITAL_ID.setter
    def DIGITAL_ID(self, value):
        self._DIGITAL_ID = value

    @property
    def RF_ID(self):
        return self._RF_ID

    @RF_ID.setter
    def RF_ID(self, value):
        self._RF_ID = value
    
    def convert_all_values(self):
        pass
        
    @property
    def CONTENT(self):
        return build_content(self)
    
    @property
    def CONVERT(self):
        return self.convert_all_values()


# ==============================================================================
# Class Name: BGT_STAT1
# ==============================================================================
class BGT_STAT1:
    def __init__(self, device):
        self._FRAME_CNT = None 
        self._SHAPE_GRP_CNT = None
        
        self.usb_spi_bridge: MIRA_USB_SPI_BRIDGE = device.mira_bridge
        self.radar_param: MIRA_RADAR_PARAMETER = device.radar_param
        self.REG_DEF = BGT_REG.STAT1_REG

    @property
    def FRAME_CNT(self):
        return self._FRAME_CNT

    @FRAME_CNT.setter
    def FRAME_CNT(self, value):
        self._FRAME_CNT = value

    @property
    def SHAPE_GRP_CNT(self):
        return self._SHAPE_GRP_CNT

    @SHAPE_GRP_CNT.setter
    def SHAPE_GRP_CNT(self, value):
        self._SHAPE_GRP_CNT = value

    def convert_all_values(self):
        pass
        
    @property
    def CONTENT(self):
        return build_content(self)
    
    @property
    def CONVERT(self):
        return self.convert_all_values()


# ==============================================================================
# Class Name: BGT_PACR1
# ==============================================================================
class BGT_PACR1:
    def __init__(self, device):
        self._OSCCLKEN = None 
        self._BIASFORC = None
        self._LOCKFORC = None
        self._LOCKSEL = None
        self._RLFSEL = None
        self._RFILTSEL = None
        self._VREFSEL = None
        self._BGAPEN = None
        self._VDIGREG = None
        self._DIGPON = None
        self._VANAREG = None 
        self._ANAPON = None
        self._LFEN = None
        self._CPEN = None
        self._ICPSEL = None
        self._U2IEN = None
        
        self.usb_spi_bridge: MIRA_USB_SPI_BRIDGE = device.mira_bridge
        self.radar_param: MIRA_RADAR_PARAMETER = device.radar_param
        self.REG_DEF = BGT_REG.PACR1_REG
        
    @property
    def OSCCLKEN(self):
        return self._OSCCLKEN

    @OSCCLKEN.setter
    def OSCCLKEN(self, value):
        self._OSCCLKEN = value
        set_reg_val(self)

    @property
    def BIASFORC(self):
        return self._BIASFORC

    @BIASFORC.setter
    def BIASFORC(self, value):
        self._BIASFORC = value
        set_reg_val(self)

    @property
    def LOCKFORC(self):
        return self._LOCKFORC

    @LOCKFORC.setter
    def LOCKFORC(self, value):
        self._LOCKFORC = value
        set_reg_val(self)

    @property
    def LOCKSEL(self):
        return self._LOCKSEL

    @LOCKSEL.setter
    def LOCKSEL(self, value):
        self._LOCKSEL = value
        set_reg_val(self)

    @property
    def RLFSEL(self):
        return self._RLFSEL

    @RLFSEL.setter
    def RLFSEL(self, value):
        self._RLFSEL = value
        set_reg_val(self)

    @property
    def RFILTSEL(self):
        return self._RFILTSEL

    @RFILTSEL.setter
    def RFILTSEL(self, value):
        self._RFILTSEL = value
        set_reg_val(self)

    @property
    def VREFSEL(self):
        return self._VREFSEL

    @VREFSEL.setter
    def VREFSEL(self, value):
        self._VREFSEL = value
        set_reg_val(self)

    @property
    def BGAPEN(self):
        return self._BGAPEN

    @BGAPEN.setter
    def BGAPEN(self, value):
        self._BGAPEN = value
        set_reg_val(self)

    @property
    def VDIGREG(self):
        return self._VDIGREG

    @VDIGREG.setter
    def VDIGREG(self, value):
        self._VDIGREG = value
        set_reg_val(self)

    @property
    def DIGPON(self):
        return self._DIGPON

    @DIGPON.setter
    def DIGPON(self, value):
        self._DIGPON = value
        set_reg_val(self)

    @property
    def VANAREG(self):
        return self._VANAREG

    @VANAREG.setter
    def VANAREG(self, value):
        self._VANAREG = value
        set_reg_val(self)

    @property
    def ANAPON(self):
        return self._ANAPON

    @ANAPON.setter
    def ANAPON(self, value):
        self._ANAPON = value
        set_reg_val(self)

    @property
    def LFEN(self):
        return self._LFEN

    @LFEN.setter
    def LFEN(self, value):
        self._LFEN = value
        set_reg_val(self)

    @property
    def CPEN(self):
        return self._CPEN

    @CPEN.setter
    def CPEN(self, value):
        self._CPEN = value
        set_reg_val(self)

    @property
    def ICPSEL(self):
        return self._ICPSEL

    @ICPSEL.setter
    def ICPSEL(self, value):
        self._ICPSEL = value
        set_reg_val(self)

    @property
    def U2IEN(self):
        return self._U2IEN

    @U2IEN.setter
    def U2IEN(self, value):
        self._U2IEN = value
        set_reg_val(self)

    def convert_all_values(self):
        pass
        
    @property
    def CONTENT(self):
        return build_content(self)
    
    @property
    def CONVERT(self):
        return self.convert_all_values()


# ==============================================================================
# Class Name: BGT_PACR2
# ==============================================================================
class BGT_PACR2:
    def __init__(self, device):
        self._DTSEL = None
        self._TRIVREG = None
        self._FSDNTMR = None
        self._FSTDNEN = None
        self._DIVEN = None
        self._DIVSET = None
        
        self.usb_spi_bridge: MIRA_USB_SPI_BRIDGE = device.mira_bridge
        self.radar_param: MIRA_RADAR_PARAMETER = device.radar_param
        self.REG_DEF = BGT_REG.PACR2_REG
            
    @property
    def DTSEL(self):
        return self._DTSEL

    @DTSEL.setter
    def DTSEL(self, value):
        self._DTSEL = value
        set_reg_val(self)

    @property
    def TRIVREG(self):
        return self._TRIVREG

    @TRIVREG.setter
    def TRIVREG(self, value):
        self._TRIVREG = value
        set_reg_val(self)

    @property
    def FSDNTMR(self):
        return self._FSDNTMR

    @FSDNTMR.setter
    def FSDNTMR(self, value):
        self._FSDNTMR = value
        set_reg_val(self)

    @property
    def FSTDNEN(self):
        return self._FSTDNEN

    @FSTDNEN.setter
    def FSTDNEN(self, value):
        self._FSTDNEN = value
        set_reg_val(self)

    @property
    def DIVEN(self):
        return self._DIVEN

    @DIVEN.setter
    def DIVEN(self, value):
        self._DIVEN = value
        set_reg_val(self)

    @property
    def DIVSET(self):
        return self._DIVSET

    @DIVSET.setter
    def DIVSET(self, value):
        self._DIVSET = value
        set_reg_val(self)

    def convert_all_values(self):
        pass
        
    @property
    def CONTENT(self):
        return build_content(self)
    
    @property
    def CONVERT(self):
        return self.convert_all_values()


# ==============================================================================
# Class Name: BGT_SFCTL
# ==============================================================================
class BGT_SFCTL:
    def __init__(self, device):
        self._PREFIX_EN = None
        self._MISO_HS_RD = None
        self._FIFO_LP_MODE = None
        self._LFSR_EN = None
        self._QSPI_WT = None
        self._FIFO_CREF = None
        
        self.usb_spi_bridge: MIRA_USB_SPI_BRIDGE = device.mira_bridge
        self.radar_param: MIRA_RADAR_PARAMETER = device.radar_param
        self.REG_DEF = BGT_REG.SFCTL_REG

    @property
    def PREFIX_EN(self):
        return self._PREFIX_EN

    @PREFIX_EN.setter
    def PREFIX_EN(self, value):
        self._PREFIX_EN = value
        set_reg_val(self)
        
    @property
    def MISO_HS_RD(self):
        return self._MISO_HS_RD

    @MISO_HS_RD.setter
    def MISO_HS_RD(self, value):
        self._MISO_HS_RD = value
        set_reg_val(self)

    @property
    def FIFO_LP_MODE(self):
        return self._FIFO_LP_MODE

    @FIFO_LP_MODE.setter
    def FIFO_LP_MODE(self, value):
        self._FIFO_LP_MODE = value
        set_reg_val(self)

    @property
    def LFSR_EN(self):
        return self._LFSR_EN

    @LFSR_EN.setter
    def LFSR_EN(self, value):
        self._LFSR_EN = value
        set_reg_val(self)

    @property
    def QSPI_WT(self):
        return self._QSPI_WT

    @QSPI_WT.setter
    def QSPI_WT(self, value):
        self._QSPI_WT = value
        set_reg_val(self)

    @property
    def FIFO_CREF(self):
        return self._FIFO_CREF

    @FIFO_CREF.setter
    def FIFO_CREF(self, value):
        self._FIFO_CREF = value
        set_reg_val(self)

    def convert_all_values(self):
        pass
        
    @property
    def CONTENT(self):
        return build_content(self)
    
    @property
    def CONVERT(self):
        return self.convert_all_values()
    

# ==============================================================================
# Class Name: BGT_SADC_CTRL
# ==============================================================================
class BGT_SADC_CTRL:
    def __init__(self, device):
        self._TC_TRIM =None
        self._DSCAL =None
        self._LVGAIN =None
        self._SESP =None
        self._SD_EN =None 
        self._SADC_CLK_DIV =None 
        self._SADC_START =None
        self._SADC_CHSEL =None
        
        self.usb_spi_bridge: MIRA_USB_SPI_BRIDGE = device.mira_bridge
        self.radar_param: MIRA_RADAR_PARAMETER = device.radar_param
        self.REG_DEF = BGT_REG.SADC_CTRL_REG
        
    @property
    def TC_TRIM(self):
        return self._TC_TRIM

    @TC_TRIM.setter
    def TC_TRIM(self, value):
        self._TC_TRIM = value
        set_reg_val(self)

    @property
    def DSCAL(self):
        return self._DSCAL

    @DSCAL.setter
    def DSCAL(self, value):
        self._DSCAL = value
        set_reg_val(self)

    @property
    def LVGAIN(self):
        return self._LVGAIN

    @LVGAIN.setter
    def LVGAIN(self, value):
        self._LVGAIN = value
        set_reg_val(self)

    @property
    def SESP(self):
        return self._SESP

    @SESP.setter
    def SESP(self, value):
        self._SESP = value
        set_reg_val(self)

    @property
    def SD_EN(self):
        return self._SD_EN

    @SD_EN.setter
    def SD_EN(self, value):
        self._SD_EN = value
        set_reg_val(self)

    @property
    def SADC_CLK_DIV(self):
        return self._SADC_CLK_DIV

    @SADC_CLK_DIV.setter
    def SADC_CLK_DIV(self, value):
        self._SADC_CLK_DIV = value
        set_reg_val(self)

    @property
    def SADC_START(self):
        return self._SADC_START

    @SADC_START.setter
    def SADC_START(self, value):
        self._SADC_START = value
        set_reg_val(self)

    @property
    def SADC_CHSEL(self):
        return self._SADC_CHSEL

    @SADC_CHSEL.setter
    def SADC_CHSEL(self, value):
        self._SADC_CHSEL = value
        set_reg_val(self)

    def convert_all_values(self):
        pass
        
    @property
    def CONTENT(self):
        return build_content(self)
    
    @property
    def CONVERT(self):
        return self.convert_all_values()


# ==============================================================================
# Class Name: BGT_CSX_0
# ==============================================================================
class BGT_CSX_0:
    def __init__(self, device, reg_adr: BGT_REG.CSX_0_REG):
        self._BBCHGLOB_EN =None  
        self._RX4MIX_EN =None   
        self._RX4LOBUF_EN =None 
        self._RX3MIX_EN =None   
        self._RX3LOBUF_EN =None 
        self._RX2MIX_EN =None  
        self._RX2LOBUF_EN =None  
        self._RX1MIX_EN =None   
        self._RX1LOBUF_EN =None   
        self._LO_DIST1_EN =None   
        self._LO_DIST2_EN =None  
        self._FDIV_EN =None   
        self._TEST_DIV_EN =None 
        self._VCO_EN = None 
        self._PD2_EN =None  
        self._TX2_EN =None 
        self._PD1_EN =None
        self._TX1_EN =None
        
        self.REG_ADR = reg_adr
        self.usb_spi_bridge: MIRA_USB_SPI_BRIDGE = device.mira_bridge
        self.radar_param: MIRA_RADAR_PARAMETER = device.radar_param
        self.REG_DEF = BGT_REG.CSX_0_REG
        
    @property
    def BBCHGLOB_EN(self):
        return self._BBCHGLOB_EN

    @BBCHGLOB_EN.setter
    def BBCHGLOB_EN(self, value):
        self._BBCHGLOB_EN = value
        set_reg_val(self)

    @property
    def RX4MIX_EN(self):
        return self._RX4MIX_EN

    @RX4MIX_EN.setter
    def RX4MIX_EN(self, value):
        self._RX4MIX_EN = value
        set_reg_val(self)

    @property
    def RX4LOBUF_EN(self):
        return self._RX4LOBUF_EN

    @RX4LOBUF_EN.setter
    def RX4LOBUF_EN(self, value):
        self._RX4LOBUF_EN = value
        set_reg_val(self)

    @property
    def RX3MIX_EN(self):
        return self._RX3MIX_EN

    @RX3MIX_EN.setter
    def RX3MIX_EN(self, value):
        self._RX3MIX_EN = value
        set_reg_val(self)

    @property
    def RX3LOBUF_EN(self):
        return self._RX3LOBUF_EN

    @RX3LOBUF_EN.setter
    def RX3LOBUF_EN(self, value):
        self._RX3LOBUF_EN = value
        set_reg_val(self)

    @property
    def RX2MIX_EN(self):
        return self._RX2MIX_EN

    @RX2MIX_EN.setter
    def RX2MIX_EN(self, value):
        self._RX2MIX_EN = value
        set_reg_val(self)

    @property
    def RX2LOBUF_EN(self):
        return self._RX2LOBUF_EN

    @RX2LOBUF_EN.setter
    def RX2LOBUF_EN(self, value):
        self._RX2LOBUF_EN = value
        set_reg_val(self)

    @property
    def RX1MIX_EN(self):
        return self._RX1MIX_EN

    @RX1MIX_EN.setter
    def RX1MIX_EN(self, value):
        self._RX1MIX_EN = value
        set_reg_val(self)

    @property
    def RX1LOBUF_EN(self):
        return self._RX1LOBUF_EN

    @RX1LOBUF_EN.setter
    def RX1LOBUF_EN(self, value):
        self._RX1LOBUF_EN = value
        set_reg_val(self)

    @property
    def LO_DIST1_EN(self):
        return self._LO_DIST1_EN

    @LO_DIST1_EN.setter
    def LO_DIST1_EN(self, value):
        self._LO_DIST1_EN = value
        set_reg_val(self)

    @property
    def LO_DIST2_EN(self):
        return self._LO_DIST2_EN

    @LO_DIST2_EN.setter
    def LO_DIST2_EN(self, value):
        self._LO_DIST2_EN = value
        set_reg_val(self)

    @property
    def FDIV_EN(self):
        return self._FDIV_EN

    @FDIV_EN.setter
    def FDIV_EN(self, value):
        self._FDIV_EN = value
        set_reg_val(self)

    @property
    def TEST_DIV_EN(self):
        return self._TEST_DIV_EN

    @TEST_DIV_EN.setter
    def TEST_DIV_EN(self, value):
        self._TEST_DIV_EN = value
        set_reg_val(self)

    @property
    def VCO_EN(self):
        return self._VCO_EN

    @VCO_EN.setter
    def VCO_EN(self, value):
        self._VCO_EN = value
        set_reg_val(self)

    @property
    def PD2_EN(self):
        return self._PD2_EN

    @PD2_EN.setter
    def PD2_EN(self, value):
        self._PD2_EN = value
        set_reg_val(self)

    @property
    def TX2_EN(self):
        return self._TX2_EN

    @TX2_EN.setter
    def TX2_EN(self, value):
        self._TX2_EN = value
        set_reg_val(self)

    @property
    def PD1_EN(self):
        return self._PD1_EN

    @PD1_EN.setter
    def PD1_EN(self, value):
        self._PD1_EN = value
        set_reg_val(self)

    @property
    def TX1_EN(self):
        return self._TX1_EN

    @TX1_EN.setter
    def TX1_EN(self, value):
        self._TX1_EN = value
        set_reg_val(self)
        
    def get_rx_active_antennas(self) -> None:
        rx = [self._RX1MIX_EN, self._RX2MIX_EN, self._RX3MIX_EN, self._RX4MIX_EN]

        # Mapping REG_ADR values to their corresponding indices
        reg_adr_to_index = {
            BGT_REG.CSX_0_REG.CSU1_0_ADR: 0,
            BGT_REG.CSX_0_REG.CSU2_0_ADR: 1,
            BGT_REG.CSX_0_REG.CSU3_0_ADR: 2,
            BGT_REG.CSX_0_REG.CSU4_0_ADR: 3,
            BGT_REG.CSX_0_REG.CSD1_0_ADR: 4,
            BGT_REG.CSX_0_REG.CSD2_0_ADR: 5,
            BGT_REG.CSX_0_REG.CSD3_0_ADR: 6,
            BGT_REG.CSX_0_REG.CSD4_0_ADR: 7
        }

        index = reg_adr_to_index.get(self.REG_ADR)
        if index is not None:
            self.radar_param.sys.rx_active_antennas[index] = sum(rx)
    
    def set_rx_active_antennas(self, index, value):
        # Mapping indices to REG_ADR values
        index_to_reg_adr = {
            0: BGT_REG.CSX_0_REG.CSU1_0_ADR,
            1: BGT_REG.CSX_0_REG.CSU2_0_ADR,
            2: BGT_REG.CSX_0_REG.CSU3_0_ADR,
            3: BGT_REG.CSX_0_REG.CSU4_0_ADR,
            4: BGT_REG.CSX_0_REG.CSD1_0_ADR,
            5: BGT_REG.CSX_0_REG.CSD2_0_ADR,
            6: BGT_REG.CSX_0_REG.CSD3_0_ADR,
            7: BGT_REG.CSX_0_REG.CSD4_0_ADR
        }

        self.REG_ADR = index_to_reg_adr.get(index)

        # Assuming value is the sum of the RX mixers
        # We have to estimate the individual values as we only have their sum
        self.RX1MIX_EN = 1 if value >= 1 else 0
        self.RX2MIX_EN = 1 if value >= 2 else 0
        self.RX3MIX_EN = 1 if value >= 3 else 0
        self.RX4MIX_EN = 1 if value == 4 else 0

    def get_tx_active_antennas(self) -> None:
        tx = [self._TX1_EN, self._TX2_EN]

        # Mapping REG_ADR values to their corresponding indices
        reg_adr_to_index = {
            BGT_REG.CSX_0_REG.CSU1_0_ADR: 0,
            BGT_REG.CSX_0_REG.CSU2_0_ADR: 1,
            BGT_REG.CSX_0_REG.CSU3_0_ADR: 2,
            BGT_REG.CSX_0_REG.CSU4_0_ADR: 3,
            BGT_REG.CSX_0_REG.CSD1_0_ADR: 4,
            BGT_REG.CSX_0_REG.CSD2_0_ADR: 5,
            BGT_REG.CSX_0_REG.CSD3_0_ADR: 6,
            BGT_REG.CSX_0_REG.CSD4_0_ADR: 7
        }

        # Use the mapping to set the appropriate index in tx_active_antennas
        index = reg_adr_to_index.get(self.REG_ADR)
        if index is not None:
            self.radar_param.sys.tx_active_antennas[index] = sum(tx)
        
    
    def set_tx_active_antennas(self, index, value):
        reg_adr_mapping = {
            0: BGT_REG.CSX_0_REG.CSU1_0_ADR,
            1: BGT_REG.CSX_0_REG.CSU2_0_ADR,
            2: BGT_REG.CSX_0_REG.CSU3_0_ADR,
            3: BGT_REG.CSX_0_REG.CSU4_0_ADR,
            4: BGT_REG.CSX_0_REG.CSD1_0_ADR,
            5: BGT_REG.CSX_0_REG.CSD2_0_ADR,
            6: BGT_REG.CSX_0_REG.CSD3_0_ADR,
            7: BGT_REG.CSX_0_REG.CSD4_0_ADR
        }
       
        self.REG_ADR = reg_adr_mapping.get(index)

        if value == 2:
            self._TX1_EN = 1
            self._TX2_EN = 1
        elif value == 1:
            self._TX1_EN = 1
            self._TX2_EN = 0
        else:
            self._TX1_EN = 0
            self._TX2_EN = 0

    def convert_all_values(self):
        self.get_rx_active_antennas()
        self.get_tx_active_antennas()
        
    @property
    def CONTENT(self):
        return build_content(self)
    
    @property
    def CONVERT(self):
        return self.convert_all_values()

# ==============================================================================
# Class Name: BGT_CSX_1
# ==============================================================================
class BGT_CSX_1:
    def __init__(self, device, reg_adr: BGT_REG.CSX_1_REG):
        self._BBCH_SEL = None 
        self._BB_RSTCNT = None
        self._TEMP_MEAS_EN = None
        self._MADC_EN = None
        self._TX2_DAC = None
        self._TX1_DAC = None

        self.REG_ADR = reg_adr
        self.usb_spi_bridge: MIRA_USB_SPI_BRIDGE = device.mira_bridge
        self.radar_param: MIRA_RADAR_PARAMETER = device.radar_param
        self.REG_DEF = BGT_REG.CSX_1_REG
        
    @property
    def BBCH_SEL(self):
        return self._BBCH_SEL

    @BBCH_SEL.setter
    def BBCH_SEL(self, value):
        self._BBCH_SEL = value
        set_reg_val(self)

    @property
    def BB_RSTCNT(self):
        return self._BB_RSTCNT

    @BB_RSTCNT.setter
    def BB_RSTCNT(self, value):
        self._BB_RSTCNT = value
        set_reg_val(self)

    @property
    def TEMP_MEAS_EN(self):
        return self._TEMP_MEAS_EN

    @TEMP_MEAS_EN.setter
    def TEMP_MEAS_EN(self, value):
        self._TEMP_MEAS_EN = value
        set_reg_val(self)

    @property
    def MADC_EN(self):
        return self._MADC_EN

    @MADC_EN.setter
    def MADC_EN(self, value):
        self._MADC_EN = value
        set_reg_val(self)

    @property
    def TX2_DAC(self):
        return self._TX2_DAC

    @TX2_DAC.setter
    def TX2_DAC(self, value):
        self._TX2_DAC = value
        set_reg_val(self)

    @property
    def TX1_DAC(self):
        return self._TX1_DAC

    @TX1_DAC.setter
    def TX1_DAC(self, value):
        self._TX1_DAC = value
        set_reg_val(self)

    def get_tx_power(self) -> None:
        reg_adr_to_index = {
            BGT_REG.CSX_1_REG.CSU1_1_ADR: 0,
            BGT_REG.CSX_1_REG.CSU2_1_ADR: 1,
            BGT_REG.CSX_1_REG.CSU3_1_ADR: 2,
            BGT_REG.CSX_1_REG.CSU4_1_ADR: 3,
            BGT_REG.CSX_1_REG.CSD1_1_ADR: 4,
            BGT_REG.CSX_1_REG.CSD2_1_ADR: 5,
            BGT_REG.CSX_1_REG.CSD3_1_ADR: 6,
            BGT_REG.CSX_1_REG.CSD4_1_ADR: 7,
        }
        index = reg_adr_to_index.get(self.REG_ADR)
        if index is not None:
            self.radar_param.sys.tx_power[index] = [np.uint8(self._TX1_DAC),
                                                    np.uint8(self._TX2_DAC)]
    
    def set_tx_power(self, tx_power: np.uint8, tx_enabled: np.uint8) -> None:
        if tx_enabled == 1:
            self.TX1_DAC = np.uint8(tx_power)
        elif tx_enabled == 2:
            self.TX1_DAC = np.uint8(tx_power)
            self.TX2_DAC = np.uint8(tx_power)
            
    def set_hp_filter(self, vga_gain: int, hp_gain: int, hp_fc: int, rx_select: int) -> None:
        if rx_select == 1:
            self.VGA_GAIN1 = vga_gain
            self.HP_GAIN = np.uint8(hp_gain << 0)
            self.HPF_SEL1 = hp_fc
        if rx_select == 2:
            self.VGA_GAIN2 = vga_gain
            self.HP_GAIN = np.uint8(hp_gain << 1)
            self.HPF_SEL2 = hp_fc
        if rx_select == 3:
            self.VGA_GAIN3 = vga_gain
            self.HP_GAIN = np.uint8(hp_gain << 2)
            self.HPF_SEL3 = hp_fc
        if rx_select == 4:
            self.VGA_GAIN4 = vga_gain
            self.HP_GAIN = np.uint8(hp_gain << 3)
            self.HPF_SEL4 = hp_fc
            
    def convert_all_values(self):
        self.get_tx_power()
        
    @property
    def CONTENT(self):
        return build_content(self)
    
    @property
    def CONVERT(self):
        return self.convert_all_values()

# ==============================================================================
# Class Name: BGT_CSX_2
# ==============================================================================
class BGT_CSX_2:
    def __init__(self, device, reg_adr: BGT_REG.CSX_2_REG):
        self._HP_GAIN = None
        self._VGA_GAIN4 = None
        self._HPF_SEL4 = None
        self._VGA_GAIN3 = None
        self._HPF_SEL3 = None
        self._VGA_GAIN2 = None
        self._HPF_SEL2 = None
        self._VGA_GAIN1 = None
        self._HPF_SEL1 = None
        
        self.usb_spi_bridge: MIRA_USB_SPI_BRIDGE = device.mira_bridge
        self.radar_param: MIRA_RADAR_PARAMETER = device.radar_param
        self.REG_ADR = reg_adr
        self.REG_DEF = BGT_REG.CSX_2_REG

    @property
    def HP_GAIN(self):
        return self._HP_GAIN

    @HP_GAIN.setter
    def HP_GAIN(self, value):
        self._HP_GAIN = value
        set_reg_val(self)

    @property
    def VGA_GAIN4(self):
        return self._VGA_GAIN4

    @VGA_GAIN4.setter
    def VGA_GAIN4(self, value):
        self._VGA_GAIN4 = value
        set_reg_val(self)

    @property
    def HPF_SEL4(self):
        return self._HPF_SEL4

    @HPF_SEL4.setter
    def HPF_SEL4(self, value):
        self._HPF_SEL4 = value
        set_reg_val(self)

    @property
    def VGA_GAIN3(self):
        return self._VGA_GAIN3

    @VGA_GAIN3.setter
    def VGA_GAIN3(self, value):
        self._VGA_GAIN3 = value
        set_reg_val(self)

    @property
    def HPF_SEL3(self):
        return self._HPF_SEL3

    @HPF_SEL3.setter
    def HPF_SEL3(self, value):
        self._HPF_SEL3 = value
        set_reg_val(self)

    @property
    def VGA_GAIN2(self):
        return self._VGA_GAIN2

    @VGA_GAIN2.setter
    def VGA_GAIN2(self, value):
        self._VGA_GAIN2 = value
        set_reg_val(self)

    @property
    def HPF_SEL2(self):
        return self._HPF_SEL2

    @HPF_SEL2.setter
    def HPF_SEL2(self, value):
        self._HPF_SEL2 = value
        set_reg_val(self)

    @property
    def VGA_GAIN1(self):
        return self._VGA_GAIN1

    @VGA_GAIN1.setter
    def VGA_GAIN1(self, value):
        self._VGA_GAIN1 = value
        set_reg_val(self)

    @property
    def HPF_SEL1(self):
        return self._HPF_SEL1

    @HPF_SEL1.setter
    def HPF_SEL1(self, value):
        self._HPF_SEL1 = value
        set_reg_val(self)

    def set_hp_filter(self, vga_gain: int, hp_gain: int, hp_fc: int, rx_select: int) -> None:
        if rx_select == 1:
            self.VGA_GAIN1 = vga_gain
            self.HP_GAIN = np.uint8(hp_gain << 0)
            self.HPF_SEL1 = hp_fc
        if rx_select == 2:
            self.VGA_GAIN2 = vga_gain
            self.HP_GAIN = np.uint8(hp_gain << 1)
            self.HPF_SEL2 = hp_fc
        if rx_select == 3:
            self.VGA_GAIN3 = vga_gain
            self.HP_GAIN = np.uint8(hp_gain << 2)
            self.HPF_SEL3 = hp_fc
        if rx_select == 4:
            self.VGA_GAIN4 = vga_gain
            self.HP_GAIN = np.uint8(hp_gain << 3)
            self.HPF_SEL4 = hp_fc

    def convert_all_values(self):
        pass
        
    @property
    def CONTENT(self):
        return build_content(self)
    
    @property
    def CONVERT(self):
        return self.convert_all_values()

# ==============================================================================
# Class Name: BGT_CSCX
# ==============================================================================
class BGT_CSCX:
    def __init__(self, device, reg_adr: BGT_REG.CSCX_REG):
        self._PLL_ISOPD = None
        self._BG_TMRF_EN = None
        self._SADC_ISOPD = None
        self._MADC_ISOPD = None
        self._BG_EN = None
        self._RF_ISOPD = None
        self._ABB_ISOPD = None
        self._CS_EN = None
        self._REPC = None
        
        self.REG_ADR = reg_adr
        self.usb_spi_bridge: MIRA_USB_SPI_BRIDGE = device.mira_bridge
        self.radar_param: MIRA_RADAR_PARAMETER = device.radar_param
        self.REG_DEF = BGT_REG.CSCX_REG
        
    @property
    def PLL_ISOPD(self):
        return self._PLL_ISOPD

    @PLL_ISOPD.setter
    def PLL_ISOPD(self, value):
        self._PLL_ISOPD = value
        set_reg_val(self)

    @property
    def BG_TMRF_EN(self):
        return self._BG_TMRF_EN

    @BG_TMRF_EN.setter
    def BG_TMRF_EN(self, value):
        self._BG_TMRF_EN = value
        set_reg_val(self)

    @property
    def SADC_ISOPD(self):
        return self._SADC_ISOPD

    @SADC_ISOPD.setter
    def SADC_ISOPD(self, value):
        self._SADC_ISOPD = value
        set_reg_val(self)

    @property
    def MADC_ISOPD(self):
        return self._MADC_ISOPD

    @MADC_ISOPD.setter
    def MADC_ISOPD(self, value):
        self._MADC_ISOPD = value
        set_reg_val(self)

    @property
    def BG_EN(self):
        return self._BG_EN

    @BG_EN.setter
    def BG_EN(self, value):
        self._BG_EN = value
        set_reg_val(self)

    @property
    def RF_ISOPD(self):
        return self._RF_ISOPD

    @RF_ISOPD.setter
    def RF_ISOPD(self, value):
        self._RF_ISOPD = value
        set_reg_val(self)

    @property
    def ABB_ISOPD(self):
        return self._ABB_ISOPD

    @ABB_ISOPD.setter
    def ABB_ISOPD(self, value):
        self._ABB_ISOPD = value
        set_reg_val(self)

    @property
    def CS_EN(self):
        return self._CS_EN

    @CS_EN.setter
    def CS_EN(self, value):
        self._CS_EN = value
        set_reg_val(self)

    @property
    def REPC(self):
        return self._REPC

    @REPC.setter
    def REPC(self, value):
        self._REPC = value
        set_reg_val(self)
        
    def set_shape_set_repetition(self, n_shape_set_repetition) -> None:
        self.REPC = np.uint8(n_shape_set_repetition & 0x0F)
        
    def convert_all_values(self):
        pass
    
    @property
    def CONTENT(self):
        return build_content(self)
    
    @property
    def CONVERT(self):
        return self.convert_all_values()


# ==============================================================================
# Class Name: BGT_CCR0
# ==============================================================================
class BGT_CCR0:
    def __init__(self, device):
        self._TR_END = None
        self._CONT_MODE = None
        self._REPT = None
        self._TR_INIT1 = None
        self._TR_INIT1_MUL = None

        self.usb_spi_bridge: MIRA_USB_SPI_BRIDGE = device.mira_bridge
        self.radar_param: MIRA_RADAR_PARAMETER = device.radar_param
        self.REG_DEF = BGT_REG.CCR0_REG

    @property
    def TR_END(self):
        return self._TR_END

    @TR_END.setter
    def TR_END(self, value):
        self._TR_END = value
        set_reg_val(self)
    
    def get_end_time(self) -> None:
        # T_END = (TR_END x 8 +5) x TSYS_CLK
        self.radar_param.sys.t_end = (self._TR_END * 8 + 5) * (1/80e6)
        
    @property
    def CONT_MODE(self):
        return self._CONT_MODE

    @CONT_MODE.setter
    def CONT_MODE(self, value):
        self._CONT_MODE = value
        set_reg_val(self)

    @property
    def REPT(self):
        return self._REPT

    @REPT.setter
    def REPT(self, value):
        self._REPT = value
        set_reg_val(self)

    def set_repetition(self, n_shape_set_repetition) -> None:
        self.REPT = np.uint8(n_shape_set_repetition)
        pass
    
    @property
    def TR_INIT1(self):
        return self._TR_INIT1

    @TR_INIT1.setter
    def TR_INIT1(self, value):
        self._TR_INIT1 = value
        set_reg_val(self)

    @property
    def TR_INIT1_MUL(self):
        return self._TR_INIT1_MUL

    @TR_INIT1_MUL.setter
    def TR_INIT1_MUL(self, value):
        self._TR_INIT1_MUL = value
        set_reg_val(self)
        
    def get_init1_time(self) -> None:
        # T_INIT1 = (TR_INIT1 x 2^TR_INIT1_MUL x 8 + TR_INIT1_MUL +3 ) x TSYS_CLK
        self.radar_param.sys.t_init1 = ((self._TR_INIT1 * (2**self._TR_INIT1_MUL) * 8) + self._TR_INIT1_MUL + 3) * (1/80e6)
        
    def set_init1_time(self, t_init1, t_end):
        tsys_clk = 1 / 80e6
        min_error = float('inf')
        best_tr_init1_mul = None
        best_tr_init1 = None

        # Iterate over possible values of TR_INIT1_MUL (considering it's a 2-bit field, range is 0-3)
        for tr_init1_mul in range(4):
            # Iterate over possible values of TR_INIT1 (considering it's an 8-bit field, range is 1-255)
            for tr_init1 in range(1, 256):
                # Calculate T_INIT1 for the current values
                calculated_t_init1 = ((tr_init1 * 2**tr_init1_mul * 8) + tr_init1_mul + 3) * tsys_clk

                # Compute the absolute error from the provided T_INIT1
                error = abs(calculated_t_init1 - t_init1)

                # Update the best parameters if the current error is smaller
                if error < min_error:
                    min_error = error
                    best_tr_init1_mul = tr_init1_mul
                    best_tr_init1 = tr_init1

        # Solve for TR_END directly
        best_tr_end = int((t_end / tsys_clk - 5) / 8)

        self._TR_INIT1_MUL = best_tr_init1_mul
        self._TR_INIT1 = best_tr_init1
        self._TR_END = best_tr_end
    
    def convert_all_values(self) -> None:
        self.get_end_time()
        self.get_init1_time()
        
    @property
    def CONTENT(self):
        return build_content(self)
    
    @property
    def CONVERT(self):
        return self.convert_all_values()


# ==============================================================================
# Class Name: BGT_CCR1
# ==============================================================================
class BGT_CCR1:
    def __init__(self, device):
        self._TR_START = None
        self._PD_MODE = None
        self._TR_FED = None
        self._TR_FED_MUL = None

        self.usb_spi_bridge: MIRA_USB_SPI_BRIDGE = device.mira_bridge
        self.radar_param: MIRA_RADAR_PARAMETER = device.radar_param
        self.REG_DEF = BGT_REG.CCR1_REG

    @property
    def TR_START(self):
        return self._TR_START

    @TR_START.setter
    def TR_START(self, value):
        self._TR_START = value
        set_reg_val(self)

    def get_start_time(self) -> None:
        # T_START= (TR_START x 8 +10) x T SYS_CLK
        self.radar_param.sys.t_start = (self._TR_START * 8 + 10) * (1/80e6)
        
    @property
    def PD_MODE(self):
        return self._PD_MODE

    @PD_MODE.setter
    def PD_MODE(self, value):
        self._PD_MODE = value
        set_reg_val(self)

    @property
    def TR_FED(self):
        return self._TR_FED

    @TR_FED.setter
    def TR_FED(self, value):
        self._TR_FED = value
        set_reg_val(self)

    @property
    def TR_FED_MUL(self):
        return self._TR_FED_MUL

    @TR_FED_MUL.setter
    def TR_FED_MUL(self, value):
        self._TR_FED_MUL = value
        set_reg_val(self)

    def get_fed_time(self) -> None:
        # T_FED = (TR_FED x 2^TR_FED_MUL x 8 + TR_FED_MUL +3) x TSYS_CLK
        self.radar_param.sys.t_fed = np.uint32((np.uint32(self._TR_FED) * 2**np.uint32(self._TR_FED_MUL) * 8 + np.uint32(self._TR_FED_MUL) + 3) * (1/80e6))

    def set_fed_time(self, fed_time: np.float32) -> None:
        T_SYS_CLK = 1/(80*1e6)
        # Maximum TR_FED_MUL value (10 decimal)
        max_tr_fed_mul = 10

        for tr_fed_mul in range(max_tr_fed_mul + 1):
            # Calculate the denominator part of the formula
            factor = 2**tr_fed_mul * 8 + tr_fed_mul + 3

            # Compute TR_FED required for the given T_FED
            tr_fed = fed_time / (factor * T_SYS_CLK)

            # Ensure that TR_FED is within the valid range of [1, 255]
            if 1 <= tr_fed <= 255:
                break
        self.TR_FED = np.uint8(tr_fed)
        self.TR_FED_MUL = np.uint8(tr_fed_mul)

    def convert_all_values(self):
        self.get_start_time()
        self.get_fed_time()
        

    @property
    def CONTENT(self):
        return build_content(self)
    
    @property
    def CONVERT(self):
        return self.convert_all_values()
    
    
# ==============================================================================
# Class Name: class BGT_CCR2:
# ==============================================================================
class BGT_CCR2:
    def __init__(self, device):
        self._MAX_FRAME_CNT = None
        self._FRAME_LEN = None

        self.usb_spi_bridge: MIRA_USB_SPI_BRIDGE = device.mira_bridge
        self.radar_param: MIRA_RADAR_PARAMETER = device.radar_param
        self.REG_DEF = BGT_REG.CCR2_REG

    @property
    def MAX_FRAME_CNT(self):
        return self._MAX_FRAME_CNT

    @MAX_FRAME_CNT.setter
    def MAX_FRAME_CNT(self, value):
        self._MAX_FRAME_CNT = value
        set_reg_val(self)
        
    # Frames
    def get_max_frame_length(self) -> None:
        self.radar_param.sys.max_frame_cnt = self._MAX_FRAME_CNT
        if self.radar_param.sys.max_frame_cnt == 0:
            self.radar_param.sys.max_frame_cnt = 4096

    @property
    def FRAME_LEN(self):
        return self._FRAME_LEN

    @FRAME_LEN.setter
    def FRAME_LEN(self, value):
        self._FRAME_LEN = value
        set_reg_val(self)
    
    # Shape Set
    def get_shape_set_repetition(self) -> None:
        self.radar_param.sys.shape_set_repetition = self._FRAME_LEN + 1
    
    def set_shape_set_repetition(self, shape_set_repetition) -> None:
        self.FRAME_LEN = shape_set_repetition
        self.radar_param.sys.shape_set_repetition = shape_set_repetition
        
    def convert_all_values(self):
        self.get_max_frame_length()
        self.get_shape_set_repetition()
        
    @property
    def CONTENT(self):
        return build_content(self)
    
    @property
    def CONVERT(self):
        return self.convert_all_values()


# ==============================================================================
# Class Name: BGT_CCR3
# ==============================================================================
class BGT_CCR3:
    def __init__(self, device):
        self._TR_PAEN = None
        self._TR_SSTART = None
        self._TR_INIT0 = None
        self._TR_INIT0_MUL = None

        self.usb_spi_bridge: MIRA_USB_SPI_BRIDGE = device.mira_bridge
        self.radar_param: MIRA_RADAR_PARAMETER = device.radar_param
        self.REG_DEF = BGT_REG.CCR3_REG

    @property
    def TR_PAEN(self):
        return self._TR_PAEN

    @TR_PAEN.setter
    def TR_PAEN(self, value):
        self._TR_PAEN = value
        set_reg_val(self)

    def get_paen_time(self) -> None:
        # T_PAEN= TR_PAEN x 8 x TSYS_CLK
        self.radar_param.sys.t_paen = self._TR_PAEN * 8 *  (1/80e6) # todo clk const

    @property
    def TR_SSTART(self):
        return self._TR_SSTART

    @TR_SSTART.setter
    def TR_SSTART(self, value):
        self._TR_SSTART = value
        set_reg_val(self)

    def get_sstart_time(self) -> None:
        # T_SSTART= (TR_SSTART x 8 +1) x TSYS_CLK
        self.radar_param.sys.t_sstart = (self._TR_SSTART * 8 + 1) * (1/80e6)
        
    @property
    def TR_INIT0(self):
        return self._TR_INIT0

    @TR_INIT0.setter
    def TR_INIT0(self, value):
        self._TR_INIT0 = value
        set_reg_val(self)

    @property
    def TR_INIT0_MUL(self):
        return self._TR_INIT0_MUL

    @TR_INIT0_MUL.setter
    def TR_INIT0_MUL(self, value):
        self._TR_INIT0_MUL = value
        set_reg_val(self)

    def get_init0_time(self) -> None:
        # T_INIT0 = (TR_INIT0 x 2^TR_INIT0_MUL x 8 + TR_INIT0_MUL +3) x TSYS_CLK
        self.radar_param.sys.t_init0 = (self._TR_INIT0 * (2**self._TR_INIT0_MUL) * 8 + self._TR_INIT0_MUL + 3) * (1/80e6) 

    def convert_all_values(self):
        self.get_sstart_time()
        self.get_init0_time()
        self.get_paen_time()
        
    @property
    def CONTENT(self):
        return build_content(self)
    
    @property
    def CONVERT(self):
        return self.convert_all_values()
    
    
class BGT_PLLX_0:
    def __init__(self, device, reg_adr: BGT_REG.PLLX_0_REG):
        self._FSU = None

        self.usb_spi_bridge: MIRA_USB_SPI_BRIDGE = device.mira_bridge
        self.radar_param: MIRA_RADAR_PARAMETER = device.radar_param
        self.REG_ADR = reg_adr
        self.REG_DEF = BGT_REG.PLLX_0_REG

    @property
    def FSU(self):
        return self._FSU

    @FSU.setter
    def FSU(self, value):
        self._FSU = value
        set_reg_val(self)
        
    def get_start_frequency(self) -> None:
        reg_adr_to_index = {
            BGT_REG.PLLX_0_REG.PLL1_0_ADR: 0,
            BGT_REG.PLLX_0_REG.PLL2_0_ADR: 1,
            BGT_REG.PLLX_0_REG.PLL3_0_ADR: 2,
            BGT_REG.PLLX_0_REG.PLL4_0_ADR: 3,
        }
        index = reg_adr_to_index.get(self.REG_ADR)
        if index is not None:
            start_freq = (ctypes.c_int32(self._FSU << 8).value >> 8)
            self.radar_param.sys.start_frequency[index] = np.float32(((start_freq / 2**20) + 96) * 640e6)
        
    def set_start_frequency(self, fsu_reg_val) -> None:
        self.FSU = fsu_reg_val
         
    def convert_all_values(self):
        self.get_start_frequency()
        
    @property
    def CONTENT(self):
        return build_content(self)
    
    @property
    def CONVERT(self):
        return self.convert_all_values()
    
    
# ==============================================================================
# Class Name: BGT_PLLX_1
# ==============================================================================
class BGT_PLLX_1:
    def __init__(self, device, reg_adr: BGT_REG.PLLX_1_REG):
        self._RSU = None

        self.usb_spi_bridge: MIRA_USB_SPI_BRIDGE = device.mira_bridge
        self.radar_param: MIRA_RADAR_PARAMETER = device.radar_param
        self.REG_ADR = reg_adr
        self.REG_DEF = BGT_REG.PLLX_1_REG

    @property
    def RSU(self):
        return self._RSU

    @RSU.setter
    def RSU(self, value):
        self._RSU = value
        set_reg_val(self)
    
    def set_ramp_steps(self, rsu_reg_val=None) -> None:
        if rsu_reg_val is None:
            rtu = np.float32((self.radar_param.sys.ramp_time[0] / 8) * 80*1e6)
            value = self.radar_param.sys.ramp_bandwidth[0] / (8*rtu)
            self.RSU = np.uint32(2**20*((value)/(640*1e6)))
        else:
            self.RSU = rsu_reg_val
        
    def get_ramp_bandwidth(self) -> None:
        reg_adr_to_index = {
            BGT_REG.PLLX_1_REG.PLL1_1_ADR: 0,
            BGT_REG.PLLX_1_REG.PLL2_1_ADR: 1,
            BGT_REG.PLLX_1_REG.PLL3_1_ADR: 2,
            BGT_REG.PLLX_1_REG.PLL4_1_ADR: 3,
        }
        index = reg_adr_to_index.get(self.REG_ADR)
        if index is not None:
            self.radar_param.sys.ramp_steps[index] = self._RSU
       
    def set_bandwidth_ramp_steps(self, rsu_reg_val: np.float32) -> None:
        self.RSU = np.uint32(rsu_reg_val)
                
    def convert_all_values(self):
        self.get_ramp_bandwidth()
        
    @property
    def CONTENT(self):
        return build_content(self)
    
    @property
    def CONVERT(self):
        return self.convert_all_values()
    
    
# ==============================================================================
# Class Name: BGT_PLLX_2
# ==============================================================================
class BGT_PLLX_2:
    def __init__(self, device, reg_adr: BGT_REG.PLLX_2_REG):
        self._RTU = None
        self._TR_EDU = None
        
        self.usb_spi_bridge: MIRA_USB_SPI_BRIDGE = device.mira_bridge
        self.radar_param: MIRA_RADAR_PARAMETER = device.radar_param
        self.REG_ADR = reg_adr
        self.REG_DEF = BGT_REG.PLLX_2_REG

    @property
    def RTU(self):
        return self._RTU

    @RTU.setter
    def RTU(self, value):
        self._RTU = value
        set_reg_val(self)
    
    def set_ramp_time(self, sample_rate: np.float32) -> None:
        self.radar_param.sys.t_acqu = self.radar_param.sys.n_samples_per_chirp[0]/sample_rate
        self.radar_param.sys.ramp_time[0] = self.radar_param.sys.t_paen + self.radar_param.sys.t_sstart + \
                                            self.radar_param.sys.t_acqu - self.radar_param.sys.t_start
        self.radar_param.sys.ramp_time[1] = self.radar_param.sys.ramp_time[0]
        self.RTU = np.uint16((self.radar_param.sys.ramp_time[0] / 8) * 80*1e6)
        
        
    def get_bandwidth_slope(self) -> None:
        reg_adr_to_index = {
            BGT_REG.PLLX_2_REG.PLL1_2_ADR: 0,
            BGT_REG.PLLX_2_REG.PLL2_2_ADR: 1,
            BGT_REG.PLLX_2_REG.PLL3_2_ADR: 2,
            BGT_REG.PLLX_2_REG.PLL4_2_ADR: 3,
        }
        index = reg_adr_to_index.get(self.REG_ADR)

        if index is None:
            return
        
        self.radar_param.sys.ramp_time[index] = np.float32(self._RTU * 8 * 12.5e-9)
        self.radar_param.sys.ramp_bandwidth[index] = np.float32(self._RTU * 8 * (640e6 / 2**20) \
                                                                * self.radar_param.sys.ramp_steps[index]) # BGT Datasheet see page 32ff 
        self.radar_param.sys.end_frequency[index] = np.float32(self.radar_param.sys.start_frequency[index]
                                                               + self.radar_param.sys.ramp_bandwidth[index])
        self.radar_param.sys.ramp_slope[index] = np.float32(self.radar_param.sys.ramp_bandwidth[index] \
                                                            // (self.radar_param.sys.t_acqu
                                                              + np.finfo(np.float32).eps)) 
        
    def set_bandwidth_ramp_time(self, rtu_reg_valu: np.uint16) -> None:
        self.RTU = rtu_reg_valu

    @property
    def TR_EDU(self):
        return self._TR_EDU

    @TR_EDU.setter
    def TR_EDU(self, value):
        self._TR_EDU = value
        set_reg_val(self)

    def get_edu_time(self):
        reg_adr_to_index = {
            BGT_REG.PLLX_2_REG.PLL1_2_ADR: 0,
            BGT_REG.PLLX_2_REG.PLL2_2_ADR: 1,
            BGT_REG.PLLX_2_REG.PLL3_2_ADR: 2,
            BGT_REG.PLLX_2_REG.PLL4_2_ADR: 3,
        }
        index = reg_adr_to_index.get(self.REG_ADR)

        if self._TR_EDU == 0 and index is not None:
            # If TR_EDU/D = 0: T_EDU/D = 2 x TSYS_CLK.
            self.radar_param.sys.t_ed[index] = 2 * (1/80e6)
        elif self._TR_EDU != 0 and index is not None:
            # If TR_EDU/D > 0: T_EDU/D = (8 x TR_EDU/D + 5) x TSYS_CLK.
            self.radar_param.sys.t_ed[index] = np.uint32(8 * np.uint32(self._TR_EDU) + 5) * (1/80e6)

    def set_edu_time(self, edu_time: np.float32) -> None:
        T_SYS_CLK = 1 / (80 * 1e6)  # System clock period (12.5 ns)

        # Calculate TR_EDU required for the given edu_time
        if edu_time <= 2 * T_SYS_CLK:
            tr_edu = 0
        else:
            tr_edu = (edu_time / T_SYS_CLK - 5) / 8

        # Ensure that TR_EDU is within the valid range of [1, 255] if not zero
        if tr_edu > 0:
            tr_edu = np.clip(tr_edu, 1, 255)

        # Convert TR_EDU to appropriate data type
        self.TR_EDU = np.uint8(tr_edu)
        
    def convert_all_values(self):
        self.get_edu_time()
        self.get_bandwidth_slope()
        
    @property
    def CONTENT(self):
        return build_content(self)
    
    @property
    def CONVERT(self):
        return self.convert_all_values()


# ==============================================================================
# Class Name: BGT_PLLX_3
# ==============================================================================
class BGT_PLLX_3:
    def __init__(self, device, reg_adr: BGT_REG.PLLX_3_REG):
        self._APU = None
        self._APD = None
        
        self.usb_spi_bridge: MIRA_USB_SPI_BRIDGE = device.mira_bridge
        self.radar_param: MIRA_RADAR_PARAMETER = device.radar_param
        self.REG_ADR = reg_adr
        self.REG_DEF = BGT_REG.PLLX_3_REG

    @property
    def APU(self):
        return self._APU

    @APU.setter
    def APU(self, value):
        self._APU = value
        set_reg_val(self)

    @property
    def APD(self):
        return self._APD

    @APD.setter
    def APD(self, value):
        self._APD = value
        set_reg_val(self)

    def get_chirp_sample_len(self) -> None:
        if self.REG_ADR == BGT_REG.PLLX_3_REG.PLL1_3_ADR:
            self.radar_param.sys.n_samples_per_chirp[0] = self._APU
            self.radar_param.sys.n_samples_per_chirp[4] = self._APD
        elif self.REG_ADR == BGT_REG.PLLX_3_REG.PLL2_3_ADR:
            self.radar_param.sys.n_samples_per_chirp[1] = self._APU
            self.radar_param.sys.n_samples_per_chirp[5] = self._APD
        elif self.REG_ADR == BGT_REG.PLLX_3_REG.PLL3_3_ADR:
            self.radar_param.sys.n_samples_per_chirp[2] = self._APU
            self.radar_param.sys.n_samples_per_chirp[6] = self._APD
        elif self.REG_ADR == BGT_REG.PLLX_3_REG.PLL4_3_ADR:
            self.radar_param.sys.n_samples_per_chirp[3] = self._APU
            self.radar_param.sys.n_samples_per_chirp[7] = self._APD
    
    def set_chirp_sample_len(self, n_sample: np.uint16) -> None:
        self.APU = np.uint16(n_sample)
        self.radar_param.sys.n_samples_per_chirp[0] = np.uint16(n_sample)
        self.radar_param.sys.n_samples_per_chirp[1] = np.uint16(n_sample)
        self.radar_param.sys.n_samples_per_chirp[2] = np.uint16(n_sample)
        self.radar_param.sys.n_samples_per_chirp[3] = np.uint16(n_sample)
        
    def convert_all_values(self):
        self.get_chirp_sample_len()
        
    @property
    def CONTENT(self):
        return build_content(self)
    
    @property
    def CONVERT(self):
        return self.convert_all_values()


# ==============================================================================
# Class Name: BGT_PLLX_4
# ==============================================================================
class BGT_PLLX_4:
    def __init__(self, device, reg_adr: BGT_REG.PLLX_4_REG):
        self._FSD = None

        self.usb_spi_bridge: MIRA_USB_SPI_BRIDGE = device.mira_bridge
        self.radar_param: MIRA_RADAR_PARAMETER = device.radar_param
        self.REG_ADR = reg_adr
        self.REG_DEF = BGT_REG.PLLX_4_REG

    @property
    def FSD(self):
        return self._FSD

    @FSD.setter
    def FSD(self, value):
        self._FSD = value
        set_reg_val(self)
        
    def get_start_frequency(self) -> None:
        reg_adr_to_index = {
            BGT_REG.PLLX_4_REG.PLL1_4_ADR: 4,
            BGT_REG.PLLX_4_REG.PLL2_4_ADR: 5,
            BGT_REG.PLLX_4_REG.PLL3_4_ADR: 6,
            BGT_REG.PLLX_4_REG.PLL4_4_ADR: 7,
        }
        index = reg_adr_to_index.get(self.REG_ADR)

        if index is not None:
            start_freq = ctypes.c_int32(self._FSD).value
            self.radar_param.sys.start_frequency[index] = np.float32(((start_freq / 2**20) + 96) * 640e6)


    def convert_all_values(self):
        self.get_start_frequency()
        
    @property
    def CONTENT(self):
        return build_content(self)
    
    @property
    def CONVERT(self):
        return self.convert_all_values()
    

# ==============================================================================
# Class Name: BGT_PLLX_5
# ==============================================================================
class BGT_PLLX_5:
    def __init__(self, device, reg_adr: BGT_REG.PLLX_5_REG):
        self._RSD = None
        
        self.usb_spi_bridge: MIRA_USB_SPI_BRIDGE = device.mira_bridge
        self.radar_param: MIRA_RADAR_PARAMETER = device.radar_param
        self.REG_ADR = reg_adr
        self.REG_DEF = BGT_REG.PLLX_5_REG

    @property
    def RSD(self):
        return self._RSD

    @RSD.setter
    def RSD(self, value):
        self._RSD = value
        set_reg_val(self)

    def get_ramp_bandwidth(self) -> None:
        reg_adr_to_index = {
            BGT_REG.PLLX_5_REG.PLL1_5_ADR: 4,
            BGT_REG.PLLX_5_REG.PLL2_5_ADR: 5,
            BGT_REG.PLLX_5_REG.PLL3_5_ADR: 6,
            BGT_REG.PLLX_5_REG.PLL4_5_ADR: 7,
        }

        index = reg_adr_to_index.get(self.REG_ADR)
        self.radar_param.sys.ramp_steps[index] = self._RSD
        if index is not None:
            return

    def convert_all_values(self):
        pass
        
    @property
    def CONTENT(self):
        return build_content(self)
    
    @property
    def CONVERT(self):
        return self.convert_all_values()

# ==============================================================================
# Class Name: BGT_PLLX_6
# ==============================================================================
class BGT_PLLX_6:
    def __init__(self, device, reg_adr: BGT_REG.PLLX_6_REG):
        self._RTD = None
        self._TR_EDD = None

        self.usb_spi_bridge: MIRA_USB_SPI_BRIDGE = device.mira_bridge
        self.radar_param: MIRA_RADAR_PARAMETER = device.radar_param
        self.REG_ADR = reg_adr
        self.REG_DEF = BGT_REG.PLLX_6_REG

    @property
    def RTD(self):
        return self._RTD

    @RTD.setter
    def RTD(self, value):
        self._RTD = value
        set_reg_val(self)
        
    def get_bandwidth_slope(self) -> None:
        reg_adr_to_index = {
            BGT_REG.PLLX_6_REG.PLL1_6_ADR: 4,
            BGT_REG.PLLX_6_REG.PLL2_6_ADR: 5,
            BGT_REG.PLLX_6_REG.PLL3_6_ADR: 6,
            BGT_REG.PLLX_6_REG.PLL4_6_ADR: 7,
        }
        index = reg_adr_to_index.get(self.REG_ADR)

        if index is None:
            return
        
        self.radar_param.sys.ramp_time[index] = np.float32(self._RTD * 8 * 12.5e-9)
        self.radar_param.sys.ramp_time = np.nan_to_num(self.radar_param.sys.ramp_time)
        
        self.radar_param.sys.ramp_bandwidth[index] = np.float32(self._RTD * 8 * (640e6 / 2**20) 
                                                                * self.radar_param.sys.ramp_steps[index]) # BGT Datasheet see page 32ff 
        self.radar_param.sys.ramp_bandwidth = np.nan_to_num(self.radar_param.sys.ramp_bandwidth)
    
        self.radar_param.sys.end_frequency[index] = np.float32(self.radar_param.sys.start_frequency[index] +  
                                                               self.radar_param.sys.ramp_bandwidth[index])
        self.radar_param.sys.end_frequency = np.nan_to_num(self.radar_param.sys.end_frequency)
        
        self.radar_param.sys.ramp_slope[index] = np.float32(self.radar_param.sys.ramp_bandwidth[index] 
                                                            / (self.radar_param.sys.t_acqu 
                                                            + np.finfo(np.float32).eps)) 
        self.radar_param.sys.ramp_slope = np.nan_to_num(self.radar_param.sys.ramp_slope)
            
    @property
    def TR_EDD(self):
        return self._TR_EDD

    @TR_EDD.setter
    def TR_EDD(self, value):
        self._TR_EDD = value
        set_reg_val(self)
        
    def get_edd_time(self):
        reg_adr_to_index = {
            BGT_REG.PLLX_6_REG.PLL1_6_ADR: 4,
            BGT_REG.PLLX_6_REG.PLL2_6_ADR: 5,
            BGT_REG.PLLX_6_REG.PLL3_6_ADR: 6,
            BGT_REG.PLLX_6_REG.PLL4_6_ADR: 7,
        }
        index = reg_adr_to_index.get(self.REG_ADR)

        if self._TR_EDD == 0 and index is not None:
            # If TR_EDU/D = 0: T_EDU/D = 2 x TSYS_CLK.
            self.radar_param.sys.t_ed[index] = 2 * (1/80e6)
        elif self._TR_EDD != 0 and index is not None:
            # If TR_EDU/D > 0: T_EDU/D = (8 x TR_EDU/D + 5) x TSYS_CLK.
            self.radar_param.sys.t_ed[index] = (8 * self._TR_EDD + 5) * (1/80e6)
            
    def convert_all_values(self):
        self.get_edd_time()
        self.get_bandwidth_slope()
        
    @property
    def CONTENT(self):
        return build_content(self)
    
    @property
    def CONVERT(self):
        return self.convert_all_values()

# ==============================================================================
# Class Name: BGT_PLLX_7
# ==============================================================================
class BGT_PLLX_7:
    def __init__(self, device, reg_adr: BGT_REG.PLLX_0_REG):
        self._REPS = None
        self._SH_EN = None
        self._CONT_MODE = None
        self._PD_MODE = None
        self._TR_SED = None
        self._TR_SED_MUL = None

        self.usb_spi_bridge: MIRA_USB_SPI_BRIDGE = device.mira_bridge
        self.radar_param: MIRA_RADAR_PARAMETER = device.radar_param
        self.REG_ADR = reg_adr
        self.REG_DEF = BGT_REG.PLLX_7_REG

    @property
    def REPS(self):
        return self._REPS

    @REPS.setter
    def REPS(self, value):
        self._REPS = value
        set_reg_val(self)
    
    def get_shape_repetition(self) -> None:
        if self.REG_ADR == BGT_REG.PLLX_7_REG.PLL1_7_ADR:
            self.radar_param.sys.shape_repetition[0] = np.uint32(2**self._REPS)
        elif self.REG_ADR == BGT_REG.PLLX_7_REG.PLL2_7_ADR:
            self.radar_param.sys.shape_repetition[1] = np.uint32(2**self._REPS)
        elif self.REG_ADR == BGT_REG.PLLX_7_REG.PLL3_7_ADR:
            self.radar_param.sys.shape_repetition[2] = np.uint32(2**self._REPS)
        elif self.REG_ADR == BGT_REG.PLLX_7_REG.PLL4_7_ADR:
            self.radar_param.sys.shape_repetition[3] = np.uint32(2**self._REPS)
    
    def set_shape_repetition(self, rep_reg_val: np.uint16) -> None:
        if rep_reg_val == 1:
            self.REPS = 0
        elif rep_reg_val > 1:
            self.REPS = np.uint8(np.log2(rep_reg_val))
        
    @property
    def SH_EN(self):
        return self._SH_EN

    @SH_EN.setter
    def SH_EN(self, value):
        self._SH_EN = value
        set_reg_val(self)

    def get_nbr_active_shapes(self) -> None:
        if self.REG_ADR == BGT_REG.PLLX_7_REG.PLL1_7_ADR:
            self.radar_param.sys.n_active_shape[0] = np.uint8(self._SH_EN)
        elif self.REG_ADR == BGT_REG.PLLX_7_REG.PLL2_7_ADR:
            self.radar_param.sys.n_active_shape[1] = np.uint8(self._SH_EN)
        elif self.REG_ADR == BGT_REG.PLLX_7_REG.PLL3_7_ADR:
            self.radar_param.sys.n_active_shape[2] = np.uint8(self._SH_EN)
        elif self.REG_ADR == BGT_REG.PLLX_7_REG.PLL4_7_ADR:
            self.radar_param.sys.n_active_shape[3] = np.uint8(self._SH_EN)
            self.radar_param.sys.shape_set_repetition /= sum(self.radar_param.sys.n_active_shape)
            self.radar_param.sys.shape_set_repetition = np.uint16(self.radar_param.sys.shape_set_repetition)

    @property
    def CONT_MODE(self):
        return self._CONT_MODE

    @CONT_MODE.setter
    def CONT_MODE(self, value):
        self._CONT_MODE = value
        set_reg_val(self)

    @property
    def PD_MODE(self):
        return self._PD_MODE

    @PD_MODE.setter
    def PD_MODE(self, value):
        self._PD_MODE = value
        set_reg_val(self)

    @property
    def TR_SED(self):
        return self._TR_SED

    @TR_SED.setter
    def TR_SED(self, value):
        self._TR_SED = value
        set_reg_val(self)

    @property
    def TR_SED_MUL(self):
        return self._TR_SED_MUL

    @TR_SED_MUL.setter
    def TR_SED_MUL(self, value):
        self._TR_SED_MUL = value
        set_reg_val(self)
        
    def get_sed_time(self) -> None:
        reg_adr_to_index = {
            BGT_REG.PLLX_7_REG.PLL1_7_ADR: 0,
            BGT_REG.PLLX_7_REG.PLL2_7_ADR: 1,
            BGT_REG.PLLX_7_REG.PLL3_7_ADR: 2,
            BGT_REG.PLLX_7_REG.PLL4_7_ADR: 3
        }

        index = reg_adr_to_index.get(self.REG_ADR)
        if index is not None:
            # T_SED = (TR_SED x 2^TR_SED_MUL x 8 + TR_SED_MUL +3) x TSYS_CLK
            self.radar_param.sys.t_sed[index] = \
                np.uint32(np.uint32(self._TR_SED) * 2**np.uint32(self._TR_SED_MUL) * 8 + np.uint32(self._TR_SED_MUL) + 3) * (1/80e6)


    def set_sed_time(self, sed_time: np.float32) -> None:
        T_SYS_CLK = 1/(80*1e6)
        # Maximum TR_FED_MUL value (10 decimal)
        max_tr_sed_mul = 10

        for tr_sed_mul in range(max_tr_sed_mul + 1):
            # Calculate the denominator part of the formula
            factor = 2**tr_sed_mul * 8 + tr_sed_mul + 3

            # Compute TR_FED required for the given T_FED
            tr_sed = sed_time / (factor * T_SYS_CLK)

            # Ensure that TR_FED is within the valid range of [1, 255]
            if 1 <= tr_sed <= 255:
                break
        self.TR_SED = np.uint8(tr_sed)
        self.TR_SED_MUL = np.uint8(tr_sed_mul)
    
    def convert_all_values(self):
        self.get_shape_repetition()
        self.get_nbr_active_shapes()
        self.get_sed_time()
        
    @property
    def CONTENT(self):
        return build_content(self)
    
    @property
    def CONVERT(self):
        return self.convert_all_values()
    
# ==============================================================================
# Class Name: BGT_RFT0
# ==============================================================================
class BGT_RFT0:
    def __init__(self, device):
        self._TEST_SIG_IF4_EN = None
        self._TEST_SIG_IF3_EN = None
        self._TEST_SIG_IF2_EN = None
        self._TEST_SIG_IF1_EN = None
        self._RFTSIGCLK_DIV = None
        self._RFTSIGCLK_DIV_EN = None
        
        self.usb_spi_bridge: MIRA_USB_SPI_BRIDGE = device.mira_bridge
        self.radar_param: MIRA_RADAR_PARAMETER = device.radar_param
        self.REG_DEF = BGT_REG.RFT0_REG
        
    @property
    def TEST_SIG_IF4_EN(self):
        return self._TEST_SIG_IF4_EN

    @TEST_SIG_IF4_EN.setter
    def TEST_SIG_IF4_EN(self, value):
        self._TEST_SIG_IF4_EN = value
        set_reg_val(self)

    @property
    def TEST_SIG_IF3_EN(self):
        return self._TEST_SIG_IF3_EN

    @TEST_SIG_IF3_EN.setter
    def TEST_SIG_IF3_EN(self, value):
        self._TEST_SIG_IF3_EN = value
        set_reg_val(self)

    @property
    def TEST_SIG_IF2_EN(self):
        return self._TEST_SIG_IF2_EN

    @TEST_SIG_IF2_EN.setter
    def TEST_SIG_IF2_EN(self, value):
        self._TEST_SIG_IF2_EN = value
        set_reg_val(self)

    @property
    def TEST_SIG_IF1_EN(self):
        return self._TEST_SIG_IF1_EN

    @TEST_SIG_IF1_EN.setter
    def TEST_SIG_IF1_EN(self, value):
        self._TEST_SIG_IF1_EN = value
        set_reg_val(self)

    @property
    def RFTSIGCLK_DIV(self):
        return self._RFTSIGCLK_DIV

    @RFTSIGCLK_DIV.setter
    def RFTSIGCLK_DIV(self, value):
        self._RFTSIGCLK_DIV = value
        set_reg_val(self)

    @property
    def RFTSIGCLK_DIV_EN(self):
        return self._RFTSIGCLK_DIV_EN

    @RFTSIGCLK_DIV_EN.setter
    def RFTSIGCLK_DIV_EN(self, value):
        self._RFTSIGCLK_DIV_EN = value
        set_reg_val(self)

    def convert_all_values(self):
        pass
        
    @property
    def CONTENT(self):
        return build_content(self)
    
    @property
    def CONVERT(self):
        return self.convert_all_values()

# ==============================================================================
# Class Name: BGT_RFT1
# ==============================================================================
class BGT_RFT1:
    def __init__(self):
        self.reserved = None


# ==============================================================================
# Class Name: BGT_DFT0
# ==============================================================================
class BGT_DFT0:
    def __init__(self, device):
        self._EFUSE_SENSE = None
        self._EFUSE_EN = None
        self.usb_spi_bridge: MIRA_USB_SPI_BRIDGE = device.mira_bridge
        self.radar_param: MIRA_RADAR_PARAMETER = device.radar_param
        self.REG_DEF = BGT_REG.DFT0_REG

    @property
    def EFUSE_SENSE(self):
        return self._EFUSE_SENSE

    @EFUSE_SENSE.setter
    def EFUSE_SENSE(self, value):
        self._EFUSE_SENSE = value
        set_reg_val(self)

    @property
    def EFUSE_EN(self):
        return self._EFUSE_EN

    @EFUSE_EN.setter
    def EFUSE_EN(self, value):
        self._EFUSE_EN = value
        set_reg_val(self)
        
    def convert_all_values(self):
        pass
        
    @property
    def CONTENT(self):
        return build_content(self)
    
    @property
    def CONVERT(self):
        return self.convert_all_values()


# ==============================================================================
# Class Name: BGT_DFT1
# ==============================================================================
class BGT_DFT1:
    def __init__(self, device):
        self._EFUSE_READY = None
        self.usb_spi_bridge: MIRA_USB_SPI_BRIDGE = device.mira_bridge
        self.radar_param: MIRA_RADAR_PARAMETER = device.radar_param
        self.REG_DEF = BGT_REG.DFT1_REG

    @property
    def EFUSE_READY(self):
        return self._EFUSE_READY

    @EFUSE_READY.setter
    def EFUSE_READY(self, value):
        self._EFUSE_READY = value
        
    def convert_all_values(self):
        pass
        
    @property
    def CONTENT(self):
        return build_content(self)
    
    @property
    def CONVERT(self):
        return self.convert_all_values()

# ==============================================================================
# Class Name: BGT_DFT0
# ==============================================================================
class BGT_PLL_DFT0:
    def __init__(self, device):
        self._BYPSDM = None
        self._BYPSDMEN = None
        self._BYPRMPEN = None
        
        self.usb_spi_bridge: MIRA_USB_SPI_BRIDGE = device.mira_bridge
        self.radar_param: MIRA_RADAR_PARAMETER = device.radar_param
        self.REG_DEF = BGT_REG.PLL_DFT0_REG

    @property
    def BYPSDM(self):
        return self._BYPSDM

    @BYPSDM.setter
    def BYPSDM(self, value):
        self._BYPSDM = value
        set_reg_val(self)

    @property
    def BYPSDMEN(self):
        return self._BYPSDMEN

    @BYPSDMEN.setter
    def BYPSDMEN(self, value):
        self._BYPSDMEN = value
        set_reg_val(self)

    @property
    def BYPRMPEN(self):
        return self._BYPRMPEN

    @BYPRMPEN.setter
    def BYPRMPEN(self, value):
        self._BYPRMPEN = value
        set_reg_val(self)

    def convert_all_values(self):
        pass
        
    @property
    def CONTENT(self):
        return build_content(self)
    
    @property
    def CONVERT(self):
        return self.convert_all_values()


# ==============================================================================
# Class Name: BGT_STAT0
# ==============================================================================
class BGT_STAT0:
    def __init__(self, device):
        self._SH_IDX = None
        self._CH_IDX = None
        self._PM = None
        self._LDO_RDY = None
        self._MADC_BGUP = None
        self._MADC_RDY = None
        self._SADC_RDY = None
        
        self.usb_spi_bridge: MIRA_USB_SPI_BRIDGE = device.mira_bridge
        self.radar_param: MIRA_RADAR_PARAMETER = device.radar_param
        self.REG_DEF = BGT_REG.STAT0_REG

    @property
    def SH_IDX(self):
        return self._SH_IDX

    @SH_IDX.setter
    def SH_IDX(self, value):
        self._SH_IDX = value
        set_reg_val(self)

    @property
    def CH_IDX(self):
        return self._CH_IDX

    @CH_IDX.setter
    def CH_IDX(self, value):
        self._CH_IDX = value
        set_reg_val(self)

    @property
    def PM(self):
        return self._PM

    @PM.setter
    def PM(self, value):
        self._PM = value
        set_reg_val(self)

    @property
    def LDO_RDY(self):
        return self._LDO_RDY

    @LDO_RDY.setter
    def LDO_RDY(self, value):
        self._LDO_RDY = value
        set_reg_val(self)

    @property
    def MADC_BGUP(self):
        return self._MADC_BGUP

    @MADC_BGUP.setter
    def MADC_BGUP(self, value):
        self._MADC_BGUP = value
        set_reg_val(self)

    @property
    def MADC_RDY(self):
        return self._MADC_RDY

    @MADC_RDY.setter
    def MADC_RDY(self, value):
        self._MADC_RDY = value
        set_reg_val(self)

    @property
    def SADC_RDY(self):
        return self._SADC_RDY

    @SADC_RDY.setter
    def SADC_RDY(self, value):
        self._SADC_RDY = value
        set_reg_val(self)

    def convert_all_values(self):
        pass
        
    @property
    def CONTENT(self):
        return build_content(self)
    
    @property
    def CONVERT(self):
        return self.convert_all_values()


# ==============================================================================
# Class Name: BGT_SADC_RESULT
# ==============================================================================
class BGT_SADC_RESULT:
    def __init__(self, device):
        self._SADC_RAW = None
        self._SADC_BUSY = None
        self._SADC_RESULT = None
        
        self.usb_spi_bridge: MIRA_USB_SPI_BRIDGE = device.mira_bridge
        self.radar_param: MIRA_RADAR_PARAMETER = device.radar_param
        self.REG_DEF = BGT_REG.SADC_RESULT_REG
        
    @property
    def SADC_RAW(self):
        return self._SADC_RAW

    @SADC_RAW.setter
    def SADC_RAW(self, value):
        self._SADC_RAW = value
        set_reg_val(self)

    @property
    def SADC_BUSY(self):
        return self._SADC_BUSY

    @SADC_BUSY.setter
    def SADC_BUSY(self, value):
        self._SADC_BUSY = value
        set_reg_val(self)

    @property
    def SADC_RESULT(self):
        return self._SADC_RESULT

    @SADC_RESULT.setter
    def SADC_RESULT(self, value):
        self._SADC_RESULT = value
        set_reg_val(self)
        
    def convert_all_values(self):
        pass
        
    @property
    def CONTENT(self):
        return build_content(self)
    
    @property
    def CONVERT(self):
        return self.convert_all_values()
        

# ==============================================================================
# Class Name: BGT_FSTAT
# ==============================================================================
class BGT_FSTAT:
    def __init__(self, device):
        self._FOF_ERR = None
        self._FULL = None
        self._CREF = None
        self._EMPTY = None
        self._FUF_ERR = None
        self._BURST_ERR = None
        self._CLK_NUM_ERR = None
        self._FILL_STATUS = None
        
        self.usb_spi_bridge: MIRA_USB_SPI_BRIDGE = device.mira_bridge
        self.radar_param: MIRA_RADAR_PARAMETER = device.radar_param
        self.REG_DEF = BGT_REG.FSTAT_REG

    @property
    def FOF_ERR(self):
        return self._FOF_ERR

    @FOF_ERR.setter
    def FOF_ERR(self, value):
        self._FOF_ERR = value

    @property
    def FULL(self):
        return self._FULL

    @FULL.setter
    def FULL(self, value):
        self._FULL = value

    @property
    def CREF(self):
        return self._CREF

    @CREF.setter
    def CREF(self, value):
        self._CREF = value
        
    @property
    def EMPTY(self):
        return self._EMPTY

    @EMPTY.setter
    def EMPTY(self, value):
        self._EMPTY = value

    @property
    def FUF_ERR(self):
        return self._FUF_ERR

    @FUF_ERR.setter
    def FUF_ERR(self, value):
        self._FUF_ERR = value

    @property
    def BURST_ERR(self):
        return self._BURST_ERR

    @BURST_ERR.setter
    def BURST_ERR(self, value):
        self._BURST_ERR = value

    @property
    def CLK_NUM_ERR(self):
        return self._CLK_NUM_ERR

    @CLK_NUM_ERR.setter
    def CLK_NUM_ERR(self, value):
        self._CLK_NUM_ERR = value

    @property
    def FILL_STATUS(self):
        return self._FILL_STATUS

    @FILL_STATUS.setter
    def FILL_STATUS(self, value):
        self._FILL_STATUS = value

    def convert_all_values(self):
        pass
        
    @property
    def CONTENT(self):
        return build_content(self)
    
    @property
    def CONVERT(self):
        return self.convert_all_values()
        

# ==============================================================================
# Class Name: BGT_CHIP_ID_1
# ==============================================================================
class BGT_CHIP_ID_1:
    def __init__(self, device):
        self._CHIP_ID_1 = None
        
        self.usb_spi_bridge: MIRA_USB_SPI_BRIDGE = device.mira_bridge
        self.radar_param: MIRA_RADAR_PARAMETER = device.radar_param
        self.REG_DEF = BGT_REG.CHIP_ID_1_REG

    @property
    def CHIP_ID_1(self):
        return self._CHIP_ID_1

    @CHIP_ID_1.setter
    def CHIP_ID_1(self, value):
        self._CHIP_ID_1 = value

    def convert_all_values(self):
        pass
        
    @property
    def CONTENT(self):
        return build_content(self)
    
    @property
    def CONVERT(self):
        return self.convert_all_values()
    
# ==============================================================================
# Class Name: BGT_CHIP_ID_2
# ==============================================================================
class BGT_CHIP_ID_2:
    def __init__(self, device):
        self._CHIP_ID_2 = None
        
        self.usb_spi_bridge: MIRA_USB_SPI_BRIDGE = device.mira_bridge
        self.radar_param: MIRA_RADAR_PARAMETER = device.radar_param
        self.REG_DEF = BGT_REG.CHIP_ID_2_REG

    @property
    def CHIP_ID_2(self):
        return self._CHIP_ID_2

    @CHIP_ID_2.setter
    def CHIP_ID_2(self, value):
        self._CHIP_ID_2 = value

    def convert_all_values(self):
        pass
        
    @property
    def CONTENT(self):
        return build_content(self)
    
    @property
    def CONVERT(self):
        return self.convert_all_values()
