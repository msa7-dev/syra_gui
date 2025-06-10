#ifndef INC_SYSTEM_CONFIG_H_
#define INC_SYSTEM_CONFIG_H_

// Firmware Information
#define MIRA_MCU_FW_VERSION "v1.0"
#define MIRA_MCU_FW_TYPE "Radar Bridge"

// Boolean Constants
#define TRUE 1
#define FALSE 0

// Buffer and FIFO Configuration
#define MAX_LOST_PACKAGES 255
#define FIFO_READ_BASE_SIZE 20000UL
#define FIFO_HEADER_SIZE 9
#define MIN_NBR_SAMPLES 64
#define FIFO_MAX_OVERHEAD 1152
#define FIFO_BUF_SIZE 2
#define N_INIT_BGT_REGS 48
#define N_BYTES_BGT_PER_REG 3
#define N_BYTES_BGT_ADR_REG 4

// USB and Command Definitions
#define SET_SPI_DUMMY_CYCLES_CMD 0x0A
#define SET_FIFO_OVERHEAD_CMD 0x1A
#define SET_FIFO_CREF_CMD 0xA0
#define INIT_RX_CMD 0x11
#define INIT_FINISHED_CMD 0xAA
#define READ_REG_RX_CMD 0x22
#define READ_ALL_REGS_RX_CMD 0x33
#define WRITE_REG_RX_CMD 0x44
#define BGT_RESET_CMD 0xFF
#define STM_RST_CMD 0xEE
#define GET_CHIP_ID_CMD 0xBB
#define MCU_FLASH_CMD 0xCC

#define USBD_VID 0xE404
#define USBD_PID_HS 0xE404
#define USBD_LANGID_STRING 1031
#define USBD_MANUFACTURER_STRING     "Sykno GmbH"
#define USBD_CONFIGURATION_STRING_HS "Sykno Radar Bridge CDC Config"
#define USBD_INTERFACE_STRING_HS     "Sykno Radar Bridge CDC Interface"
#define USBD_PRODUCT_STRING_HS       "Sykno Radar Bridge No Sensor Detected"

// MiRa Sensor ID Structure
typedef struct {
    uint8_t uuid;
    uint8_t digital_id;
    uint8_t rf_id;
    uint32_t chip_id_1;
    uint32_t chip_id_2;
    uint64_t chip_id;
} MiRa_Sensor_ID;

// MiRa USB Configuration Structure
typedef struct {
    uint16_t usb_product_id;
    uint16_t usb_vendor_id;
    char usb_manufacturer_name[128];
    char usb_product_name[128];
} MiRa_USB_Config;

// Sensor Register Configuration Structure
typedef struct {
    uint32_t fifo_base_size;
    uint32_t fifo_adr;
    uint16_t fifo_header_overhead;
} Sensor_Register_Config;

// USB Vendor Information
#define USB_VENDOR_ID 0x1337
#define MIRA_MANUFACTURER_NAME "Sykno GmbH"

// Sensor-Specific Identifiers and Constants
#define BGT60ATR24C_DIGITAL_ID 5
#define BGT60ATR24C_RF_ID 4
#define BGT60ATR24C_SENSOR_UUID 0x24
#define BGT60ATR24C_FIFO_ADR 0x62
#define BGT60ATR24C_FIFO_READ 12288UL
#define BGT60ATR24C_USB_PRODUCT_ID 0x6024
#define BGT60ATR24C_PRODUCT_NAME "| " MIRA_MANUFACTURER_NAME " - MiRa6024 | FW: " MIRA_MCU_FW_TYPE " (" MIRA_MCU_FW_VERSION ") |"

#define BGT60TR13C_DIGITAL_ID 3
#define BGT60TR13C_RF_ID 3
#define BGT60TR13C_SENSOR_UUID 0x13
#define BGT60TR13C_FIFO_ADR 0xFFC00000UL
#define BGT60TR13C_FIFO_READ 18432UL
#define BGT60TR13C_USB_PRODUCT_ID 0x6013
#define BGT60TR13C_PRODUCT_NAME "| " MIRA_MANUFACTURER_NAME " - SY6013 | FW: " MIRA_MCU_FW_TYPE " (" MIRA_MCU_FW_VERSION ") |"

#define BGT60UTR11AIP_DIGITAL_ID 7
#define BGT60UTR11AIP_RF_ID 12
#define BGT60UTR11AIP_SENSOR_UUID 0x11
#define BGT60UTR11AIP_FIFO_ADR 0xFFE40000UL
#define BGT60UTR11AIP_FIFO_READ 3072UL
#define BGT60UTR11AIP_USB_PRODUCT_ID 0x6011
#define BGT60UTR11AIP_PRODUCT_NAME "| " MIRA_MANUFACTURER_NAME " - SY6011 | FW: " MIRA_MCU_FW_TYPE " (" MIRA_MCU_FW_VERSION ") |"

#define MIRA_ERR_INDICATION_USB_PRODUCT_ID 0xE404
#define MIRA_ERR_INDICATION_USB_PRODUCT_NAME "| " MIRA_MANUFACTURER_NAME " - No MiRa sensor detected | FW: " MIRA_MCU_FW_TYPE " (" MIRA_MCU_FW_VERSION ") |"

#endif /* INC_SYSTEM_CONFIG_H_ */
