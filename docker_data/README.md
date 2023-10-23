# Documentation

CELEBI workflow makes use of multiple packages and scripts that enable necessary seamless computation of FRB data. This compute environment, which was earlier located on OzStar supercomputer, is containerized to make the workflow more portable. The files in this folder constitute the data necessary to rebuild the docker container. This documentation details: 

_i) How the containers were built and their contents. 
ii) Different approaches to invoking the containers, 
iii) Calling packages (CASA)_

## Building the containers

Two singularity/docker container images were built as a part of this work. The first image, labelled `celebi_latest.sif`, contains all the packages used in the CELEBI pipeline. These include, but not limited to, `AIPS`, `Parseltongue3`, `DiFX`, `CASA`, `sched_11.5`, `gcc`, `python3.8`, `astropy`, `numba`,`openmpi`, `IPP`, `GSL`, `CRAFTConverter`, and the necessary python scripts (the locations of which were added to PYTHONPATH or PATH as per the need). The second images (`aipsonly_1.0.sif`) is relatively lean and contains only `AIPS` and `Parseltongue3`. Both the container images were built on Ubunutu:20.04 docker image, and were later pulled onto Ngarrgu Tindebeek (NT) using `singularity pull docker_image_address`. (For example: `singularity pull docker://srikanthkom/aipsonly:1.0`). 

## Invoking the containers



## What's in this folder

The folder contains multiple files that are used in the process of building the container. 

1. `.AIPSRC`: contains AIPS installation settings that were used during the installation process of AIPS. This file was directly copied to the home folder within the container to prevent AIPS prompts.
2. `Dockerfile`: This file was used to build the container using docker.
3. `Makefile`: This makefile was generated using `configureLinux64gfortran` in `/opt/sched_11.5/src` folder in the container.
4. `requirements.txt`: This was used to install reqiured packages using pip. 
5. `script.exp`: AIPS configuration as described in http://www.aips.nrao.edu/install.shtml requires post-installation configuration which generates multiple prompts. These prompts are answered with `expect` package, which in turn makes use of this script.
6. `setup_proc_container`: This file helps in setting up the environment variables and sources `LOGIN.SH` (for AIPS) and `setup.bash` (for DiFx). 

The files, `.AIPSRC`, `Makefile`, `requirements.txt`, `script.exp`, `setup_proc_container`, were copied onto the container during the container building process. These files are necessary if one attempts to rebuild the containers. The locations to which these files are copied can be found against the `COPY` command in the `Dockerfile`. 
