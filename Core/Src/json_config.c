#include "json_config.h"
#include <string.h>
#include <stdio.h>

#define CONFIG_DATA_ADDRESS 0x08080000  // Address where the binary data is stored in flash

void load_config(Config *config) {
    // Point to the memory address where the binary data is stored
    const uint8_t *flash_memory = (const uint8_t *)CONFIG_DATA_ADDRESS;

    // Copy the binary data directly into the config structure
    memcpy(config, flash_memory, sizeof(Config));

    // Check the header
    if (config->header != CONFIG_MAGIC_HEADER) {
        printf("Error: Invalid configuration header.\n");
        return;
    }

    // Check the tail
    if (config->tail != CONFIG_MAGIC_TAIL) {
        printf("Error: Invalid configuration tail.\n");
        return;
    }

    // Optionally, print the values to verify they were loaded correctly
    printf("param1: %d\n", config->param1);
    printf("param2: %f\n", config->param2);
    printf("subparam1: %d\n", config->subconfig.subparam1);
    printf("subparam2: %f\n", config->subconfig.subparam2);
    printf("param3: %s\n", config->param3);
}

// Function to validate the configuration
int validate_config(const Config *config) {
    // Check the header and tail for integrity
    if (config->header != CONFIG_MAGIC_HEADER || config->tail != CONFIG_MAGIC_TAIL) {
        return 0;  // Invalid configuration data
    }

    // Replace these checks with your actual validation logic
    if (config->param1 != 123) return 0;  // Example check for param1
    if (config->param2 != 45.67f) return 0;  // Example check for param2
    if (config->subconfig.subparam1 != 890) return 0;  // Example check for subparam1
    if (config->subconfig.subparam2 != 12.34f) return 0;  // Example check for subparam2

    return 1;  // All parameters are valid
}
