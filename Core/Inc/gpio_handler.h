#ifndef GPIO_HANDLER_H
#define GPIO_HANDLER_H

#include "stm32h7xx_hal.h"

#define LED_Pin GPIO_PIN_5
#define LED_GPIO_Port GPIOE

#define PULL_Pin GPIO_PIN_0
#define PULL_GPIO_Port GPIOA

#define USB_SWITCH_PIN_Pin GPIO_PIN_11
#define USB_SWITCH_PIN_GPIO_Port GPIOA

#define CSN_Pin GPIO_PIN_11
#define CSN_GPIO_Port GPIOE

#define FIFO_IRQ_Pin GPIO_PIN_13
#define FIFO_IRQ_GPIO_Port GPIOE
#define FIFO_IRQ_EXTI_IRQn EXTI15_10_IRQn

#define BOOT_PULL_Pin GPIO_PIN_6
#define BOOT_PULL_GPIO_Port GPIOB

// Struct definition here
struct PULL_Mode_s {
    GPIO_InitTypeDef pull_InitStruct_output;
    GPIO_InitTypeDef pull_InitStruct_input;
    GPIO_InitTypeDef usb_switch_InitStruct_output;
};

extern struct PULL_Mode_s pullMode_s; // Declaration

void MX_GPIO_Init(void);

#endif // GPIO_HANDLER_H
