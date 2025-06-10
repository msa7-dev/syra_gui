#include "dma_handler.h"

void MX_DMA_Init(void)
{
    __HAL_RCC_DMA1_CLK_ENABLE();

    DMA_HandleTypeDef hdma_memtomem_dma1_stream0 = {0};
    hdma_memtomem_dma1_stream0.Instance = DMA1_Stream0;
    hdma_memtomem_dma1_stream0.Init.Request = DMA_REQUEST_MEM2MEM;
    hdma_memtomem_dma1_stream0.Init.Direction = DMA_MEMORY_TO_MEMORY;
    hdma_memtomem_dma1_stream0.Init.PeriphInc = DMA_PINC_ENABLE;
    hdma_memtomem_dma1_stream0.Init.MemInc = DMA_MINC_ENABLE;
    hdma_memtomem_dma1_stream0.Init.PeriphDataAlignment = DMA_PDATAALIGN_WORD;
    hdma_memtomem_dma1_stream0.Init.MemDataAlignment = DMA_MDATAALIGN_WORD;
    hdma_memtomem_dma1_stream0.Init.Mode = DMA_NORMAL;
    hdma_memtomem_dma1_stream0.Init.Priority = DMA_PRIORITY_LOW;
    hdma_memtomem_dma1_stream0.Init.FIFOMode = DMA_FIFOMODE_ENABLE;
    hdma_memtomem_dma1_stream0.Init.FIFOThreshold = DMA_FIFO_THRESHOLD_FULL;
    hdma_memtomem_dma1_stream0.Init.MemBurst = DMA_MBURST_SINGLE;
    hdma_memtomem_dma1_stream0.Init.PeriphBurst = DMA_PBURST_SINGLE;

    if (HAL_DMA_Init(&hdma_memtomem_dma1_stream0) != HAL_OK)
    {
        Error_Handler();
    }

    HAL_NVIC_SetPriority(DMA1_Stream0_IRQn, 0, 0);
    HAL_NVIC_EnableIRQ(DMA1_Stream0_IRQn);
}

void MX_MDMA_Init(void)
{
    __HAL_RCC_MDMA_CLK_ENABLE();

    HAL_NVIC_SetPriority(MDMA_IRQn, 0, 0);
    HAL_NVIC_EnableIRQ(MDMA_IRQn);
}
