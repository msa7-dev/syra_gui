#!/bin/bash

sudo apt-get update -y
sudo apt-get upgrade
sudo apt-get dist-upgrade

sudo apt-get install build-essential libncurses5-dev libncursesw5-dev libreadline6-dev libdb5.3-dev libgdbm-dev libc6-dev libbz2-dev libexpat1-dev liblzma-dev zlib1g-dev libsqlite3-dev tk-dev libssl-dev openssl libffi-dev -y

mkdir Python-Installation
cd Python-Installation

wget https://www.python.org/ftp/python/3.10.2/Python-3.10.2.tgz
tar xzvf Python-3.10.2.tgz
rm -f Python-3.10.2.tgz

cd Python-3.10.2
sudo ./configure --enable-optimizations
sudo make -j 4
sudo make altinstall

cd ../..
sudo rm -rf Python-Installation

sudo apt-get --purge remove build-essential libncurses5-dev libncursesw5-dev libreadline6-dev libdb5.3-dev libgdbm-dev libc6-dev libz2-dev libexpat1-dev liblzma-dev zlib1g-dev libsqlite3-dev tk-dev libssl-dev openssl libffi-dev -y
sudo apt-get autoremove -y
sudo apt-get clean

python3.10.2 -m pip install --upgrade pip
sudo echo 'alias python3="python"' >> ~/.bashrc
sudo echo 'alias python="python3.10.2"' >> ~/.bashrc
sudo echo 'alias pip3="pip"' >> ~/.bashrc
sudo echo 'alias pip="python3.10.2 -m pip"' >> ~/.bashrc
source ~/.bashrc

