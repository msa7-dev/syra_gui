#ifndef JSON_CONFIG_H
#define JSON_CONFIG_H

#include <stdint.h>

#define CONFIG_MAGIC_HEADER 0xDEADBEEF
#define CONFIG_MAGIC_TAIL   0xBEEFDEAD

typedef struct {
    uint32_t header;  // Magic number for verification
    int param1;
    float param2;
    struct {
        int subparam1;
        float subparam2;
    } subconfig;
    char param3[50];
    uint32_t tail;  // Magic number for verification
} Config;

void load_config(Config *config);
int validate_config(const Config *config);

#endif // JSON_CONFIG_H
