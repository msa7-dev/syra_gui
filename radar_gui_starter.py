import sys
import os
from loguru import logger
# Add the dependencies folder to the system path
script_dir = os.path.dirname(__file__)

# Go back four directories
for _ in range(3):
    script_dir = os.path.dirname(script_dir)

# Construct the path to the dependencies folder
dependencies_path = os.path.join(script_dir)

# Add the dependencies folder to the system path
sys.path.append(dependencies_path)

import __init__

# Import the required modules from the dependencies folder
try:
    import radar_eval.gui.radar_eval_qt_gui as mira_eval_gui
except ImportError as e:
    logger.debug(f"ImportError: {e}")
    sys.exit(1)

# Execute the function
try:
    mira_eval_gui.MIRA_MAIN_GUI.mira_gui_main()
except Exception as e:
    logger.debug(f"Error: {e}")
    sys.exit(1)
