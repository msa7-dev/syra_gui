#ifndef RADAR_SENSOR_H
#define RADAR_SENSOR_H

#include "stm32h7xx_hal.h"
#include "system_config.h"

extern OSPI_HandleTypeDef hospi1; // Assuming this is the type of hospi1
extern uint8_t init_bgt_flag;

typedef struct {
    OSPI_RegularCmdTypeDef spi_writer;
    OSPI_RegularCmdTypeDef qspi_writer;
    OSPI_RegularCmdTypeDef* writer;

    OSPI_RegularCmdTypeDef spi_reg_reader;
    OSPI_RegularCmdTypeDef qspi_reg_reader;
    OSPI_RegularCmdTypeDef* reg_reader;

    OSPI_RegularCmdTypeDef spi_n_reg_reader;
    OSPI_RegularCmdTypeDef qspi_n_reg_reader;
    OSPI_RegularCmdTypeDef* n_reg_reader;

    OSPI_RegularCmdTypeDef spi_fifo_reader;
    OSPI_RegularCmdTypeDef qspi_fifo_reader;
    OSPI_RegularCmdTypeDef* fifo_reader;

    uint8_t n_dummy_cycles;
    uint8_t n_fifo_overhead;
    uint16_t n_read_fifo;
} SPI_Cmd_TypeDef;

extern SPI_Cmd_TypeDef spi_config_struct;
extern volatile uint8_t fifo_buf_spi_indicator;
extern uint8_t fifo_buf_spi[FIFO_BUF_SIZE][FIFO_READ_BASE_SIZE + FIFO_MAX_OVERHEAD];
extern Sensor_Register_Config sensor_cfg;
extern MiRa_Sensor_ID sensor_ids;
extern MiRa_USB_Config usb_config;

void init_qspi_commands(void);
void init_bgt_registers(void);
void read_singel_bgt_register(void);
void read_n_bgt_register(void);
void write_bgt_reg(void);
void get_chip_ids(void);
void init_qspi_dio3_pull_pin(void);
void activate_qspi_gpios(void);
void deactivate_qspi_gpios(void);
void write_bgt_reg_generic(uint32_t adr_reg_value);
void read_single_bgt_register_generic(uint8_t* rx_buffer, uint8_t adr);

#endif // RADAR_SENSOR_H
