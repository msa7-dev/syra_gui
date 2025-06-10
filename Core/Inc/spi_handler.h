#ifndef SPI_HANDLER_H
#define SPI_HANDLER_H

#include "stm32h7xx_hal.h"
#include "stm32h7xx_hal_ospi.h"

extern OSPI_HandleTypeDef hospi1;

void MX_OCTOSPI1_Init(void);

#endif // SPI_HANDLER_H
