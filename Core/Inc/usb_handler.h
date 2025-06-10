#ifndef USB_HANDLER_H
#define USB_HANDLER_H

#include "stm32h7xx_hal.h"
#include "usbd_cdc_if.h"

typedef struct {
    uint8_t* txBuffer;
    volatile uint8_t txRdy;
    volatile uint16_t txLength;

    uint8_t* rxBuffer;
    volatile uint8_t rxRdy;
    volatile uint16_t rxLength;
} USB_Data_TypeDef;


extern volatile USB_Data_TypeDef usbData_s;

void USB_CDC_ReceiveCallback(uint8_t* Buf, uint32_t *Len);
void USB_CDC_Tx_Buf_Callback(void);
void usb_rx_handle_cases(void);
uint8_t compare_rx_usb_cmd(uint8_t rx_cmd);
void boot_rst(void);

#endif // USB_HANDLER_H
