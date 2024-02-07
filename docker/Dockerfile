# Use an official Ubuntu as a parent image
FROM ubuntu:latest

# Set the working directory in the container
WORKDIR /home/sykno

# Copy the current directory contents into the container at /home/sykno
COPY . .

# Avoid interactive dialogues from apt-get and set the timezone
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC

# Update and upgrade the system, and install necessary packages
RUN apt-get update -y && apt-get upgrade -y && \
    apt-get install -y apt-utils sudo tzdata usbutils udev \
    wget build-essential checkinstall libreadline-dev \
    libncursesw5-dev libssl-dev libsqlite3-dev tk-dev \
    libgdbm-dev libc6-dev libbz2-dev libffi-dev zlib1g-dev \
    tzdata x11-xserver-utils libusb-1.0-0-dev libftdi1-dev \
    libqt5svg5* libglib2.0-0 libsm6 libxrender1 libxext6 \
    libgl1-mesa-glx build-essential && \
    ln -fs /usr/share/zoneinfo/$TZ /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata && \
    apt-get autoremove -y && apt-get autoclean -y

RUN apt-get update -y && apt-get upgrade -y

RUN cp /home/sykno/mira/setup/udev/99-mira6024_sykno.rules /etc/udev/rules.d/

# Download and install Python 3.11.7
RUN cd /usr/src && \
    wget https://www.python.org/ftp/python/3.11.7/Python-3.11.7.tgz && \
    tar xzf Python-3.11.7.tgz && \
    cd Python-3.11.7 && \
    ./configure --enable-optimizations && \
    make altinstall

# Upgrade pip and install Python packages
RUN python3.11 -m pip install --upgrade pip && \
    python3.11 -m pip install -r /home/sykno/requirements.txt

# Compile Python extensions
RUN cd /home/sykno/mira/proc/mira_cython/ && \
    python3.11 ./setup.py build_ext --inplace && \
    cd -

# Define the command to run the application
# CMD ["sh", "-c", "taskset -c 1 python3.11 -B ./sykno_cli mira-gui"]
