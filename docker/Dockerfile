# Default build arguments
ARG CONFIG="default"

# Install different packages based on the CONFIG argument
# RUN if [ "$CONFIG" = "dev" ]; then \
    #   apt-get update && apt-get install -y package-for-dev; \
    # elif [ "$CONFIG" = "prod" ]; then \
    #   apt-get update && apt-get install -y package-for-prod; \
    # else \
    #   echo "Default configuration - no additional packages installed"; \
    # fi
# 
# docker build --build-arg CONFIG=dev -t my-image:dev .
# docker build --build-arg CONFIG=prod -t my-image:prod .
# sudo apt-get install x11-xserver-utils


# Use an official Ubuntu as a parent image
FROM ubuntu:latest

# Set the working directory in the container
WORKDIR /home/sykno

# Copy the current directory contents into the container at /home/sykno
COPY . .

# Avoid interactive dialogues from apt-get and set the timezone
ENV DEBIAN_FRONTEND=noninteractive

# Update and upgrade the system
RUN apt-get update -y && apt-get upgrade -y && apt-get install -y apt-utils tzdata
RUN ln -fs /usr/share/zoneinfo/$TZ /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata

ENV TZ=UTC

# Install udev and copy udev rules
RUN apt-get update -y && apt-get install -y udev && \
    cp ./mira/setup/udev/99-mira6024_sykno.rules /etc/udev/rules.d/ && \
    chmod 644 /etc/udev/rules.d/99-mira6024_sykno.rules && \
    chown root:root /etc/udev/rules.d/99-mira6024_sykno.rules

# Install necessary packages for building Python
RUN apt-get install -y wget build-essential checkinstall \
    libreadline-dev libncursesw5-dev libssl-dev libsqlite3-dev \
    tk-dev libgdbm-dev libc6-dev libbz2-dev libffi-dev zlib1g-dev \
    tzdata x11-xserver-utils

# Download and compile Python 3.12.1
RUN cd /usr/src && \
    wget https://www.python.org/ftp/python/3.12.1/Python-3.12.1.tgz && \
    tar xzf Python-3.12.1.tgz && \
    cd Python-3.12.1 && \
    ./configure --enable-optimizations && \
    make altinstall

# Install other necessary packages
RUN apt-get update && apt-get install -y \
    libusb-1.0-0-dev \
    libftdi1-dev \
    libqt5svg5* \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libgl1-mesa-glx \
    build-essential

# Upgrade pip and install Python packages
RUN cd /home/sykno/ && \
    python3.12 -m pip install --upgrade pip && \
    python3.12 -m pip install -r ./requirements.txt

RUN cd /home/sykno/mira/proc/mira_cython/ && \
    python3.12 ./setup.py build_ext --inplace && \
    cd -

# Clean up
RUN apt-get autoremove -y && apt-get autoclean -y

# Define the command to run the application (uncomment the desired CMD line)
# CMD ["python3.12", "./mira/proc/mira_cython/setup.py", "build_ext", "--inplace"]
CMD ["python3.12", "-B", "./sykno_cli", "mira-gui"]
# CMD ["python", "app.py"]
