


class BGT60UTR11AIP_MAIN:
    def __init__(self, device):
        self._LDO_MODE = None 
        self._LOAD_STRENGTH = None 
        self._MADC_BG_CLK_DIV = None 
        self._CW_MODE = None  
        self._SPI_BC_MODE = None
        self._PU_IRQ_EN = None
        self._PU_CSN_EN = None
        self._PU_CLK_EN = None
        self._PU_DI_EN = None
        self._PU_DO_EN = None
        self._PU_RST_EN = None
        self._FIFO_RESET = None
        self._FSM_RESET = None 
        self._SW_RESET = None  
        self._FRAME_START = None
        
        self.usb_spi_bridge = device.mira_bridge
        self.radar_param = device.radar_param
        self.REG_DEF = BGT_REG.MAIN_REG  # Ensure BGT_REG.MAIN_REG is defined elsewhere
    
    @property
    def LDO_MODE(self):
        return self._LDO_MODE

    @LDO_MODE.setter
    def LDO_MODE(self, value):
        self._LDO_MODE = value
        self.set_reg_val()

    @property
    def LOAD_STRENGTH(self):
        return self._LOAD_STRENGTH

    @LOAD_STRENGTH.setter
    def LOAD_STRENGTH(self, value):
        self._LOAD_STRENGTH = value
        self.set_reg_val()

    @property
    def MADC_BG_CLK_DIV(self):
        return self._MADC_BG_CLK_DIV

    @MADC_BG_CLK_DIV.setter
    def MADC_BG_CLK_DIV(self, value):
        self._MADC_BG_CLK_DIV = value
        self.set_reg_val()

    @property
    def CW_MODE(self):
        return self._CW_MODE

    @CW_MODE.setter
    def CW_MODE(self, value):
        self._CW_MODE = value
        self.set_reg_val()

    @property
    def SPI_BC_MODE(self):
        return self._SPI_BC_MODE

    @SPI_BC_MODE.setter
    def SPI_BC_MODE(self, value):
        self._SPI_BC_MODE = value
        self.set_reg_val()

    @property
    def PU_IRQ_EN(self):
        return self._PU_IRQ_EN

    @PU_IRQ_EN.setter
    def PU_IRQ_EN(self, value):
        self._PU_IRQ_EN = value
        self.set_reg_val()

    @property
    def PU_CSN_EN(self):
        return self._PU_CSN_EN

    @PU_CSN_EN.setter
    def PU_CSN_EN(self, value):
        self._PU_CSN_EN = value
        self.set_reg_val()

    @property
    def PU_CLK_EN(self):
        return self._PU_CLK_EN

    @PU_CLK_EN.setter
    def PU_CLK_EN(self, value):
        self._PU_CLK_EN = value
        self.set_reg_val()

    @property
    def PU_DI_EN(self):
        return self._PU_DI_EN

    @PU_DI_EN.setter
    def PU_DI_EN(self, value):
        self._PU_DI_EN = value
        self.set_reg_val()

    @property
    def PU_DO_EN(self):
        return self._PU_DO_EN

    @PU_DO_EN.setter
    def PU_DO_EN(self, value):
        self._PU_DO_EN = value
        self.set_reg_val()

    @property
    def PU_RST_EN(self):
        return self._PU_RST_EN

    @PU_RST_EN.setter
    def PU_RST_EN(self, value):
        self._PU_RST_EN = value
        self.set_reg_val()

    @property
    def FIFO_RESET(self):
        return self._FIFO_RESET

    @FIFO_RESET.setter
    def FIFO_RESET(self, value):
        self._FIFO_RESET = value
        self.set_reg_val()

    @property
    def FSM_RESET(self):
        return self._FSM_RESET

    @FSM_RESET.setter
    def FSM_RESET(self, value):
        self._FSM_RESET = value
        self.set_reg_val()
        self._FSM_RESET = 0

    @property
    def SW_RESET(self):
        return self._SW_RESET

    @SW_RESET.setter
    def SW_RESET(self, value):
        self._SW_RESET = value
        self.set_reg_val()
        self._SW_RESET = 0
        
    @property
    def FRAME_START(self):
        return self._FRAME_START

    @FRAME_START.setter
    def FRAME_START(self, value):
        self._FRAME_START = value
        self.set_reg_val()
        self._FRAME_START = 0

    @property
    def CONTENT(self):
        return self.build_content()
    
    @property
    def CONVERT(self):
        return self.convert_all_values()
    