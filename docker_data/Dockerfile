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

# Installing Python packages
COPY requirements.txt /tmp/
RUN cd /tmp && \
    pip install -r requirements.txt

# Installing DiFX
# For DiFX both source files and binaries are needed
# Moving DiFX installation files downloaded using svn co 
COPY virtualtrunk /opt/virtualtrunk/

# Installating DiFX dependencies
RUN apt install -y bison && \
    apt install -y flex && \
    apt install -y doxygen

RUN chmod +x /opt/virtualtrunk/setup.bash && \
    chmod +x /opt/virtualtrunk/install-difx

# You can only source if the shell is /bin/bash
SHELL ["/bin/bash", "-c"]

# Compiling DiFX
RUN source /opt/virtualtrunk/setup.bash && \
    /opt/virtualtrunk/install-difx
SHELL ["/bin/sh", "-c"]

    
# Installing CRAFTConverter    
# Coping CRAFTConverter files
COPY CRAFTConverter /opt/CRAFTConverter/
RUN cd /opt/CRAFTConverter/ && \
    make

# # Installing SCHED
# # Compiled binaries available and environmental 
# # variables will be adjusted

COPY sched_11.5 /opt/sched_11.5/
RUN apt install -y pgplot5
RUN pip install ipython==7.20.0
COPY ASKAP/ /opt/virtualtrunk/sites/ASKAP/

# DIFX_EOPS and DIFX_UTILS will be hardcoded into the container for now
# These variables can be changed by pushing the files as input to relevant
# nextflow processes or may be use containerOptions
# export DIFX_EOPS=/fred/oz002/askap/craft/craco/processing/.eops
# export DIFX_UT1LS=/fred/oz002/askap/craft/craco/processing/.ut1ls

COPY .eops /opt/
COPY .ut1ls /opt/
COPY analysis_scripts/ /opt/analysis_scripts/
COPY astroquery/ /opt/astroquery/
RUN pip install requests
RUN pip install urllib3
COPY craft-python/ /opt/craft-python/
RUN pip install numba
RUN pip install joblib
COPY craft/ /opt/source/craft/

#AIPS dependencies
RUN apt-get install -y rsync
RUN apt-get install -y cvs
RUN apt-get install -y libtinfo5
# The AIPS image
# AIPS doesn't like running as root
# Create a new group for AIPS users
RUN groupadd aipsgroup

# Create the 'aips' user and add it to the 'aipsgroup' group
RUN useradd -md /usr/local/aips -s /bin/bash -G aipsgroup aips

# Set the password for the 'aips' user
RUN echo "aips:aips" | chpasswd


# Set the working directory and switch to 'aips' user
WORKDIR /usr/local/aips
USER aips:aipsgroup



# # Install AIPS 31DEC20
# #ADD	31DEC22 .AIPSRC
# RUN wget ftp://ftp.aoc.nrao.edu/pub/software/aips/31DEC22/install.pl \
#   && chmod 755 install.pl \
#   && rsync rsync://ftp.aoc.nrao.edu/ \
#   && ./install.pl -n



# Setup AIPS
USER root
# RUN	printf '\n\
# sssin           5000/tcp        SSSIN      # AIPS TV server\n\
# ssslock         5002/tcp        SSSLOCK    # AIPS TV Lock\n\
# msgserv         5008/tcp        MSGSERV    # AIPS Message Server\n\
# tekserv         5009/tcp        TEKSERV    # AIPS TekServer\n\
# aipsmt0         5010/tcp        AIPSMT0    # AIPS remote FITS disk access\n\
# aipsmt1         5011/tcp        AIPSMT1    # AIPS remote tape 1\n\
# aipsmt2         5012/tcp        AIPSMT2    # AIPS remote tape 2\n\
# ' >> /root/services &&\
# 	printf '\n# all users should source AIPS\n\
# if [ -f /usr/local/aips/LOGIN.SH ]; then\n\
#   source /usr/local/aips/LOGIN.SH\n\
# fi\n\
# ' >> /etc/bash.bashrc


# Make port 80 available to the world outside this container
# EXPOSE 80

#CMD ["bash"]