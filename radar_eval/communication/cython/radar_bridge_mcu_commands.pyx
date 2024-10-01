from libc.stdint cimport uint8_t

cdef class SYRA_MCU_COMMANDS:
    cdef public uint8_t read_cmd
    cdef public uint8_t write_cmd
    cdef public uint8_t flash_cmd
    cdef public uint8_t read_n_cmd
    cdef public uint8_t stm_rst_cmd
    cdef public uint8_t init_bgt_cmd
    cdef public uint8_t bgt_reset_cmd
    cdef public uint8_t bgt_on_hold_cmd
    cdef public uint8_t bgt_chip_id_cmd
    cdef public uint8_t set_fifo_cref_cmd
    cdef public uint8_t init_finished_cmd
    cdef public uint8_t set_dummy_cycles_cmd
    cdef public uint8_t set_fifo_overhead_cmd

    def __init__(self):
        self.read_cmd = 0x22
        self.write_cmd = 0x44
        self.flash_cmd = 0xCC
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

cdef class SYRA_MCU_USB_DEF:
    cdef public uint8_t get_chip_id_rx_len
    cdef public uint8_t spi_read_reg_cmd_len

    def __init__(self):
        self.get_chip_id_rx_len = 8
        self.spi_read_reg_cmd_len = 4
