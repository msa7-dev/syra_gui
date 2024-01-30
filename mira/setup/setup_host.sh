#!/bin/zsh
#
sudo apt-get update && sudo apt-get upgrade -y
#
## Install Python and pip
sudo apt install -y python3 python3-pip
pip --version 
#
## Install git
sudo apt install -y git
git --version
#
sudo apt-get install openssh-client sshpass

RED='\033[0;31m'
GREEN='\033[0;32m'

if [ $# -ne 1 ]; then
    echo "Usage: $0 <argument>"
    exit 1
fi

case $1 in
  'mira')
    echo -e "${GREEN}You selected Sykno MiRa6024 Setup installation."
    dir='MiRa6024'
    arg='mira'
    ;;
  'vira')
    echo -e "${GREEN}You selected Sykno ViRa24 Setup installation."
    echo -e "${RED}TODO"
    dir='ViRa24'
    arg='vira'
    ;;
  'rara')
    echo "You selected case 3."
    # Add your commands here
    ;;
  'rara')
    echo "You selected case 4."
    # Add your commands here
    ;;
  *)
    echo "Invalid selection. Please select either 'mira', 'vira', 'rara', or 'rara'."
    exit 1
    ;;
esac

# Set the necessary variables
HOST="sykno-pi"
USER="sykno"
PASSWORD="syknoerl"
SETUP_SOURCE_FILE="./setup_rapi.sh"
ALIAS_SOURCE_FILE="./alias.zsh"
DESTINATION_FILE="/home/sykno/$dir/"

sypi='alias sypi='sshpass -p "syknoerl" ssh -o StrictHostKeyChecking=no "sykno@sykno-pi"''
# Check if the alias command already exists in .bashrc
if grep -Fxq "$sypi" ~/.oh-my-zsh/custom/alias.zsh; then
    echo "Alias command already exists in .oh-my-zsh/custom/alias.zsh"
else
    # Append the alias command to .bashrc
    echo "$sypi" >> ~/.oh-my-zsh/custom/alias.zsh
    echo "Alias command added to .oh-my-zsh/custom/alias.zsh"
fi

#source ~/.zshrc

sshpass -p "syknoerl" ssh -o StrictHostKeyChecking=no "sykno@sykno-pi" "mkdir /home/sykno/$dir"

# Transfer the file using sshpass and scp
sshpass -p "$PASSWORD" scp "$SETUP_SOURCE_FILE" "$USER@$HOST:$DESTINATION_FILE" 
sshpass -p "$PASSWORD" scp "$ALIAS_SOURCE_FILE" "$USER@$HOST:$DESTINATION_FILE" 

sshpass -p "syknoerl" ssh -o StrictHostKeyChecking=no sykno@sykno-pi "chmod +x /home/sykno/$dir/setup_rapi.sh && echo syknoerl | sudo -S /home/sykno/$dir/setup_rapi.sh ${arg}"




