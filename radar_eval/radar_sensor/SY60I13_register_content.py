class BGT60TR13C_MAIN:
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
        
        self.usb_spi_bridge = device.mira_bridge
        self.radar_param = device.radar_param
        self.REG_DEF = BGT_REG.MAIN_REG
    
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
    def SADC_BG_CLK_DIV(self):
        return self._SADC_BG_CLK_DIV

    @SADC_BG_CLK_DIV.setter
    def SADC_BG_CLK_DIV(self, value):
        self._SADC_BG_CLK_DIV = value
        self.set_reg_val()

    @property
    def CW_MODE(self):
        return self._CW_MODE

    @CW_MODE.setter
    def CW_MODE(self, value):
        self._CW_MODE = value
        self.set_reg_val()

    @property
    def TR_WKUP_MUL(self):
        return self._TR_WKUP_MUL

    @TR_WKUP_MUL.setter
    def TR_WKUP_MUL(self, value):
        self._TR_WKUP_MUL = value
        self.set_reg_val()

    @property
    def TR_WKUP(self):
        return self._TR_WKUP

    @TR_WKUP.setter
    def TR_WKUP(self, value):
        self._TR_WKUP = value
        self.set_reg_val()
        self.get_wakeup_time()
        
    def get_wakeup_time(self):
        self.radar_param.sys.t_wkup = (self._TR_WKUP * 2**self._TR_WKUP_MUL * 8 + self._TR_WKUP_MUL + 3) * (1/80e6)
        
    def calculate_wakeup_registers(self, target_t_wu=1e-3, tsys_clk=1/80e6):
        min_error = float('inf')
        best_tr_wkup_mul = None
        best_tr_wkup = None
        for tr_wkup_mul in range(16):
            for tr_wkup in range(1, 256):
                calculated_t_wu = (tr_wkup * 2**tr_wkup_mul * 8 + tr_wkup_mul + 3) * tsys_clk
                error = abs(calculated_t_wu - target_t_wu)
                if error < min_error:
                    min_error = error
                    best_tr_wkup_mul = tr_wkup_mul
                    best_tr_wkup = tr_wkup
        self._TR_WKUP_MUL = best_tr_wkup_mul
        self._TR_WKUP = best_tr_wkup
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
        
    def convert_all_values(self):
        self.get_wakeup_time()
        
    @property
    def CONTENT(self):
        return self.build_content()
    
    @property
    def CONVERT(self):
        return self.convert_all_values()
    
    
    