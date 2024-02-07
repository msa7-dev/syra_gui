import __init__
from enum import IntEnum

"""
    File Name: mira6024_reg_def.py
    Author: Sykno GmbH
    Device: MiRa6024|1A
"""

"""
    BGT60ATR24C MIMO Radar Sensor
    
    Register Class Definitions:
    class BGT_REG(IntEnum):
        BGT_REG = Int
        FIELD_ID = Int
        FIELD_POS = Int
        FIELD_MSK = Int
        FIELD_SET = Int
        FIELD_RST = Int
"""

# ==============================================================================
# Class Name: BGT60ATR24C Register: MAIN_REG
# ==============================================================================
class MAIN_REG(IntEnum):
    MAIN_ADR = 0x00

    FRAME_START_ID = 0x101
    FRAME_START_POS = 0
    FRAME_START_MSK = 0x000001
    FRAME_START_SET = 1
    FRAME_START_RST = 0

    SW_RESET_ID = 0x102
    SW_RESET_POS = 1
    SW_RESET_MSK = 0x000002
    SW_RESET_SET = 1
    SW_RESET_RST = 0

    FSM_RESET_ID = 0x103
    FSM_RESET_POS = 2
    FSM_RESET_MSK = 0x000004
    FSM_RESET_SET = 1
    FSM_RESET_RST = 0

    FIFO_RESET_ID = 0x104
    FIFO_RESET_POS = 3
    FIFO_RESET_MSK = 0x000008
    FIFO_RESET_SET = 1
    FIFO_RESET_RST = 0

    RESET_ID = 0x105
    RESET_POS = 1
    RESET_MSK = 0x00000e
    RESET_SET = 0b111
    RESET_RST = 0b000

    TR_WKUP_ID = 0x106
    TR_WKUP_POS = 4
    TR_WKUP_MSK = 0x000ff0
    TR_WKUP_SET = 1
    TR_WKUP_RST = 0

    TR_WKUP_MUL_ID = 0x107
    TR_WKUP_MUL_POS = 12
    TR_WKUP_MUL_MSK = 0x00f000
    TR_WKUP_MUL_SET = 1
    TR_WKUP_MUL_RST = 0

    CW_MODE_ID = 0x108
    CW_MODE_POS = 16
    CW_MODE_MSK = 0x010000
    CW_MODE_SET = 1
    CW_MODE_RST = 0

    SADC_BG_CLK_DIV_ID = 0x109
    SADC_BG_CLK_DIV_POS = 17
    SADC_BG_CLK_DIV_MSK = 0x060000
    SADC_BG_CLK_DIV_SET = 1
    SADC_BG_CLK_DIV_RST = 3

    MADC_BG_CLK_DIV_ID = 0x10a
    MADC_BG_CLK_DIV_POS = 19
    MADC_BG_CLK_DIV_MSK = 0x180000
    MADC_BG_CLK_DIV_SET = 1
    MADC_BG_CLK_DIV_RST = 3

    LOAD_STRENGTH_ID = 0x10b
    LOAD_STRENGTH_POS = 21
    LOAD_STRENGTH_MSK = 0x600000
    LOAD_STRENGTH_SET = 1
    LOAD_STRENGTH_RST = 0

    LDO_MODE_ID = 0x10c
    LDO_MODE_POS = 23
    LDO_MODE_MSK = 0x800000
    LDO_MODE_SET = 1
    LDO_MODE_RST = 0


# ==============================================================================
# Class Name: BGT60ATR24C Register: ADC0_REG
# ==============================================================================
class ADC0_REG(IntEnum):
    ADC0_ADR = 0x01

    ADC_OVERS_CFG_ID = 0x111
    ADC_OVERS_CFG_POS = 0
    ADC_OVERS_CFG_MSK = 0x000003
    ADC_OVERS_CFG_SET = 00
    ADC_OVERS_CFG_RST = 0

    BG_TC_TRIM_ID = 0x112
    BG_TC_TRIM_POS = 2
    BG_TC_TRIM_MSK = 0x00001c
    BG_TC_TRIM_SET = 1
    BG_TC_TRIM_RST = 0

    BG_CHOP_EN_ID = 0x113
    BG_CHOP_EN_POS = 5
    BG_CHOP_EN_MSK = 0x000050
    BG_CHOP_EN_SET = 1
    BG_CHOP_EN_RST = 0

    STC_ID = 0x114
    STC_POS = 6
    STC_MSK = 0x0000c0
    STC_SET = 0
    STC_RST = 1

    DSCAL_ID = 0x115
    DSCAL_POS = 8
    DSCAL_MSK = 0x000100
    DSCAL_SET = 1
    DSCAL_RST = 0

    TRACK_CFG_ID = 0x116
    TRACK_CFG_POS = 9
    TRACK_CFG_MSK = 0x000600
    TRACK_CFG_SET = 2
    TRACK_CFG_RST = 1

    MSB_CTRL_ID = 0x117
    MSB_CTRL_POS = 11
    MSB_CTRL_MSK = 0x000800
    MSB_CTRL_SET = 1
    MSB_CTRL_RST = 0

    TRIG_MADC_ID = 0x118
    TRIG_MADC_POS = 12
    TRIG_MADC_MSK = 0x001000
    TRIG_MADC_SET = 1
    TRIG_MADC_RST = 0

    ADC_DIV_ID = 0x119
    ADC_DIV_POS = 14
    ADC_DIV_MSK = 0xffc000
    ADC_DIV_SET = 33
    ADC_DIV_RST = 40

# ==============================================================================
# Class Name: BGT60ATR24C Register: CHIP_VERSION_REG
# ==============================================================================
class CHIP_VERSION_REG(IntEnum):
    CHIP_VERSION_ADR = 0x02

    RF_ID_ID = 0x121
    RF_ID_POS = 0
    RF_ID_MSK = 0x0000ff
    RF_ID_SET = 0x00
    RF_ID_RST = 0x00

    DIGITAL_ID_ID = 0x122
    DIGITAL_ID_POS = 8
    DIGITAL_ID_MSK = 0xffff00
    DIGITAL_ID_SET = 0x00
    DIGITAL_ID_RST = 0x00


# ==============================================================================
# Class Name: BGT60ATR24C Register: STAT1_REG
# ==============================================================================
class STAT1_REG(IntEnum):
    STAT1_ADR = 0x03

    SHAPE_GRP_CNT_ID = 0x131
    SHAPE_GRP_CNT_POS = 0
    SHAPE_GRP_CNT_MSK = 0x000fff
    SHAPE_GRP_CNT_SET = 0x00
    SHAPE_GRP_CNT_RST = 0x00

    FRAME_CNT_ID = 0x132
    FRAME_CNT_POS = 12
    FRAME_CNT_MSK = 0xfff000
    FRAME_CNT_SET = 0x00
    FRAME_CNT_RST = 0x00


# ==============================================================================
# Class Name: BGT60ATR24C Register: PACR1_REG
# ==============================================================================
class PACR1_REG(IntEnum):
    PACR1_ADR = 0x04

    ANAPON_ID = 0x140
    ANAPON_POS = 0
    ANAPON_MSK = 0x000001
    ANAPON_SET = 1
    ANAPON_RST = 0

    VANAREG_ID = 0x141
    VANAREG_POS = 1
    VANAREG_MSK = 0x000006
    VANAREG_SET = 2
    VANAREG_RST = 2

    DIGPON_ID = 0x142
    DIGPON_POS = 3
    DIGPON_MSK = 0x000008
    DIGPON_SET = 1
    DIGPON_RST = 0

    VDIGREG_ID = 0x143
    VDIGREG_POS = 4
    VDIGREG_MSK = 0x000030
    VDIGREG_SET = 2
    VDIGREG_RST = 2

    BGAPEN_ID = 0x144
    BGAPEN_POS = 6
    BGAPEN_MSK = 0x000040
    BGAPEN_SET = 1
    BGAPEN_RST = 0

    U2IEN_ID = 0x145
    U2IEN_POS = 7
    U2IEN_MSK = 0x000080
    U2IEN_SET = 1
    U2IEN_RST = 0

    VREFSEL_ID = 0x146
    VREFSEL_POS = 8
    VREFSEL_MSK = 0x000300
    VREFSEL_SET = 1
    VREFSEL_RST = 1

    RFILTSEL_ID = 0x147
    RFILTSEL_POS = 10
    RFILTSEL_MSK = 0x000400
    RFILTSEL_SET = 0
    RFILTSEL_RST = 1

    RLFSEL_ID = 0x148
    RLFSEL_POS = 11
    RLFSEL_MSK = 0x000800
    RLFSEL_SET = 1
    RLFSEL_RST = 0

    LOCKSEL_ID = 0x149
    LOCKSEL_POS = 13
    LOCKSEL_MSK = 0x00e000
    LOCKSEL_SET = 3
    LOCKSEL_RST = 3

    LOCKFORC_ID = 0x14a
    LOCKFORC_POS = 16
    LOCKFORC_MSK = 0x010000
    LOCKFORC_SET = 0
    LOCKFORC_RST = 1

    ICPSEL_ID = 0x14b
    ICPSEL_POS = 17
    ICPSEL_MSK = 0x0e0000
    ICPSEL_SET = 4
    ICPSEL_RST = 4

    BIASFORC_ID = 0x14c
    BIASFORC_POS = 20
    BIASFORC_MSK = 0x100000
    BIASFORC_SET = 1
    BIASFORC_RST = 0

    CPEN_ID = 0x14d
    CPEN_POS = 21
    CPEN_MSK = 0x200000
    CPEN_SET = 1
    CPEN_RST = 0

    LFEN_ID = 0x14e
    LFEN_POS = 22
    LFEN_MSK = 0x400000
    LFEN_SET = 1
    LFEN_RST = 0

    OSCCLKEN_ID = 0x14f
    OSCCLKEN_POS = 23
    OSCCLKEN_MSK = 0x800000
    OSCCLKEN_SET = 1
    OSCCLKEN_RST = 0


# ==============================================================================
# Class Name: BGT60ATR24C Register: PACR2_REG
# ==============================================================================
class PACR2_REG(IntEnum):
    PACR2_ADR = 0x05

    DIVSET_ID = 0x151
    DIVSET_POS = 0
    DIVSET_MSK = 0x00001f
    DIVSET_SET = 20
    DIVSET_RST = 20

    DIVEN_ID = 0x152
    DIVEN_POS = 5
    DIVEN_MSK = 0x000020
    DIVEN_SET = 1
    DIVEN_RST = 0

    FSTDNEN_ID = 0x153
    FSTDNEN_POS = 6
    FSTDNEN_MSK = 0x0000c0
    FSTDNEN_SET = 0
    FSTDNEN_RST = 0

    FSDNTMR_ID = 0x154
    FSDNTMR_POS = 8
    FSDNTMR_MSK = 0x01ff00
    FSDNTMR_SET = 0
    FSDNTMR_RST = 0

    TRIVREG_ID = 0x155
    TRIVREG_POS = 17
    TRIVREG_MSK = 0x020000
    TRIVREG_SET = 1
    TRIVREG_RST = 0

    DTSEL_ID = 0x156
    DTSEL_POS = 18
    DTSEL_MSK = 0x0c0000
    DTSEL_SET = 1
    DTSEL_RST = 1


# ==============================================================================
# Class Name: BGT60ATR24C Register: SFCTL_REG
# ==============================================================================
class SFCTL_REG(IntEnum):
    SFCTL_ADR = 0x06

    FIFO_CREF_ID = 0x161
    FIFO_CREF_POS = 0
    FIFO_CREF_MSK = 0x001fff
    FIFO_CREF_SET = 0x1000
    FIFO_CREF_RST = 0x0000

    FIFO_LP_MODE_ID = 0x162
    FIFO_LP_MODE_POS = 13
    FIFO_LP_MODE_MSK = 0x002000
    FIFO_LP_MODE_SET = 1
    FIFO_LP_MODE_RST = 0

    MISO_HS_RD_ID = 0x163
    MISO_HS_RD_POS = 16
    MISO_HS_RD_MSK = 0x010000
    MISO_HS_RD_SET = 1
    MISO_HS_RD_RST = 0

    LFSR_EN_ID = 0x164
    LFSR_EN_POS = 17
    LFSR_EN_MSK = 0x020000
    LFSR_EN_SET = 1
    LFSR_EN_RST = 0

    PREFIX_EN_ID = 0x165
    PREFIX_EN_POS = 18
    PREFIX_EN_MSK = 0x040000
    PREFIX_EN_SET = 1
    PREFIX_EN_RST = 0

    QSPI_WT_ID = 0x166
    QSPI_WT_POS = 20
    QSPI_WT_MSK = 0xf00000
    QSPI_WT_SET = 3
    QSPI_WT_RST = 7

# ==============================================================================
# Class Name: BGT60ATR24C Register: SADC_CTRL_REG
# ==============================================================================
class SADC_CTRL_REG(IntEnum):
    SADC_CTRL_ADR = 0x07

    SADC_CHSEL_ID = 0x171
    SADC_CHSEL_POS = 0
    SADC_CHSEL_MSK = 0x00000F
    SADC_CHSEL_SET = 0
    SADC_CHSEL_RST = 0

    SADC_START_ID = 0x172
    SADC_START_POS = 4
    SADC_START_MSK = 0x000010
    SADC_START_SET = 1
    SADC_START_RST = 0x00

    SADC_CLK_DIV_ID = 0x173
    SADC_CLK_DIV_POS = 6
    SADC_CLK_DIV_MSK = 0x0000c0
    SADC_CLK_DIV_SET = 2
    SADC_CLK_DIV_RST = 3

    SD_EN_ID = 0x174
    SD_EN_POS = 8
    SD_EN_MSK = 0x000100
    SD_EN_SET = 1
    SD_EN_RST = 0

    OVERS_CFG_ID = 0x175
    OVERS_CFG_POS = 9
    OVERS_CFG_MSK = 0x000600
    OVERS_CFG_SET = 0
    OVERS_CFG_RST = 0

    SESP_ID = 0x176
    SESP_POS = 11
    SESP_MSK = 0x000800
    SESP_SET = 1
    SESP_RST = 0

    LVGAIN_ID = 0x177
    LVGAIN_POS = 12
    LVGAIN_MSK = 0x001000
    LVGAIN_SET = 1
    LVGAIN_RST = 0

    DSCAL_ID = 0x178
    DSCAL_POS = 13
    DSCAL_MSK = 0x002000
    DSCAL_SET = 1
    DSCAL_RST = 0

    TC_TRIM_ID = 0x179
    TC_TRIM_POS = 14
    TC_TRIM_MSK = 0x01c000
    TC_TRIM_SET = 0
    TC_TRIM_RST = 0

# ==============================================================================
# Class Name: BGT60ATR24C Register: CSX_0_REG
# ==============================================================================
class CSX_0_REG(IntEnum):
    CSI_0_ADR = 0x08
    CSDS_0_ADR = 0x0C
    CSU1_0_ADR = 0x10
    CSD1_0_ADR = 0x13
    CSU2_0_ADR = 0x17
    CSD2_0_ADR = 0x1A
    CSU3_0_ADR = 0x1E
    CSD3_0_ADR = 0x21
    CSU4_0_ADR = 0x25
    CSD4_0_ADR = 0x28

    TX1_EN_ID = 0x181
    TX1_EN_POS = 0
    TX1_EN_MSK = 0x000001
    TX1_EN_SET = 1
    TX1_EN_RST = 0

    PD1_EN_ID = 0x182
    PD1_EN_POS = 1
    PD1_EN_MSK = 0x000002
    PD1_EN_SET = 1
    PD1_EN_RST = 0

    TX2_EN_ID = 0x183
    TX2_EN_POS = 2
    TX2_EN_MSK = 0x000004
    TX2_EN_SET = 1
    TX2_EN_RST = 0

    PD2_EN_ID = 0x184
    PD2_EN_POS = 3
    PD2_EN_MSK = 0x000008
    PD2_EN_SET = 1
    PD2_EN_RST = 0

    VCO_EN_ID = 0x185
    VCO_EN_POS = 4
    VCO_EN_MSK = 0x000010
    VCO_EN_SET = 1
    VCO_EN_RST = 0

    TEST_DIV_EN_ID = 0x186
    TEST_DIV_EN_POS = 5
    TEST_DIV_EN_MSK = 0x000020
    TEST_DIV_EN_SET = 1
    TEST_DIV_EN_RST = 0

    FDIV_EN_ID = 0x187
    FDIV_EN_POS = 6
    FDIV_EN_MSK = 0x000040
    FDIV_EN_SET = 1
    FDIV_EN_RST = 0

    LO_DIST2_EN_ID = 0x188
    LO_DIST2_EN_POS = 10
    LO_DIST2_EN_MSK = 0x000400
    LO_DIST2_EN_SET = 1
    LO_DIST2_EN_RST = 0

    LO_DIST1_EN_ID = 0x189
    LO_DIST1_EN_POS = 11
    LO_DIST1_EN_MSK = 0x000800
    LO_DIST1_EN_SET = 1
    LO_DIST1_EN_RST = 0

    RX1LOBUF_EN_ID = 0x18a
    RX1LOBUF_EN_POS = 12
    RX1LOBUF_EN_MSK = 0x001000
    RX1LOBUF_EN_SET = 1
    RX1LOBUF_EN_RST = 0

    RX1MIX_EN_ID = 0x18b
    RX1MIX_EN_POS = 13
    RX1MIX_EN_MSK = 0x002000
    RX1MIX_EN_SET = 1
    RX1MIX_EN_RST = 0

    RX2LOBUF_EN_ID = 0x18c
    RX2LOBUF_EN_POS = 14
    RX2LOBUF_EN_MSK = 0x004000
    RX2LOBUF_EN_SET = 1
    RX2LOBUF_EN_RST = 0

    RX2MIX_EN_ID = 0x18d
    RX2MIX_EN_POS = 15
    RX2MIX_EN_MSK = 0x008000
    RX2MIX_EN_SET = 1
    RX2MIX_EN_RST = 0

    RX3LOBUF_EN_ID = 0x18e
    RX3LOBUF_EN_POS = 16
    RX3LOBUF_EN_MSK = 0x010000
    RX3LOBUF_EN_SET = 1
    RX3LOBUF_EN_RST = 0

    RX3MIX_EN_ID = 0x18f
    RX3MIX_EN_POS = 17
    RX3MIX_EN_MSK = 0x020000
    RX3MIX_EN_SET = 1
    RX3MIX_EN_RST = 0

    RX4LOBUF_EN_ID = 0x281
    RX4LOBUF_EN_POS = 18
    RX4LOBUF_EN_MSK = 0x040000
    RX4LOBUF_EN_SET = 1
    RX4LOBUF_EN_RST = 0

    RX4MIX_EN_ID = 0x281
    RX4MIX_EN_POS = 19
    RX4MIX_EN_MSK = 0x080000
    RX4MIX_EN_SET = 1
    RX4MIX_EN_RST = 0

    BBCHGLOB_EN_ID = 0x282
    BBCHGLOB_EN_POS = 20
    BBCHGLOB_EN_MSK = 0x100000
    BBCHGLOB_EN_SET = 1
    BBCHGLOB_EN_RST = 0

# ==============================================================================
# Class Name: BGT60ATR24C Register: CSX_1_REG
# ==============================================================================
class CSX_1_REG(IntEnum):
    CSI_1_ADR = 0x09
    CSDS_1_ADR = 0x0D
    CSU1_1_ADR = 0x11
    CSD1_1_ADR = 0x14
    CSU2_1_ADR = 0x18
    CSD2_1_ADR = 0x1B
    CSU3_1_ADR = 0x1F
    CSD3_1_ADR = 0x22
    CSU4_1_ADR = 0x26
    CSD4_1_ADR = 0x29

    TX1_DAC_ID = 0x191
    TX1_DAC_POS = 0
    TX1_DAC_MSK = 0x00001f
    TX1_DAC_SET = 15
    TX1_DAC_RST = 0

    TX2_DAC_ID = 0x192
    TX2_DAC_POS = 5
    TX2_DAC_MSK = 0x0003e0
    TX2_DAC_SET = 15
    TX2_DAC_RST = 0

    MADC_EN_ID = 0x193
    MADC_EN_POS = 10
    MADC_EN_MSK = 0x000400
    MADC_EN_SET = 1
    MADC_EN_RST = 0

    TEMP_MEAS_EN_ID = 0x194
    TEMP_MEAS_EN_POS = 12
    TEMP_MEAS_EN_MSK = 0x001000
    TEMP_MEAS_EN_SET = 1
    TEMP_MEAS_EN_RST = 0

    BB_RSTCNT_ID = 0x195
    BB_RSTCNT_POS = 13
    BB_RSTCNT_MSK = 0x0fe000
    BB_RSTCNT_SET = 1
    BB_RSTCNT_RST = 0

    BBCH_SEL_ID = 0x196
    BBCH_SEL_POS = 20
    BBCH_SEL_MSK = 0xf00000
    BBCH_SEL_SET = 0x1111
    BBCH_SEL_RST = 0x0000

# ==============================================================================
# Class Name: BGT60ATR24C Register: CSX_2_REG
# ==============================================================================
class CSX_2_REG(IntEnum):
    CSI_2_ADR = 0x0A
    CSDS_2_ADR = 0x0E
    CSU1_2_ADR = 0x12
    CSD1_2_ADR = 0x15
    CSU2_2_ADR = 0x19
    CSD2_2_ADR = 0x1C
    CSU3_2_ADR = 0x20
    CSD3_2_ADR = 0x23
    CSU4_2_ADR = 0x27
    CSD4_2_ADR = 0x2A

    HPF_SEL1_ID = 0x1a2
    HPF_SEL1_POS = 0
    HPF_SEL1_MSK = 0x000003
    HPF_SEL1_SET = 3
    HPF_SEL1_RST = 0

    VGA_GAIN1_ID = 0x1a1
    VGA_GAIN1_POS = 2
    VGA_GAIN1_MSK = 0x00001c
    VGA_GAIN1_SET = 1
    VGA_GAIN1_RST = 0

    HPF_SEL2_ID = 0x1a2
    HPF_SEL2_POS = 5
    HPF_SEL2_MSK = 0x000060
    HPF_SEL2_SET = 3
    HPF_SEL2_RST = 0

    VGA_GAIN2_ID = 0x1a3
    VGA_GAIN2_POS = 7
    VGA_GAIN2_MSK = 0x000380
    VGA_GAIN2_SET = 1
    VGA_GAIN2_RST = 0

    HPF_SEL3_ID = 0x1a4
    HPF_SEL3_POS = 10
    HPF_SEL3_MSK = 0x000c00
    HPF_SEL3_SET = 3
    HPF_SEL3_RST = 0

    VGA_GAIN3_ID = 0x1a5
    VGA_GAIN3_POS = 12
    VGA_GAIN3_MSK = 0x007000
    VGA_GAIN3_SET = 1
    VGA_GAIN3_RST = 0

    HPF_SEL4_ID = 0x1a6
    HPF_SEL4_POS = 15
    HPF_SEL4_MSK = 0x018000
    HPF_SEL4_SET = 3
    HPF_SEL4_RST = 0

    VGA_GAIN4_ID = 0x1a7
    VGA_GAIN4_POS = 17
    VGA_GAIN4_MSK = 0x0e0000
    VGA_GAIN4_SET = 1
    VGA_GAIN4_RST = 0

    HP_GAIN_ID = 0x1a8
    HP_GAIN_POS = 20
    HP_GAIN_MSK = 0xf00000
    HP_GAIN_SET = 0x1111
    HP_GAIN_RST = 0x0000

# ==============================================================================
# Class Name: BGT60ATR24C Register: CSCX_REG
# ==============================================================================
class CSCX_REG(IntEnum):
    CSCI_ADR = 0x0B
    CSCDS_ADR = 0x0F
    CSC1_ADR = 0x16
    CSC2_ADR = 0x1D
    CSC3_ADR = 0x24
    CSC4_ADR = 0x2B

    REPC_ID = 0x381
    REPC_POS = 0
    REPC_MSK = 0x00000f
    REPC_SET = 1024
    REPC_RST = 0

    CS_EN_ID = 0x382
    CS_EN_POS = 4
    CS_EN_MSK = 0x000010
    CS_EN_SET = 1
    CS_EN_RST = 0

    ABB_ISOPD_ID = 0x383
    ABB_ISOPD_POS = 5
    ABB_ISOPD_MSK = 0x000020
    ABB_ISOPD_SET = 1
    ABB_ISOPD_RST = 0

    RF_ISOPD_ID = 0x384
    RF_ISOPD_POS = 6
    RF_ISOPD_MSK = 0x000040
    RF_ISOPD_SET = 1
    RF_ISOPD_RST = 0

    BG_EN_ID = 0x385
    BG_EN_POS = 7
    BG_EN_MSK = 0x000080
    BG_EN_SET = 1
    BG_EN_RST = 0

    MADC_ISOPD_ID = 0x386
    MADC_ISOPD_POS = 8
    MADC_ISOPD_MSK = 0x000100
    MADC_ISOPD_SET = 1
    MADC_ISOPD_RST = 0

    SADC_ISOPD_ID = 0x387
    SADC_ISOPD_POS = 9
    SADC_ISOPD_MSK = 0x000200
    SADC_ISOPD_SET = 1
    SADC_ISOPD_RST = 0

    BG_TMRF_EN_ID = 0x387
    BG_TMRF_EN_POS = 10
    BG_TMRF_EN_MSK = 0x000400
    BG_TMRF_EN_SET = 1
    BG_TMRF_EN_RST = 0

    PLL_ISOPD_ID = 0x388
    PLL_ISOPD_POS = 11
    PLL_ISOPD_MSK = 0x000800
    PLL_ISOPD_SET = 1
    PLL_ISOPD_RST = 0

# ==============================================================================
# Class Name: BGT60ATR24C Register: CCR0_REG
# ==============================================================================
class CCR0_REG(IntEnum):
    CCR0_ADR = 0x2C

    TR_END_ID = 0xb11
    TR_END_POS = 0
    TR_END_MSK = 0x0001ff
    TR_END_SET = 1
    TR_END_RST = 0

    CONT_MODE_ID = 0xb12
    CONT_MODE_POS = 9
    CONT_MODE_MSK = 0x000200
    CONT_MODE_SET = 1
    CONT_MODE_RST = 0

    REPT_ID = 0xb13
    REPT_POS = 10
    REPT_MSK = 0x003c00
    REPT_SET = 15
    REPT_RST = 0

    TR_INIT1_ID = 0xb14
    TR_INIT1_POS = 14
    TR_INIT1_MSK = 0x3fc000
    TR_INIT1_SET = 1
    TR_INIT1_RST = 0

    TR_INIT1_MUL_ID = 0xb15
    TR_INIT1_MUL_POS = 22
    TR_INIT1_MUL_MSK = 0xc00000
    TR_INIT1_MUL_SET = 1
    TR_INIT1_MUL_RST = 0

# ==============================================================================
# Class Name: BGT60ATR24C Register: CCR1_REG
# ==============================================================================
class CCR1_REG(IntEnum):
    CCR1_ADR = 0x2D

    TR_START_ID = 0x911
    TR_START_POS = 0
    TR_START_MSK = 0x0001ff
    TR_START_SET = 1
    TR_START_RST = 0

    PD_MODE_ID = 0x912
    PD_MODE_POS = 9
    PD_MODE_MSK = 0x000600
    PD_MODE_SET = 1
    PD_MODE_RST = 0

    TR_FED_ID = 0x913
    TR_FED_POS = 11
    TR_FED_MSK = 0x07f800
    TR_FED_SET = 1
    TR_FED_RST = 0

    TR_FED_MUL_ID = 0x914
    TR_FED_MUL_POS = 19
    TR_FED_MUL_MSK = 0xf80000
    TR_FED_MUL_SET = 1
    TR_FED_MUL_RST = 0

# ==============================================================================
# Class Name: BGT60ATR24C Register: CCR2_REG
# ==============================================================================
class CCR2_REG(IntEnum):
    CCR2_ADR = 0x2E

    MAX_FRAME_CNT_ID = 0xa11
    MAX_FRAME_CNT_POS = 0
    MAX_FRAME_CNT_MSK = 0x000fff
    MAX_FRAME_CNT_SET = 0xfff
    MAX_FRAME_CNT_RST = 0

    FRAME_LEN_ID = 0xa12
    FRAME_LEN_POS = 12
    FRAME_LEN_MSK = 0xfff000
    FRAME_LEN_SET = 0xfff
    FRAME_LEN_RST = 0

# ==============================================================================
# Class Name: BGT60ATR24C Register: CCR3_REG
# ==============================================================================
class CCR3_REG(IntEnum):
    CCR3_ADR = 0x2F

    TR_PAEN_ID = 0xb11
    TR_PAEN_POS = 0
    TR_PAEN_MSK = 0x0001ff
    TR_PAEN_SET = 1
    TR_PAEN_RST = 0

    TR_SSTART_ID = 0xb12
    TR_SSTART_POS = 9
    TR_SSTART_MSK = 0x003e00
    TR_SSTART_SET = 1
    TR_SSTART_RST = 0

    TR_INIT0_ID = 0xb14
    TR_INIT0_POS = 14
    TR_INIT0_MSK = 0x3fc000
    TR_INIT0_SET = 1
    TR_INIT0_RST = 0

    TR_INIT0_MUL_ID = 0xb15
    TR_INIT0_MUL_POS = 22
    TR_INIT0_MUL_MSK = 0xc00000
    TR_INIT0_MUL_SET = 1
    TR_INIT0_MUL_RST = 0

# ==============================================================================
# Class Name: BGT60ATR24C Register: PLLX_0_REG
# ==============================================================================
class PLLX_0_REG(IntEnum):
    PLL1_0_ADR = 0x30
    PLL2_0_ADR = 0x38
    PLL3_0_ADR = 0x40
    PLL4_0_ADR = 0x48

    FSU_ID = 0xb21
    FSU_POS = 0
    FSU_MSK = 0xffffff
    FSU_SET = 0xacab
    FSU_RST = 0x000000

# ==============================================================================
# Class Name: BGT60ATR24C Register: PLLX_1_REG
# ==============================================================================
class PLLX_1_REG(IntEnum):
    PLL1_1_ADR = 0x31
    PLL2_1_ADR = 0x39
    PLL3_1_ADR = 0x41
    PLL4_1_ADR = 0x49

    RSU_ID = 0xb31
    RSU_POS = 0
    RSU_MSK = 0x7fffff
    RSU_SET = 0xacab
    RSU_RST = 0x000000

# ==============================================================================
# Class Name: BGT60ATR24C Register: PLLX_2_REG
# ==============================================================================
class PLLX_2_REG(IntEnum):
    PLL1_2_ADR = 0x32
    PLL2_2_ADR = 0x3A
    PLL3_2_ADR = 0x42
    PLL4_2_ADR = 0x4A

    RTU_ID = 0xb41
    RTU_POS = 0
    RTU_MSK = 0x003fff
    RTU_SET = 0xacab
    RTU_RST = 0x000000

    TR_EDU_ID = 0xb42
    TR_EDU_POS = 16
    TR_EDU_MSK = 0xff0000
    TR_EDU_SET = 0xacab
    TR_EDU_RST = 0x000000

# ==============================================================================
# Class Name: BGT60ATR24C Register: PLLX_3_REG
# ==============================================================================
class PLLX_3_REG(IntEnum):
    PLL1_3_ADR = 0x33
    PLL2_3_ADR = 0x3B
    PLL3_3_ADR = 0x43
    PLL4_3_ADR = 0x4B

    APU_ID = 0xc11
    APU_POS = 0
    APU_MSK = 0x000fff
    APU_SET = 0xfff
    APU_RST = 0x000

    APD_ID = 0xc12
    APD_POS = 12
    APD_MSK = 0xfff000
    APD_SET = 0xfff
    APD_RST = 0x000

# ==============================================================================
# Class Name: BGT60ATR24C Register: PLLX_4_REG
# ==============================================================================
class PLLX_4_REG(IntEnum):
    PLL1_4_ADR = 0x34
    PLL2_4_ADR = 0x3C
    PLL3_4_ADR = 0x44
    PLL4_4_ADR = 0x4C

    FSD_ID = 0xb51
    FSD_POS = 0
    FSD_MSK = 0xffffff
    FSD_SET = 0xacab
    FSD_RST = 0x000000

# ==============================================================================
# Class Name: BGT60ATR24C Register: PLLX_5_REG
# ==============================================================================
class PLLX_5_REG(IntEnum):
    PLL1_5_ADR = 0x35
    PLL2_5_ADR = 0x3D
    PLL3_5_ADR = 0x45
    PLL4_5_ADR = 0x4D

    RSD_ID = 0xb61
    RSD_POS = 0
    RSD_MSK = 0x7fffff
    RSD_SET = 0xacab
    RSD_RST = 0x000000

# ==============================================================================
# Class Name: BGT60ATR24C Register: PLLX_6_REG
# ==============================================================================
class PLLX_6_REG(IntEnum):
    PLL1_6_ADR = 0x36
    PLL2_6_ADR = 0x3E
    PLL3_6_ADR = 0x46
    PLL4_6_ADR = 0x4E

    RTD_ID = 0xb71
    RTD_POS = 0
    RTD_MSK = 0x003fff
    RTD_SET = 0xacab
    RTD_RST = 0x000000

    TR_EDD_ID = 0xb82
    TR_EDD_POS = 16
    TR_EDD_MSK = 0xff0000
    TR_EDD_SET = 0xacab
    TR_EDD_RST = 0x000000

# ==============================================================================
# Class Name: BGT60ATR24C Register: PLLX_7_REG
# ==============================================================================
class PLLX_7_REG(IntEnum):
    PLL1_7_ADR = 0x37
    PLL2_7_ADR = 0x3F
    PLL3_7_ADR = 0x47
    PLL4_7_ADR = 0x4F

    REPS_ID = 0xd11
    REPS_POS = 0
    REPS_MSK = 0x00000f
    REPS_SET = 15
    REPS_RST = 0

    SH_EN_ID = 0xd12
    SH_EN_POS = 4
    SH_EN_MSK = 0x000010
    SH_EN_SET = 1
    SH_EN_RST = 0

    CONT_MODE_ID = 0xd13
    CONT_MODE_POS = 8
    CONT_MODE_MSK = 0x000100
    CONT_MODE_SET = 1
    CONT_MODE_RST = 0

    PD_MODE_ID = 0xd14
    PD_MODE_POS = 9
    PD_MODE_MSK = 0x000600
    PD_MODE_SET = 1
    PD_MODE_RST = 0

    TR_SED_ID = 0xd15
    TR_SED_POS = 11
    TR_SED_MSK = 0x07f800
    TR_SED_SET = 1
    TR_SED_RST = 0

    TR_SED_MUL_ID = 0xd16
    TR_SED_MUL_POS = 19
    TR_SED_MUL_MSK = 0xf80000
    TR_SED_MUL_SET = 1
    TR_SED_MUL_RST = 0

# ==============================================================================
# Class Name: BGT60ATR24C Register: RFT0_REG
# ==============================================================================
class RFT0_REG(IntEnum):
    RFT0_ADR = 0x55

    RFTSIGCLK_DIV_ID = 0xf11
    RFTSIGCLK_DIV_POS = 0
    RFTSIGCLK_DIV_MSK = 0x001fff
    RFTSIGCLK_DIV_SET = 0x0000
    RFTSIGCLK_DIV_RST = 0x001f40

    RFTSIGCLK_DIV_EN_ID = 0xf12
    RFTSIGCLK_DIV_EN_POS = 13
    RFTSIGCLK_DIV_EN_MSK = 0x002000
    RFTSIGCLK_DIV_EN_SET = 1
    RFTSIGCLK_DIV_EN_RST = 0

    TEST_SIG_IF1_EN_ID = 0xf13
    TEST_SIG_IF1_EN_POS = 18
    TEST_SIG_IF1_EN_MSK = 0x040000
    TEST_SIG_IF1_EN_SET = 1
    TEST_SIG_IF1_EN_RST = 0

    TEST_SIG_IF2_EN_ID = 0xf14
    TEST_SIG_IF2_EN_POS = 19
    TEST_SIG_IF2_EN_MSK = 0x080000
    TEST_SIG_IF2_EN_SET = 1
    TEST_SIG_IF2_EN_RST = 0

    TEST_SIG_IF3_EN_ID = 0xf15
    TEST_SIG_IF3_EN_POS = 20
    TEST_SIG_IF3_EN_MSK = 0x100000
    TEST_SIG_IF3_EN_SET = 1
    TEST_SIG_IF3_EN_RST = 0

    TEST_SIG_IF4_EN_ID = 0xf16
    TEST_SIG_IF4_EN_POS = 21
    TEST_SIG_IF4_EN_MSK = 0x200000
    TEST_SIG_IF4_EN_SET = 1
    TEST_SIG_IF4_EN_RST = 0

# ==============================================================================
# Class Name: BGT60ATR24C Register: DFT0_REG
# ==============================================================================
class DFT0_REG(IntEnum):
    DFT0_ADR = 0x57

    EFUSE_SENSE_ID = 0xf78
    EFUSE_SENSE_POS = 14
    EFUSE_SENSE_MSK = 0x004000
    EFUSE_SENSE_SET = 0x00
    EFUSE_SENSE_RST = 0x00

    EFUSE_EN_ID = 0xf79
    EFUSE_EN_POS = 4
    EFUSE_EN_MSK = 0x000010
    EFUSE_EN_SET = 0x00
    EFUSE_EN_RST = 0x00

# ==============================================================================
# Class Name: BGT60ATR24C Register: DFT1_REG
# ==============================================================================
class DFT1_REG(IntEnum):
    DFT1_ADR = 0x58

    EFUSE_READY_ID = 0xf80
    EFUSE_READY_POS = 9
    EFUSE_READY_MSK = 0x000200
    EFUSE_READY_SET = 0x00
    EFUSE_READY_RST = 0x00

# ==============================================================================
# Class Name: BGT60ATR24C Register: PLL_DFT0_REG
# ==============================================================================
class PLL_DFT0_REG(IntEnum):
    PLL_DFT0_ADR = 0x59

    BYPRMPEN_ID = 0xe11
    BYPRMPEN_POS = 0
    BYPRMPEN_MSK = 0x000000
    BYPRMPEN_SET = 0x00
    BYPRMPEN_RST = 0x00

    BYPSDMEN_ID = 0xe12
    BYPSDMEN_POS = 1
    BYPSDMEN_MSK = 0x0000001
    BYPSDMEN_SET = 0x00
    BYPSDMEN_RST = 0x00

    BYPSDM_ID = 0xe13
    BYPSDM_POS = 2
    BYPSDM_MSK = 0x000002
    BYPSDM_SET = 0x00
    BYPSDM_RST = 0x00

# ==============================================================================
# Class Name: BGT60ATR24C Register: STAT0_REG
# ==============================================================================
class STAT0_REG(IntEnum):
    STAT0_ADR = 0x5D

    SADC_RDY_ID = 0x1
    SADC_RDY_POS = 0
    SADC_RDY_MSK = 0x000001
    SADC_RDY_SET = 0x00
    SADC_RDY_RST = 0x00

    MADC_RDY_ID = 0x1
    MADC_RDY_POS = 1
    MADC_RDY_MSK = 0x000002
    MADC_RDY_SET = 0x00
    MADC_RDY_RST = 0x00

    MADC_BGUP_ID = 0x1
    MADC_BGUP_POS = 2
    MADC_BGUP_MSK = 0x000004
    MADC_BGUP_SET = 0x00
    MADC_BGUP_RST = 0x00

    LDO_RDY_ID = 0x1
    LDO_RDY_POS = 3
    LDO_RDY_MSK = 0x000008
    LDO_RDY_SET = 0x00
    LDO_RDY_RST = 0x00

    PM_ID = 0x1
    PM_POS = 5
    PM_MSK = 0x0000e0
    PM_SET = 0x00
    PM_RST = 0x00

    CH_IDX_ID = 0x1
    CH_IDX_POS = 8
    CH_IDX_MSK = 0x000700
    CH_IDX_SET = 0x00
    CH_IDX_RST = 0x00

    SH_IDX_ID = 0x1
    SH_IDX_POS = 11
    SH_IDX_MSK = 0x003800
    SH_IDX_SET = 0x00
    SH_IDX_RST = 0x00

# ==============================================================================
# Class Name: BGT60ATR24C Register: SADC_RESULT_REG
# ==============================================================================
class SADC_RESULT_REG(IntEnum):
    SADC_RESULT_ADR = 0x5E

    SADC_RESULT_ID = 0x1
    SADC_RESULT_POS = 0
    SADC_RESULT_MSK = 0x0003ff
    SADC_RESULT_SET = 0x00
    SADC_RESULT_RST = 0x00

    SADC_BUSY_ID = 0x1
    SADC_BUSY_POS = 10
    SADC_BUSY_MSK = 0x000400
    SADC_BUSY_SET = 0x00
    SADC_BUSY_RST = 0x00

    SADC_RAW_ID = 0x1
    SADC_RAW_POS = 12
    SADC_RAW_MSK = 0x3ff000
    SADC_RAW_SET = 0x00
    SADC_RAW_RST = 0x00

# ==============================================================================
# Class Name: BGT60ATR24C Register: FSTAT_REG
# ==============================================================================
class FSTAT_REG(IntEnum):
    FSTAT_ADR = 0x5F
    FILL_STATUS_ID = 0x1
    FILL_STATUS_POS = 0
    FILL_STATUS_MSK = 0x003fff
    FILL_STATUS_SET = 0x00
    FILL_STATUS_RST = 0x00

    CLK_NUM_ERR_ID = 0x1
    CLK_NUM_ERR_POS = 17
    CLK_NUM_ERR_MSK = 0x020000
    CLK_NUM_ERR_SET = 0x00
    CLK_NUM_ERR_RST = 0x00

    BURST_ERR_ID = 0x1
    BURST_ERR_POS = 18
    BURST_ERR_MSK = 0x040000
    BURST_ERR_SET = 0x00
    BURST_ERR_RST = 0x00

    FUF_ERR_ID = 0x1
    FUF_ERR_POS = 19
    FUF_ERR_MSK = 0x080000
    FUF_ERR_SET = 0x00
    FUF_ERR_RST = 0x00

    EMPTY_ID = 0x1
    EMPTY_POS = 20
    EMPTY_MSK = 0x100000
    EMPTY_SET = 0x00
    EMPTY_RST = 0x00

    CREF_ID = 0x1
    CREF_POS = 21
    CREF_MSK = 0x200000
    CREF_SET = 0x00
    CREF_RST = 0x00

    FULL_ID = 0x1
    FULL_POS = 22
    FULL_MSK = 0x400000
    FULL_SET = 0x00
    FULL_RST = 0x00

    FOF_ERR_ID = 0x1
    FOF_ERR_POS = 23
    FOF_ERR_MSK = 0x800000
    FOF_ERR_SET = 0x00
    FOF_ERR_RST = 0x00

# ==============================================================================
# Class Name: BGT60ATR24C Register: CHIP_ID_1_REG
# ==============================================================================
class CHIP_ID_1_REG(IntEnum):
    CHIP_ID_1_ADR = 0x60

    CHIP_ID_1_ID = 0xf90
    CHIP_ID_1_POS = 0
    CHIP_ID_1_MSK = 0xffffff
    CHIP_ID_1_SET = 0x00
    CHIP_ID_1_RST = 0x00

# ==============================================================================
# Class Name: BGT60ATR24C Register: CHIP_ID_2_REG
# ==============================================================================
class CHIP_ID_2_REG(IntEnum):
    CHIP_ID_2_ADR = 0x61

    CHIP_ID_2_ID = 0xf91
    CHIP_ID_2_POS = 0
    CHIP_ID_2_MSK = 0xffffff
    CHIP_ID_2_SET = 0x00
    CHIP_ID_2_RST = 0x00

# ==============================================================================
# Class Name: BGT60ATR24C Register: GSR0_REG
# ==============================================================================
class GSR0_REG(IntEnum):
    CLK_NUM_ERR_ID = 0x1
    CLK_NUM_ERR_POS = 0
    CLK_NUM_ERR_MSK = 0x000001
    CLK_NUM_ERR_SET = 0x00
    CLK_NUM_ERR_RST = 0x00

    SPI_BURST_ERR_ID = 0x1
    SPI_BURST_ERR_POS = 1
    SPI_BURST_ERR_MSK = 0x000002
    SPI_BURST_ERR_SET = 0x00
    SPI_BURST_ERR_RST = 0x00

    MISO_HS_READ_ID = 0x1
    MISO_HS_READ_POS = 2
    MISO_HS_READ_MSK = 0x000004
    MISO_HS_READ_SET = 0x00
    MISO_HS_READ_RST = 0x00

    FOU_ERR_ID = 0x1
    FOU_ERR_POS = 3
    FOU_ERR_MSK = 0x000008
    FOU_ERR_SET = 0x00
    FOU_ERR_RST = 0x00
