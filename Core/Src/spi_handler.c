#include "main.h"
#include "spi_handler.h"

OSPI_HandleTypeDef hospi1;

void MX_OCTOSPI1_Init(void)
{
    OSPIM_CfgTypeDef sOspiManagerCfg = {0};

    hospi1.Instance = OCTOSPI1;
    hospi1.Init.FifoThreshold = 1;
    hospi1.Init.DualQuad = HAL_OSPI_DUALQUAD_DISABLE;
    hospi1.Init.MemoryType = HAL_OSPI_MEMTYPE_MICRON;
    hospi1.Init.DeviceSize = 32;
    hospi1.Init.ChipSelectHighTime = 1;
    hospi1.Init.FreeRunningClock = HAL_OSPI_FREERUNCLK_DISABLE;
    hospi1.Init.ClockMode = HAL_OSPI_CLOCK_MODE_0;
    hospi1.Init.WrapSize = HAL_OSPI_WRAP_NOT_SUPPORTED;
    hospi1.Init.ClockPrescaler = 1;
    hospi1.Init.SampleShifting = HAL_OSPI_SAMPLE_SHIFTING_NONE;
    hospi1.Init.DelayHoldQuarterCycle = HAL_OSPI_DHQC_DISABLE;
    hospi1.Init.ChipSelectBoundary = 0;
    hospi1.Init.DelayBlockBypass = HAL_OSPI_DELAY_BLOCK_BYPASSED;
    hospi1.Init.MaxTran = 0;
    hospi1.Init.Refresh = 0;

    if (HAL_OSPI_Init(&hospi1) != HAL_OK)
    {
        Error_Handler();
    }

    sOspiManagerCfg.ClkPort = 1;
    sOspiManagerCfg.IOLowPort = HAL_OSPIM_IOPORT_1_LOW;

    if (HAL_OSPIM_Config(&hospi1, &sOspiManagerCfg, HAL_OSPI_TIMEOUT_DEFAULT_VALUE) != HAL_OK)
    {
        Error_Handler();
    }
}
