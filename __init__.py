import sys
from loguru import logger
from pathlib import Path

sys_config_pahts = [Path("./radar_eval/config/radar_sys_config.ini").resolve()]
for n, path in enumerate(sys_config_pahts):
    if path.is_file():
        MIRA_SYS_CONFIG_PATH = path
        break
    elif n == len(sys_config_pahts)-1:
        logger.error(f'Error 404: System configuration file not found! Searched here: {path}')
        sys.exit()
