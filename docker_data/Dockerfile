# Use an official Ubuntu as a parent image
FROM ubuntu:20.04

# Set the maintainer label
LABEL maintainer="Srikanth Kompella v.kompella@curtin.edu.au"

# Set environment variables to non-interactive (this prevents some prompts)
ENV DEBIAN_FRONTEND=non-interactive

# Run package updates and install packages
RUN apt-get update \
    && apt-get install -y \
    wget \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Installing gcc-9 (Installs gcc-9.4.0 or gcc-9.5.0)
RUN apt-get remove -y gcc && \
    apt install -y gcc-9 && \
    ln -s /usr/bin/gcc-9 /usr/bin/gcc

# Installing openmpi (Installs openmpi 4.0.3 )
RUN apt-get update
RUN apt install -y libopenmpi-dev

# # Copy the Intel IPP offline installer into the container
# # Replace "your-ipp-installer-file" with the name of your IPP installer file
#COPY ipp.sh /tmp/

# # Run the Intel IPP installer
# RUN ["/bin/bash", "-c", "cd /tmp && chmod +x ipp.sh && ./ipp.sh &&"]

# Installation of python and its libraries
# This step is brought forward as DiFX needs python. 
RUN apt install -y software-properties-common
RUN add-apt-repository -y ppa:deadsnakes/ppa
RUN rm -rf /usr/bin/python3 
RUN apt -y install build-essential
RUN apt install -y python3.7-dev
#Make python and python3 point to python3.7
RUN ln -sf /usr/bin/python3.7 /usr/bin/python
RUN ln -sf /usr/bin/python3.7 /usr/bin/python3

# Installing pip using python3.7 and get-pip.py
#RUN mkdir /tmp
RUN cd /tmp
RUN wget https://bootstrap.pypa.io/get-pip.py
RUN apt-get -y install python3.7-distutils
RUN python get-pip.py

# Using pip to install ipp
# Refer https://www.intel.com/content/www/us/en/docs/oneapi/installation-guide-linux/2023-0/pip.html
RUN pip install ipp-static
#Installing gsl
RUN apt install -y pkg-config
RUN apt install -y libgsl-dev

COPY requirements.txt /tmp/
RUN cd /tmp && \
    pip install -r requirements.txt

# For DiFX both source files and binaries are needed
COPY virtualtrunk /opt/virtualtrunk/

RUN apt install -y bison && \
    apt install -y flex && \
    apt install -y doxygen
RUN chmod -y 770 /opt/virtualtrunk/setup.bash &&
    chmod -y 770 /opt/virtualtrunk/install-difx
SHELL ["/bin/bash", "-c"]
RUN "source /opt/virtualtrunk/setup.bash" && \
    /opt/virtualtrunk/install-difx
SHELL ["/bin/sh", "-c"]

    
    

# IPP files are found here /usr/local/lib
# Make port 80 available to the world outside this container
# EXPOSE 80

# Run any command you like when the container launches
#CMD ["bash"]