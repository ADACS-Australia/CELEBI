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

# Python 3.7 install
RUN apt install -y software-properties-common &&\
    apt install -y pip &&\
    pip install --timeout=300 ipp-static
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

RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.8 1


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
#Installing ipython using requirements.txt
#RUN pip install ipython==7.20.0
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
RUN add-apt-repository ppa:kettenis-w/parseltongue &&\
    apt-get update && \
    apt-get install -y python3-parseltongue

USER aips:aipsgroup
ADD .AIPSRC .AIPSRC

RUN wget ftp://ftp.aoc.nrao.edu/pub/software/aips/31DEC23/install.pl \
  && chmod 755 install.pl \
  && ./install.pl -n

USER root
RUN apt-get update &&\
    apt install -y vim

# Configuring AIPS using the expect script which provides inputs for the
# prompts from AIPS commands. 
COPY services /root/services
COPY script.exp /usr/local/aips/

RUN apt install -y expect
RUN cd /usr/local/aips/ && \
    chmod +x script.exp && \
    ./script.exp &&\
    chmod +x LOGIN.SH
COPY setup_proc_container /opt/
COPY sourcing.sh /opt/
RUN chmod +x /opt/sourcing.sh && \
    chmod +x /opt/setup_proc_container 
RUN chmod -R 777  /usr/local/aips/*
# ENTRYPOINT ["/opt/sourcing.sh"]
#RUN useradd -md /usr/local/aips -s /bin/bash -G aipsgroup vkompell

# Compiling Sched_11.5

RUN apt-get install -y libpng-dev &&\
    apt-get install -y libx11-dev

COPY Makefile /opt/sched_11.5/src/

RUN export PGPLOT_DIR=/usr/lib/pgplot5 &&\
    cd /opt/sched_11.5/src/ &&\
    make clean &&\
    make 
RUN chmod -R 777 /opt/sched_11.5
#Installing casa using pip
RUN pip install \
    casatools==6.6.0.20 \
    casatasks==6.6.0.20 \
    casaplotms==2.2.4 \
    casaviewer==1.9.1 \
    casampi==0.5.4 \
    casashell==6.6.0.20 \
    casadata==2023.9.18 \
    casaplotserver==1.7.1 \
    almatasks==1.7.1 \
    casatestutils==6.6.0.20 \
    casatablebrowser==0.0.33 \
    casalogger==1.0.17 \
    casafeather==0.0.20
    


    
    

