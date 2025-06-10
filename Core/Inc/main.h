#ifndef __MAIN_H
#define __MAIN_H

#ifdef __cplusplus
extern "C" {
#endif

#include "stm32h7xx_hal.h"

void Error_Handler(void);

extern void set_new_usb_descriptor(void);
extern uint8_t chip_id[8];

#ifdef __cplusplus
}
#endif

#endif /* __MAIN_H */
