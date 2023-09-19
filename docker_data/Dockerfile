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
# COPY ipp.sh /tmp/

# # Run the Intel IPP installer
# RUN ["/bin/bash", "-c", "cd /tmp && chmod +x ipp.sh && ./ipp.sh"]

# Installing pip
RUN apt install -y pip
# Using pip to install ipp
# Refer https://www.intel.com/content/www/us/en/docs/oneapi/installation-guide-linux/2023-0/pip.html
RUN pip install ipp
#Installing gsl
RUN apt install -y libgsl-dev

# DiFX needs python
#apt install software-properties-common
#add-apt-repository -y ppa:deadsnakes/ppa
#apt install python3.7



# For DiFX both source files and binaries are needed


# IPP files are found here /usr/local/lib
# Make port 80 available to the world outside this container
# EXPOSE 80

# Run any command you like when the container launches
#CMD ["bash"]