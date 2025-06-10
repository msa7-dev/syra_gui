#include "usb_handler.h"
#include "gpio_handler.h"
#include "radar_sensor.h"
#include "system_config.h"


volatile USB_Data_TypeDef usbData_s;
extern uint8_t usb_connect_flag;

static void bgt_reset(void){
//	PULL_GPIO_Port->MODER |=  (0b01 << (2 * PULL_Pin));  // change MDIO from Input to Output

	(void)HAL_GPIO_Init(PULL_GPIO_Port, &pullMode_s.pull_InitStruct_output);

	(void)HAL_GPIO_WritePin(PULL_GPIO_Port, PULL_Pin, GPIO_PIN_SET);

	for(volatile uint8_t i = 0; i < 255; i++){};

	(void)HAL_GPIO_WritePin(CSN_GPIO_Port, CSN_Pin, GPIO_PIN_SET);

	for(volatile uint8_t i = 0; i < 255; i++){};

	(void)HAL_GPIO_WritePin(PULL_GPIO_Port, PULL_Pin, GPIO_PIN_RESET);

	for(volatile uint8_t i = 0; i < 255; i++){};

	(void)HAL_GPIO_WritePin(PULL_GPIO_Port, PULL_Pin, GPIO_PIN_SET);
}

void USB_CDC_ReceiveCallback(uint8_t* Buf, uint32_t *Len)
{
    uint8_t* tempRxBuffer = (uint8_t*) realloc(usbData_s.rxBuffer, *Len * sizeof(uint8_t));
    memcpy(tempRxBuffer, Buf, *Len);
    usbData_s.rxBuffer = tempRxBuffer;
    usbData_s.rxLength = *Len;
    usbData_s.rxRdy = 1;

    usb_rx_handle_cases();
    free(tempRxBuffer);
    tempRxBuffer = NULL;
}

void USB_CDC_Tx_Buf_Callback(void)
{
    static uint8_t led_counter = 0;

    if (led_counter < 50) {
        led_counter++;
    } else {
        led_counter = 0;
        if (init_bgt_flag == 1) {
            HAL_GPIO_TogglePin(LED_GPIO_Port, LED_Pin);
        }
    }
}

void usb_rx_handle_cases(void)
{
    if(compare_rx_usb_cmd(SET_FIFO_OVERHEAD_CMD) && usbData_s.rxLength == 2) {
        spi_config_struct.n_fifo_overhead = usbData_s.rxBuffer[1];
        spi_config_struct.fifo_reader->NbData = sensor_cfg.fifo_base_size + (spi_config_struct.n_fifo_overhead * FIFO_HEADER_SIZE);
        return;
    }

    if(compare_rx_usb_cmd(SET_SPI_DUMMY_CYCLES_CMD) && usbData_s.rxLength == 2) {
        spi_config_struct.n_dummy_cycles = usbData_s.rxBuffer[1];
        spi_config_struct.qspi_n_reg_reader.DummyCycles = spi_config_struct.n_dummy_cycles;
        spi_config_struct.qspi_reg_reader.DummyCycles = spi_config_struct.n_dummy_cycles;
        spi_config_struct.qspi_fifo_reader.DummyCycles = spi_config_struct.n_dummy_cycles;
        return;
    }

    if(compare_rx_usb_cmd(SET_FIFO_CREF_CMD) && usbData_s.rxLength == 3) {
        spi_config_struct.n_read_fifo = ((usbData_s.rxBuffer[1] << 8) | usbData_s.rxBuffer[2]) * 3;
        return;
    }

    if(compare_rx_usb_cmd(INIT_RX_CMD) && usbData_s.rxLength > 5) {
        init_bgt_registers();
        return;
    }

    if(compare_rx_usb_cmd(READ_ALL_REGS_RX_CMD) && usbData_s.rxLength >= 3) {
        read_n_bgt_register();
        free(usbData_s.rxBuffer);
        usbData_s.rxBuffer = NULL;
        return;
    }

    if(compare_rx_usb_cmd(READ_REG_RX_CMD) && usbData_s.rxLength == 2) {
        read_singel_bgt_register();
        return;
    }

    if(compare_rx_usb_cmd(WRITE_REG_RX_CMD) && usbData_s.rxLength == 5) {
        // Compensate for the Python startup delay
        volatile uint32_t delay = 0;
        if (init_bgt_flag == 1) {
            for (uint8_t i = 0; i < 64; i++) {
                delay = 0;
                while (delay < 0xFFFF) {
                    delay++;
                }
            }
        }
        write_bgt_reg();
        return;
    }

    if(compare_rx_usb_cmd(GET_CHIP_ID_CMD) && usbData_s.rxLength == 1) {
        usb_connect_flag = 1;
        CDC_Transmit_HS((uint8_t*) chip_id, 8);
        return;
    }

    if(compare_rx_usb_cmd(INIT_FINISHED_CMD) && usbData_s.rxLength == 1) {
        init_bgt_flag = 1;
        return;
    }

    if(compare_rx_usb_cmd(BGT_RESET_CMD) && usbData_s.rxLength == 1) {
        bgt_reset();
        return;
    }

    if(compare_rx_usb_cmd(STM_RST_CMD) && usbData_s.rxLength == 1) {
        __disable_irq();
        HAL_NVIC_SystemReset();
        return;
    }

    if(compare_rx_usb_cmd(MCU_FLASH_CMD) && usbData_s.rxLength == 1) {
        boot_rst();
        return;
    }
}

uint8_t compare_rx_usb_cmd(uint8_t rx_cmd)
{
    return (usbData_s.rxBuffer[0] == rx_cmd);
}

void boot_rst(void)
{
    bgt_reset();
    HAL_GPIO_WritePin(USB_SWITCH_PIN_GPIO_Port, USB_SWITCH_PIN_Pin, GPIO_PIN_RESET);

    GPIO_InitTypeDef GPIO_InitStruct = {0};

    GPIO_InitStruct.Pin = BOOT_PULL_Pin;
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(BOOT_PULL_GPIO_Port, &GPIO_InitStruct);

    HAL_GPIO_WritePin(BOOT_PULL_GPIO_Port, BOOT_PULL_Pin, GPIO_PIN_SET);

    for (volatile uint32_t i = 0; i < 0x00ffffff; i++) {
        __asm__("nop");
    }
    __disable_irq();

    HAL_NVIC_SystemReset();
}


