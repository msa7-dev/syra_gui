#include "main.h"
#include "usb_device.h"
#include "clock_config.h"
#include "dma_handler.h"
#include "gpio_handler.h"
#include "spi_handler.h"
#include "usb_handler.h"
#include "radar_sensor.h"

uint8_t init_bgt_flag = 0;
uint8_t usb_connect_flag = 0;

HAL_StatusTypeDef miraStatusHal;
MDMA_HandleTypeDef hmdma_octospi1_fifo_th;
DMA_HandleTypeDef hdma_memtomem_dma1_stream0;

extern USBD_HandleTypeDef hUsbDeviceHS;
extern void USB_CDC_Tx_Buf_Callback(void);
extern void USB_CDC_ReceiveCallback(uint8_t* Buf, uint32_t *Len);

int main(void)
{
    HAL_Init();
    SystemClock_Config();

    MX_GPIO_Init();
    MX_MDMA_Init();
    MX_DMA_Init();
    MX_OCTOSPI1_Init();

    init_qspi_commands();
    init_qspi_dio3_pull_pin();
    CDC_ReceiveCallback = USB_CDC_ReceiveCallback;
    CDC_Tx_Buf_Callback = USB_CDC_Tx_Buf_Callback;

    HAL_GPIO_Init(PULL_GPIO_Port, &pullMode_s.pull_InitStruct_output);
    HAL_GPIO_WritePin(PULL_GPIO_Port, PULL_Pin, GPIO_PIN_SET);
    HAL_GPIO_WritePin(USB_SWITCH_PIN_GPIO_Port, USB_SWITCH_PIN_Pin, GPIO_PIN_SET);
    HAL_OSPI_RegisterCallback(&hospi1, HAL_MDMA_XFER_CPLT_CB_ID, HAL_OSPI_RxCpltCallback);
    get_chip_ids();
    set_new_usb_descriptor();
    MX_USB_DEVICE_Init();

    while(usb_connect_flag != 1)
    {
        HAL_GPIO_TogglePin(LED_GPIO_Port, LED_Pin);
        HAL_Delay(100);
        HAL_GPIO_TogglePin(LED_GPIO_Port, LED_Pin);
        HAL_Delay(100);
        HAL_GPIO_TogglePin(LED_GPIO_Port, LED_Pin);
        HAL_Delay(100);
        HAL_GPIO_TogglePin(LED_GPIO_Port, LED_Pin);
        HAL_Delay(100);
        HAL_GPIO_TogglePin(LED_GPIO_Port, LED_Pin);
        HAL_Delay(100);
        HAL_GPIO_TogglePin(LED_GPIO_Port, LED_Pin);
        HAL_Delay(500);
        HAL_GPIO_TogglePin(LED_GPIO_Port, LED_Pin);
        HAL_Delay(500);
        HAL_GPIO_TogglePin(LED_GPIO_Port, LED_Pin);
        HAL_Delay(500);
    }

    while(TRUE)
    {
        if(init_bgt_flag != 1)
        {
            HAL_GPIO_TogglePin(LED_GPIO_Port, LED_Pin);
            HAL_Delay(100);
            HAL_GPIO_TogglePin(LED_GPIO_Port, LED_Pin);
            HAL_Delay(100);
            HAL_GPIO_TogglePin(LED_GPIO_Port, LED_Pin);
            HAL_Delay(100);
            HAL_GPIO_TogglePin(LED_GPIO_Port, LED_Pin);
            HAL_Delay(100);
            HAL_GPIO_TogglePin(LED_GPIO_Port, LED_Pin);
            HAL_Delay(100);
            HAL_GPIO_TogglePin(LED_GPIO_Port, LED_Pin);
            HAL_Delay(500);
            HAL_GPIO_TogglePin(LED_GPIO_Port, LED_Pin);
            HAL_Delay(500);
            HAL_GPIO_TogglePin(LED_GPIO_Port, LED_Pin);
            HAL_Delay(500);
        }
        else
        {
            HAL_Delay(0xFFFFFFFF);
        }
    }
}

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */
  __disable_irq();
  while (1)
  {
  }
  /* USER CODE END Error_Handler_Debug */
}

#ifdef  USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */
