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
RUN apt-get update&&\
    apt install -y software-properties-common &&\
    update-alternatives --install /usr/bin/python python /usr/bin/python3.8 1
#AIPS dependencies
RUN apt-get install -y rsync &&\
    apt-get install -y cvs&&\
    apt-get install -y libtinfo5
# The AIPS image
# AIPS doesn't like running as root
# Create a new group for AIPS users
# Create the 'aips' user and add it to the 'aipsgroup' group
RUN groupadd aipsgroup &&\
    useradd -md /usr/local/aips -s /bin/bash -G aipsgroup aips &&\
# Set the password for the 'aips' user
    echo "aips:aips" | chpasswd


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

RUN apt install -y expect &&\
    cd /usr/local/aips/ && \
    chmod +x script.exp && \
    ./script.exp &&\
    chmod +x LOGIN.SH
