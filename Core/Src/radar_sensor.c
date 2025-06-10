#include "radar_sensor.h"
#include "usb_handler.h"
#include "gpio_handler.h"
#include <string.h>

SPI_Cmd_TypeDef spi_config_struct;
volatile uint8_t fifo_buf_spi_indicator = 0;
uint8_t fifo_buf_spi[FIFO_BUF_SIZE][FIFO_READ_BASE_SIZE + FIFO_MAX_OVERHEAD] = {0};

Sensor_Register_Config sensor_cfg;
MiRa_Sensor_ID sensor_ids;
MiRa_USB_Config usb_config;

typedef struct SPI_Data_s{
	uint8_t* rxBuffer;
	volatile uint8_t rxRdy;
	volatile uint16_t rxLength;

	uint8_t* txBuffer;
	volatile uint8_t txRdy;
	volatile uint16_t txLength;
} SPI_Data_TypeDef;

volatile SPI_Data_TypeDef spiData_s;

void decode_chip_version(uint8_t digital_id, uint8_t rf_id);
void init_qspi_commands(void);
void init_qspi_dio3_pull_pin(void);
void read_n_bgt_register(void);
void get_chip_ids(void);
void activate_qspi_gpios(void);
void deactivate_qspi_gpios(void);
void write_bgt_reg_generic(uint32_t adr_reg_value);
void read_single_bgt_register_generic(uint8_t* rx_buffer, uint8_t adr);
void read_singel_bgt_register(void);
void write_bgt_reg(void);


void Sensor_Init(void) {
    init_qspi_commands();
    init_qspi_dio3_pull_pin();
    HAL_OSPI_RegisterCallback(&hospi1, HAL_MDMA_XFER_CPLT_CB_ID, HAL_OSPI_RxCpltCallback);
    get_chip_ids();
}

void init_bgt_registers(void){
	for(uint16_t reg_val_buf_pos = 1; reg_val_buf_pos < usbData_s.rxLength - 5; reg_val_buf_pos += 4){

		spi_config_struct.writer->Instruction = (uint32_t) (((usbData_s.rxBuffer[reg_val_buf_pos+0] << 1) | 1) << 24)
                                                	       | (usbData_s.rxBuffer[reg_val_buf_pos+1] << 16)
                                                           | (usbData_s.rxBuffer[reg_val_buf_pos+2] << 8)
                                                           | (usbData_s.rxBuffer[reg_val_buf_pos+3] << 0);

		(void)activate_qspi_gpios();

		HAL_OSPI_Command(&hospi1, spi_config_struct.writer, 1);
		HAL_OSPI_Transmit(&hospi1, (uint8_t*) NULL, 1);

		(void)deactivate_qspi_gpios();
	}
}

void read_singel_bgt_register(void){
	uint8_t bgt_reg_buffer[N_BYTES_BGT_ADR_REG] = {0};

	spi_config_struct.reg_reader->Address = (uint32_t) ((usbData_s.rxBuffer[1] << 1) | 0);

	(void)activate_qspi_gpios();

	HAL_OSPI_Command(&hospi1, spi_config_struct.reg_reader, 1);
	HAL_OSPI_Receive(&hospi1, (uint8_t*) &bgt_reg_buffer[1], 1);

	(void)deactivate_qspi_gpios();

	bgt_reg_buffer[0] = usbData_s.rxBuffer[1];

	CDC_Transmit_HS((uint8_t*) &bgt_reg_buffer[0], N_BYTES_BGT_ADR_REG);
}

void write_bgt_reg(void){
	spi_config_struct.writer->Instruction = (uint32_t) (((usbData_s.rxBuffer[1] << 1) | 1) << 24)
												       | (usbData_s.rxBuffer[2] <<16)
													   | (usbData_s.rxBuffer[3] << 8)
													   | (usbData_s.rxBuffer[4] << 0);

	(void)activate_qspi_gpios();

	HAL_OSPI_Command(&hospi1, spi_config_struct.writer, 1);
	HAL_OSPI_Transmit(&hospi1, (uint8_t*) NULL, 1);

	(void)deactivate_qspi_gpios();
}

void init_qspi_commands(void) {
    spi_config_struct.spi_writer.AlternateBytesMode = HAL_OSPI_ALTERNATE_BYTES_NONE;
    spi_config_struct.spi_writer.InstructionMode = HAL_OSPI_INSTRUCTION_1_LINE;
    spi_config_struct.spi_writer.InstructionSize = HAL_OSPI_INSTRUCTION_32_BITS;
    spi_config_struct.spi_writer.AddressMode = HAL_OSPI_ADDRESS_NONE;
    spi_config_struct.spi_writer.DataMode = HAL_OSPI_DATA_NONE;
    spi_config_struct.spi_writer.DummyCycles = 0;
    spi_config_struct.spi_writer.NbData = 0;

    spi_config_struct.qspi_writer = spi_config_struct.spi_writer;

    spi_config_struct.spi_reg_reader.AlternateBytesMode = HAL_OSPI_ALTERNATE_BYTES_NONE;
    spi_config_struct.spi_reg_reader.InstructionMode = HAL_OSPI_INSTRUCTION_NONE;
    spi_config_struct.spi_reg_reader.AddressMode = HAL_OSPI_ADDRESS_1_LINE;
    spi_config_struct.spi_reg_reader.AddressSize = HAL_OSPI_ADDRESS_8_BITS;
    spi_config_struct.spi_reg_reader.DataMode = HAL_OSPI_DATA_1_LINE;
    spi_config_struct.spi_reg_reader.DummyCycles = 0;
    spi_config_struct.spi_reg_reader.NbData = N_BYTES_BGT_PER_REG;

    spi_config_struct.qspi_reg_reader = spi_config_struct.spi_reg_reader;
    spi_config_struct.qspi_reg_reader.AddressMode = HAL_OSPI_ADDRESS_4_LINES;
    spi_config_struct.qspi_reg_reader.DataMode = HAL_OSPI_DATA_4_LINES;
    spi_config_struct.qspi_reg_reader.DummyCycles = 8;

    spi_config_struct.spi_n_reg_reader = spi_config_struct.spi_reg_reader;

    spi_config_struct.qspi_n_reg_reader = spi_config_struct.qspi_reg_reader;

    spi_config_struct.spi_fifo_reader = spi_config_struct.spi_reg_reader;
    spi_config_struct.spi_fifo_reader.AddressSize = HAL_OSPI_ADDRESS_32_BITS;
    spi_config_struct.spi_fifo_reader.Address = 0xFFC00000;
    spi_config_struct.spi_fifo_reader.NbData = FIFO_READ_BASE_SIZE;

    spi_config_struct.qspi_fifo_reader = spi_config_struct.qspi_reg_reader;
    spi_config_struct.qspi_fifo_reader.AddressSize = HAL_OSPI_ADDRESS_8_BITS;
    spi_config_struct.qspi_fifo_reader.Address = 0x62;
}

void init_qspi_dio3_pull_pin(void) {
    pullMode_s.pull_InitStruct_input.Speed = GPIO_SPEED_FREQ_HIGH;
    pullMode_s.pull_InitStruct_input.Mode = GPIO_MODE_INPUT;
    pullMode_s.pull_InitStruct_input.Pull = GPIO_PULLUP;
    pullMode_s.pull_InitStruct_input.Pin = PULL_Pin;

    pullMode_s.pull_InitStruct_output.Speed = GPIO_SPEED_FREQ_HIGH;
    pullMode_s.pull_InitStruct_output.Mode = GPIO_MODE_OUTPUT_PP;
    pullMode_s.pull_InitStruct_output.Pull = GPIO_PULLUP;
    pullMode_s.pull_InitStruct_output.Pin = PULL_Pin;
}

void get_chip_ids(void) {
    uint8_t chip_version[N_BYTES_BGT_ADR_REG] = {0};
    uint8_t chip_id_1_lower[N_BYTES_BGT_ADR_REG] = {0};
    uint8_t chip_id_2_upper[N_BYTES_BGT_ADR_REG] = {0};

    spi_config_struct.writer = &spi_config_struct.spi_writer;
    spi_config_struct.reg_reader = &spi_config_struct.spi_reg_reader;
    read_single_bgt_register_generic(chip_version, 0x02);

    chip_id[6] = chip_version[2];
    chip_id[7] = chip_version[3];

    decode_chip_version(chip_version[2], chip_version[3]);

    if (sensor_ids.uuid == BGT60ATR24C_SENSOR_UUID) {
        write_bgt_reg_generic(0x57000000);
        write_bgt_reg_generic(0x57000010);
        write_bgt_reg_generic(0x57004010);
        for(volatile uint16_t i = 0; i < 0xffff; i++){};
        read_single_bgt_register_generic(chip_id_1_lower, 0x60);
        read_single_bgt_register_generic(chip_id_2_upper, 0x61);
        for (uint8_t i = 0; i < 6; i++){
            uint8_t offset = 0;
            uint8_t* chip_id_p = 0;
            if (i > 2){
                offset = 3;
                chip_id_p = chip_id_1_lower;
            } else{
                chip_id_p = chip_id_2_upper;
            }
            chip_id[i] = chip_id_p[i+1-offset];
        }
    }

    if (sensor_ids.uuid == BGT60TR13C_SENSOR_UUID){
        chip_id[0] = 0x60;
        chip_id[1] = 0x13;
        chip_id[2] = 0x00;
        chip_id[3] = 0x00;
        chip_id[4] = 0x60;
        chip_id[5] = 0x13;
    }

    if (sensor_ids.uuid == BGT60UTR11AIP_SENSOR_UUID){
        write_bgt_reg_generic(0x57000000);
        write_bgt_reg_generic(0x57000010);
        write_bgt_reg_generic(0x57004010);

        write_bgt_reg_generic(0x57000010);
        for(volatile uint16_t i = 0; i < 0xffff; i++){};

        read_single_bgt_register_generic(chip_id_1_lower, 0x5d);
        read_single_bgt_register_generic(chip_id_2_upper, 0x5e);

        write_bgt_reg_generic(0x57000000);
        for (uint8_t i = 0; i < 6; i++){
            uint8_t offset = 0;
            uint8_t* chip_id_p = 0;
            if (i > 2){
                offset = 3;
                chip_id_p = chip_id_1_lower;
            } else{
                chip_id_p = chip_id_2_upper;
            }
            chip_id[i] = chip_id_p[i+1-offset];
        }
    }

    sensor_ids.chip_id_1 = chip_id_1_lower[1] << 16 | chip_id_1_lower[2] << 8 | chip_id_1_lower[3];
    sensor_ids.chip_id_2 = chip_id_2_upper[1] << 16 | chip_id_2_upper[2] << 8 | chip_id_2_upper[3];
    sensor_ids.chip_id = sensor_ids.chip_id_2 << 24 | sensor_ids.chip_id_1;
}

void activate_qspi_gpios(void) {
    HAL_GPIO_WritePin(CSN_GPIO_Port, CSN_Pin, GPIO_PIN_RESET);

    if (sensor_ids.uuid == BGT60ATR24C_SENSOR_UUID) {
        HAL_GPIO_Init(PULL_GPIO_Port, &pullMode_s.pull_InitStruct_input);
    }
}

void deactivate_qspi_gpios(void) {
    if (sensor_ids.uuid == BGT60ATR24C_SENSOR_UUID) {
        HAL_GPIO_Init(PULL_GPIO_Port, &pullMode_s.pull_InitStruct_output);
        HAL_GPIO_WritePin(PULL_GPIO_Port, PULL_Pin, GPIO_PIN_SET);
    }
    HAL_GPIO_WritePin(CSN_GPIO_Port, CSN_Pin, GPIO_PIN_SET);
}

void write_bgt_reg_generic(uint32_t adr_reg_value) {
    spi_config_struct.writer->Instruction = (uint32_t) (((((uint8_t)(adr_reg_value >> 24) << 1) | 1) << 24)
                                                        |  ((uint8_t)(adr_reg_value >> 16) << 16)
                                                        |  ((uint8_t)(adr_reg_value >>  8) << 8)
                                                        |  ((uint8_t)(adr_reg_value >>  0) << 0));

    activate_qspi_gpios();

    HAL_OSPI_Command(&hospi1, spi_config_struct.writer, 1);
    HAL_OSPI_Transmit(&hospi1, (uint8_t*) NULL, 1);

    deactivate_qspi_gpios();
}

void read_single_bgt_register_generic(uint8_t* rx_buffer, uint8_t adr) {
    spi_config_struct.reg_reader->Address = (uint32_t) ((adr << 1) | 0);

    activate_qspi_gpios();

    HAL_OSPI_Command(&hospi1, spi_config_struct.reg_reader, 1);
    HAL_OSPI_Receive(&hospi1, (uint8_t*) &rx_buffer[1], 1);

    deactivate_qspi_gpios();

    rx_buffer[0] = adr;
}

void decode_chip_version(uint8_t digital_id, uint8_t rf_id) {
    sensor_ids.digital_id = digital_id;
    sensor_ids.rf_id = rf_id;

    if (digital_id == BGT60ATR24C_DIGITAL_ID && rf_id == BGT60ATR24C_RF_ID) {
        sensor_ids.uuid = BGT60ATR24C_SENSOR_UUID;
        sensor_cfg.fifo_base_size = BGT60ATR24C_FIFO_READ;
        sensor_cfg.fifo_adr = BGT60ATR24C_FIFO_ADR;
        usb_config.usb_product_id = BGT60ATR24C_USB_PRODUCT_ID;
        strcpy(usb_config.usb_product_name, BGT60ATR24C_PRODUCT_NAME);
        spi_config_struct.writer = &spi_config_struct.qspi_writer;
        spi_config_struct.reg_reader = &spi_config_struct.qspi_reg_reader;
        spi_config_struct.n_reg_reader = &spi_config_struct.qspi_n_reg_reader;
        spi_config_struct.fifo_reader = &spi_config_struct.qspi_fifo_reader;
    } else if (digital_id == BGT60TR13C_DIGITAL_ID && rf_id == BGT60TR13C_RF_ID) {
        sensor_ids.uuid = BGT60TR13C_SENSOR_UUID;
        sensor_cfg.fifo_base_size = BGT60TR13C_FIFO_READ;
        sensor_cfg.fifo_adr = BGT60TR13C_FIFO_ADR;
        usb_config.usb_product_id = BGT60TR13C_USB_PRODUCT_ID;
        strcpy(usb_config.usb_product_name, BGT60TR13C_PRODUCT_NAME);
        spi_config_struct.writer = &spi_config_struct.spi_writer;
        spi_config_struct.reg_reader = &spi_config_struct.spi_reg_reader;
        spi_config_struct.n_reg_reader = &spi_config_struct.spi_n_reg_reader;
        spi_config_struct.fifo_reader = &spi_config_struct.spi_fifo_reader;
    } else if (digital_id == BGT60UTR11AIP_DIGITAL_ID && rf_id == BGT60UTR11AIP_RF_ID) {
        sensor_ids.uuid = BGT60UTR11AIP_SENSOR_UUID;
        sensor_cfg.fifo_base_size = BGT60UTR11AIP_FIFO_READ;
        sensor_cfg.fifo_adr = BGT60UTR11AIP_FIFO_ADR;
        usb_config.usb_product_id = BGT60UTR11AIP_USB_PRODUCT_ID;
        strcpy(usb_config.usb_product_name, BGT60UTR11AIP_PRODUCT_NAME);
        spi_config_struct.writer = &spi_config_struct.spi_writer;
        spi_config_struct.reg_reader = &spi_config_struct.spi_reg_reader;
        spi_config_struct.n_reg_reader = &spi_config_struct.spi_n_reg_reader;
        spi_config_struct.fifo_reader = &spi_config_struct.spi_fifo_reader;
    } else {
        usb_config.usb_product_id = MIRA_ERR_INDICATION_USB_PRODUCT_ID;
        strcpy(usb_config.usb_product_name, MIRA_ERR_INDICATION_USB_PRODUCT_NAME);
    }

    usb_config.usb_vendor_id = USB_VENDOR_ID;
    strcpy(usb_config.usb_manufacturer_name, MIRA_MANUFACTURER_NAME);
    spi_config_struct.fifo_reader->NbData = sensor_cfg.fifo_base_size;
    spi_config_struct.fifo_reader->Address = sensor_cfg.fifo_adr;
}

inline void HAL_OSPI_RxCpltCallback(OSPI_HandleTypeDef *hospi){
	if(init_bgt_flag == 1){
		(void)deactivate_qspi_gpios();

		if(fifo_buf_spi_indicator == 0){
			fifo_buf_spi_indicator = 1;
			CDC_Transmit_HS((uint8_t *) &fifo_buf_spi[0][0], (uint16_t) (sensor_cfg.fifo_base_size
														  	  	  	  + (spi_config_struct.n_fifo_overhead*FIFO_HEADER_SIZE)));
		}else{
			if(fifo_buf_spi_indicator == 1){
				fifo_buf_spi_indicator = 0;
				CDC_Transmit_HS((uint8_t *) &fifo_buf_spi[1][0], (uint16_t) (sensor_cfg.fifo_base_size
																		  + (spi_config_struct.n_fifo_overhead*FIFO_HEADER_SIZE)));
			}
		}
	}
}

inline void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin){

    if(GPIO_Pin == FIFO_IRQ_Pin && init_bgt_flag == 1) // check if FIFO is filled to the selected level
    {
    	(void)activate_qspi_gpios();

    	HAL_OSPI_Command(&hospi1, spi_config_struct.fifo_reader, 1); // send the FIFO command to BGT
    	if(fifo_buf_spi_indicator == 0){
    		HAL_OSPI_Receive_DMA(&hospi1, (uint8_t*) &fifo_buf_spi[0][0]); // read BGT FIFO
    	}
    	else{
    		if(fifo_buf_spi_indicator == 1){
    		HAL_OSPI_Receive_DMA(&hospi1, (uint8_t*) &fifo_buf_spi[1][0]); // read BGT FIFO
    		}
    	}
	}
}


void read_n_bgt_register(void){
	// The complete BGT registers should be read out at once and send via USB
	uint16_t qspi_rx_len = 1;
	qspi_rx_len = ((uint16_t) ((uint16_t) (usbData_s.rxBuffer[2] << 8)
							 | (uint16_t) usbData_s.rxBuffer[3]));
	qspi_rx_len *= 3;

	spi_config_struct.n_reg_reader->Address = (uint32_t) usbData_s.rxBuffer[1];

	if (spiData_s.rxBuffer == NULL){
		spiData_s.rxBuffer = (uint8_t*) malloc(qspi_rx_len*sizeof(uint8_t));
	}
	spi_config_struct.n_reg_reader->NbData = (uint32_t) qspi_rx_len;

	(void)activate_qspi_gpios();

	HAL_OSPI_Command(&hospi1, spi_config_struct.n_reg_reader, 1);
	HAL_OSPI_Receive(&hospi1, (uint8_t*) &spiData_s.rxBuffer[0], 1);

	(void)deactivate_qspi_gpios();

	CDC_Transmit_HS((uint8_t*) &spiData_s.rxBuffer[0], qspi_rx_len);
}

