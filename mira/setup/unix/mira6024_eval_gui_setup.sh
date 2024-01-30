#!/bin/zsh
#!/bin/bash

# 1. Setup the Python environment via Poetry
echo "Setting up Python environment for Sykno - MiRa6024|1A..."
# curl -sSL https://install.python-poetry.org | python3 -
# sudo poetry install

# 2. Move udev rules for a USB device into the correct directory
UDEV_RULES_SRC="/home/jurnijasted/coding/sykno/py/mira/"  # Please replace this with the path to your udev rules
UDEV_RULES_DEST="/etc/udev/rules.d/"
echo "Copying udev rules for the MiRa6024|1A USB device..."
echo "Source: $UDEV_RULES_SRC"
echo "Destination: $UDEV_RULES_DEST"
sudo cp "$UDEV_RULES_SRC" "$UDEV_RULES_DEST"
sudo udevadm control --reload-rules && sudo udevadm trigger
echo "MiRa6024|1A udev rules copied and reloaded."

# 3. Append new alias commands to the .bashrc file
echo "Appending aliases to .bashrc..."
ALIASES="
# Sykno MiRa6024|1A aliases
alias py='cd ~/sykno/py'
alias sykno='cd ~/sykno'
alias mira='cd ~/sykno/py/mira'
alias sypi='sshpass -p "syknoerl" ssh -o StrictHostKeyChecking=no "sykno@sykno-pi"'
alias mira='cd ~/sykno/py && sudo taskset -c 1 nice -n -20 python3 -B ./cli_Sykno mira-gui'
# Add more aliases as needed
"
echo "$ALIASES" >> ~/.bashrc
echo "Added the following aliases to ~/.bashrc:"
echo "$ALIASES"
source ~/.bashrc

# 4. Execute a Python script
PYTHON_SCRIPT="/home/jurnijasted/coding/sykno/py/cli_Sykno"  # Please replace this with the path to your Python script
echo "Executing the Python script..."
echo "Script path: $PYTHON_SCRIPT"
gnome-keyring-daemon --unlock
sudo -E taskset -c 1 nice -n -20 poetry run python3 -B $PYTHON_SCRIPT mira-gui
