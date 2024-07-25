#!/bin/bash

# Define the udev rules file name and paths
RULES_FILE="99-sykno_usb_device.rules"
SOURCE_DIR="./radar_eval/setup/unix/udev/"
DEST_DIR="/etc/udev/rules.d"

# Full paths
SOURCE_PATH="${SOURCE_DIR}/${RULES_FILE}"
DEST_PATH="${DEST_DIR}/${RULES_FILE}"

# Function to move the udev rules file and reload udev
move_and_reload_udev() {
    echo "Moving ${RULES_FILE} to ${DEST_DIR}"
    sudo cp "${SOURCE_PATH}" "${DEST_PATH}"
    echo "Reloading udev rules"
    sudo udevadm control --reload-rules
    echo "Triggering udev"
    sudo udevadm trigger
}

# Check if the udev rules file exists in the destination directory
if [ -f "${DEST_PATH}" ]; then
    echo "${RULES_FILE} already exists in ${DEST_DIR}"
else
    # Check if the udev rules file exists in the source directory
    if [ -f "${SOURCE_PATH}" ]; then
        move_and_reload_udev
    else
        echo "${RULES_FILE} not found in ${SOURCE_DIR}"
        exit 1
    fi
fi

sudo apt-get install hdf5-tools

echo "Done"
