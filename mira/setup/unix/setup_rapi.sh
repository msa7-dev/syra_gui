#!/bin/bash
userToken="glpat-s65JavBxs6TYvc582VAm"

RED='\033[0;31m'
GREEN='\033[0;32m'

if [ $# -ne 1 ]; then
    echo "Usage: $0 <argument> \n <argument> => 'mira', 'vira', 'rara', or 'rara'"
    exit 1
fi

case $1 in
  'mira')
    echo -e "${GREEN}You selected Sykno MiRa6024 Setup installation."
    gitRepo='fp_jan_py'
    piDir='MiRa6024'
    arg='mira'
    udevName=mira6024
    guiCmd=mira-gui
    ;;
  'vira')
    echo -e "${GREEN}You selected Sykno ViRa24 Setup installation."
    echo -e "${RED}TODO"
    piDir='ViRa24'
    arg='vira'
    udevName=vira24
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

sudo apt-get update && sudo apt-get upgrade -y

# Install required packages
#sudo apt-get install -y git curl jq libusb-1.0-0-dev

cd /home/sykno/$piDir

git clone https://oauth2:$userToken@gitlab.com/sykno/$gitRepo.git py

cd /home/sykno/$piDir/py

pip install --upgrade pip
pip --version

pip install poetry
poetry --version

poetry init

poetry install

# Create udev rules file
echo 'SUBSYSTEM=="usb", MODE="0666"' | sudo tee /etc/udev/rules.d/99-$udevName.rules

# Reload udev rules
sudo udevadm control --reload-rules
sudo udevadm trigger


sudo touch /etc/vnc/config.custom
sudo bash -c 'echo "vncserver-x11-serviced.service" >> /etc/vnc/config.custom'

sudo systemctl enable vncserver-x11-serviced.service

sudo apt update

sudo apt install -y zsh

sudo chsh -s /usr/bin/zsh

sudo apt install curl

sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh -y)"

mv /home/sykno/$piDir/alias.zsh /home/sykno/.oh-my-zsh/custom/alias.zsh

echo 'alias start_'${arg}'=cd /home/sykno/'${piDir}'/py && poetry shell && python /home/sykno/'${piDir}'/py/cli_Sykno '${mira_gui}'' >> /home/sykno/.oh-my-zsh/custom/alias.zsh
 
source /home/sykno/.zshrc

sudo reboot