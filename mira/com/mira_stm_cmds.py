# ==============================================================================
# Class Name: MIRA_STM_COMMANDS
# ==============================================================================
class MIRA_STM_COMMANDS():
    def __init__(self) -> None:
        self.read_cmd = 0x22
        self.write_cmd = 0x44
        self.read_n_cmd = 0x33
        self.stm_rst_cmd = 0xEE
        self.init_bgt_cmd = 0x11
        self.bgt_reset_cmd = 0xFF
        self.bgt_on_hold_cmd = 0xA1
        self.init_finished_cmd = 0xAA
        self.set_fifo_cref_cmd = 0xA0
        self.set_dummy_cycles_cmd = 0x0A
        self.set_fifo_overhead_cmd = 0x1A
        