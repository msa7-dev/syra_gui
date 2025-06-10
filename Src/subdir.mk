################################################################################
# Automatically-generated file. Do not edit!
# Toolchain: GNU Tools for STM32 (13.3.rel1)
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
../Core/Src/clock_config.c \
../Core/Src/dma_handler.c \
../Core/Src/gpio_handler.c \
../Core/Src/json_config.c \
../Core/Src/main.c \
../Core/Src/radar_sensor.c \
../Core/Src/spi_handler.c \
../Core/Src/stm32h7xx_hal_msp.c \
../Core/Src/stm32h7xx_it.c \
../Core/Src/syscalls.c \
../Core/Src/sysmem.c \
../Core/Src/system_stm32h7xx.c \
../Core/Src/usb_handler.c 

OBJS += \
./Core/Src/clock_config.o \
./Core/Src/dma_handler.o \
./Core/Src/gpio_handler.o \
./Core/Src/json_config.o \
./Core/Src/main.o \
./Core/Src/radar_sensor.o \
./Core/Src/spi_handler.o \
./Core/Src/stm32h7xx_hal_msp.o \
./Core/Src/stm32h7xx_it.o \
./Core/Src/syscalls.o \
./Core/Src/sysmem.o \
./Core/Src/system_stm32h7xx.o \
./Core/Src/usb_handler.o 

C_DEPS += \
./Core/Src/clock_config.d \
./Core/Src/dma_handler.d \
./Core/Src/gpio_handler.d \
./Core/Src/json_config.d \
./Core/Src/main.d \
./Core/Src/radar_sensor.d \
./Core/Src/spi_handler.d \
./Core/Src/stm32h7xx_hal_msp.d \
./Core/Src/stm32h7xx_it.d \
./Core/Src/syscalls.d \
./Core/Src/sysmem.d \
./Core/Src/system_stm32h7xx.d \
./Core/Src/usb_handler.d 


# Each subdirectory must supply rules for building sources it contributes
Core/Src/%.o Core/Src/%.su Core/Src/%.cyclo: ../Core/Src/%.c Core/Src/subdir.mk
	arm-none-eabi-gcc "$<" -mcpu=cortex-m7 -std=gnu18 -DDEBUG -DUSE_HAL_DRIVER -DSTM32H723xx -c -I../USB_DEVICE/App -I../USB_DEVICE/Target -I../Core/Inc -I../Drivers/STM32H7xx_HAL_Driver/Inc -I../Drivers/STM32H7xx_HAL_Driver/Inc/Legacy -I../Middlewares/ST/STM32_USB_Device_Library/Core/Inc -I../Middlewares/ST/STM32_USB_Device_Library/Class/CDC/Inc -I../Drivers/CMSIS/Device/ST/STM32H7xx/Include -I../Drivers/CMSIS/Include -O0 -ffunction-sections -fdata-sections -Wall -fstack-usage -fcyclomatic-complexity -MMD -MP -MF"$(@:%.o=%.d)" -MT"$@" --specs=nano.specs -mfpu=fpv5-d16 -mfloat-abi=hard -mthumb -o "$@"

clean: clean-Core-2f-Src

clean-Core-2f-Src:
	-$(RM) ./Core/Src/clock_config.cyclo ./Core/Src/clock_config.d ./Core/Src/clock_config.o ./Core/Src/clock_config.su ./Core/Src/dma_handler.cyclo ./Core/Src/dma_handler.d ./Core/Src/dma_handler.o ./Core/Src/dma_handler.su ./Core/Src/gpio_handler.cyclo ./Core/Src/gpio_handler.d ./Core/Src/gpio_handler.o ./Core/Src/gpio_handler.su ./Core/Src/json_config.cyclo ./Core/Src/json_config.d ./Core/Src/json_config.o ./Core/Src/json_config.su ./Core/Src/main.cyclo ./Core/Src/main.d ./Core/Src/main.o ./Core/Src/main.su ./Core/Src/radar_sensor.cyclo ./Core/Src/radar_sensor.d ./Core/Src/radar_sensor.o ./Core/Src/radar_sensor.su ./Core/Src/spi_handler.cyclo ./Core/Src/spi_handler.d ./Core/Src/spi_handler.o ./Core/Src/spi_handler.su ./Core/Src/stm32h7xx_hal_msp.cyclo ./Core/Src/stm32h7xx_hal_msp.d ./Core/Src/stm32h7xx_hal_msp.o ./Core/Src/stm32h7xx_hal_msp.su ./Core/Src/stm32h7xx_it.cyclo ./Core/Src/stm32h7xx_it.d ./Core/Src/stm32h7xx_it.o ./Core/Src/stm32h7xx_it.su ./Core/Src/syscalls.cyclo ./Core/Src/syscalls.d ./Core/Src/syscalls.o ./Core/Src/syscalls.su ./Core/Src/sysmem.cyclo ./Core/Src/sysmem.d ./Core/Src/sysmem.o ./Core/Src/sysmem.su ./Core/Src/system_stm32h7xx.cyclo ./Core/Src/system_stm32h7xx.d ./Core/Src/system_stm32h7xx.o ./Core/Src/system_stm32h7xx.su ./Core/Src/usb_handler.cyclo ./Core/Src/usb_handler.d ./Core/Src/usb_handler.o ./Core/Src/usb_handler.su

.PHONY: clean-Core-2f-Src

