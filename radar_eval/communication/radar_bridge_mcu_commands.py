# ==============================================================================
# Class Name: MIRA_MCU_COMMANDS
# ==============================================================================
class MIRA_MCU_COMMANDS():
    def __init__(self) -> None:
        self.read_cmd = 0x22
        self.flash_cmd = 0xCC
        self.write_cmd = 0x44
        self.read_n_cmd = 0x33
        self.stm_rst_cmd = 0xEE
        self.init_bgt_cmd = 0x11
        self.bgt_reset_cmd = 0xFF
        self.bgt_on_hold_cmd = 0xA1
        self.bgt_chip_id_cmd = 0xBB
        self.set_fifo_cref_cmd = 0xA0
        self.init_finished_cmd = 0xAA
        self.set_dummy_cycles_cmd = 0x0A
        self.set_fifo_overhead_cmd = 0x1A

class MIRA_MCU_USB_DEF():
    def __init__(self) -> None:
        self.get_chip_id_rx_len = 8
        self.spi_read_reg_cmd_len = 4