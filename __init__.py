import sys
from loguru import logger
from pathlib import Path

MIRA_SYS_CONFIG_PATH = Path("./mira/config/emra_sys_config.ini").resolve()
if MIRA_SYS_CONFIG_PATH.is_file():
    pass
else:
    logger.error(f'Error 404: System configuration file not found! Searched here: {MIRA_SYS_CONFIG_PATH}')
    sys.exit()
