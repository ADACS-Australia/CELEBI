# Documentation

CELEBI workflow makes use of multiple packages and scripts that enable necessary seamless computation of FRB data. This compute environment, which was earlier located on OzStar supercomputer, is containerized to make the workflow more portable. The files in this folder constitute the data necessary to rebuild the docker container. This documentation details: 

# Table of Contents

- [Documentation](#documentation)
  - [Building the Containers](#building-the-containers)
  - [Invoking the Containers](#invoking-the-containers)
  - [Examples](#examples)
    - [Running CASA in the Container](#running-casa-in-the-container)
  - [Known Issues](#known-issues)
  - [What's in this Folder](#whats-in-this-folder)




## Building the containers

Two singularity/docker container images were built as a part of this work. The first image, labelled `celebi_latest.sif`, contains all the packages used in the CELEBI pipeline. These include, but not limited to, `AIPS`, `Parseltongue3`, `DiFX`, `CASA`, `sched_11.5`, `gcc`, `python3.8`, `astropy`, `numba`,`openmpi`, `IPP`, `GSL`, `CRAFTConverter`, and the necessary python scripts (the locations of which were added to PYTHONPATH or PATH as per the need). The second images (`aipsonly_1.0.sif`) is relatively lean and contains only `AIPS` and `Parseltongue3`. Both the container images were built on Ubunutu:20.04 docker image, and were later pulled onto Ngarrgu Tindebeek (NT) using `singularity pull docker_image_address`. (For example: `singularity pull docker://srikanthkom/aipsonly:1.0`). 

## Invoking the containers

The containers can be run in different ways as detailed below (after you have run `module load apptainer`) : 

1. Using Singularity shell: `singularity (or apptainer) shell image_name.sif` runs shell within the container and allows you to interact with the contents of the container.
   
2. Using singularity run or exec: `singularity run image_name.sif command` executes the command as if it were run using the container environment. 
   
3. Using a sandbox: A sandbox can be created using `singularity build --sandbox sandbox_name/ image.sif`. The sandbox can then be used as described above, however, you can use --writable flag when running the sandbox, and whatever changes you make in the sandbox remain. For example, if you open the sandbox using `singularity shell sandbox_name`, and create a directory inside it, exit it, and then open it again using `singularity shell ..`, you should be able to see the directory created. Additionally, once you make the necessary changes you can build a container image(*.sif) using the sandbox by running `singularity build my_image.sif my_sandbox/`.

A sandbox is necessary to run AIPS as AIPS requires rw file system. Any code that fails to run with a standard image *.sif due to filesystem permissions should be run in sandbox with `--writable` flag.

## Examples

A folder named `tests/` in the parent folder contains a sample nextflow workflow(`testflow.nf`), config file (`nextflow.config`), a sample python script (`testfile.py`) that generates an output file (`version.txt`) containing the version of the python package that invokes it. `testflow.nf` script when invoked using ` nextflow run testflow.nf -with-singularity celebi_sandbox/` runs the code in the process definition on the container. Note that the `--writable` flag is added under `containerOptions` in the process defintion. This nextflow script tests whether AIPS is working in the container or not. The python script can be invoked using `singularity run --writable --bind /fred/oz002/askap/craft/craco/processing/containers:/usr/local/ aips_sandbox/  bash -c " cd /usr/local/ && python /usr/local/testfile.py"`. In this example the host folder (`.../containers`) is bound to `/usr/local`, but you can use any other folder that exists in the container. 

### Running CASA in the container

Since CASA is installed as a python package, the mode of execution is slightly different. The modules necessary are imported in the beginning of the python script (for example to use `imstat` you should do `from casatasks import imstat` and then call imstat as usual). The script which was earlier invoked using `casa casaimstat.py` should now be invoked using `python casaimstat.py`. `tests/` folder holds a sample python script for casa (`casaimstat.py`), and `testcasa` which is in the same folder calls this script.


## Known issues

1. Integration of containers with nextflow: Filesystem issues popped up when the container sandbox (using --writable flag) was integrated with nextflow. Although, there are no issues in executing `singularity run --writable sandbox/` from the terminal.
2. rw permissions and AIPS: AIPS required rw permissions on the filesytem ,this entailed *.sif images cannot be directly invoked and a sandbox approach was implemented as a workaround.
3. However, if multiple parallel processes read and write to the sandbox simultaneouly,fitld 8 errors show up. A quick and dirty workaround for this is to use multiple sandbox containers, either by building them on the fly, or by having multiple standalone versions such that different nextflow processes call different containers. An untested idea is to create a lag between the processes (using `sleep`) to ensure no two processes are doing the same thing at the same time.


## What's in this folder

The folder contains multiple files that are used in the process of building the container. 

1. `.AIPSRC`: contains AIPS installation settings that were used during the installation process of AIPS. This file was directly copied to the home folder within the container to prevent AIPS prompts.
2. `Dockerfile`: This file was used to build the container using docker.
3. `Makefile`: This makefile was generated using `configureLinux64gfortran` in `/opt/sched_11.5/src` folder in the container.
4. `requirements.txt`: This was used to install reqiured packages using pip. 
5. `script.exp`: AIPS configuration as described in http://www.aips.nrao.edu/install.shtml requires post-installation configuration which generates multiple prompts. These prompts are answered with `expect` package, which in turn makes use of this script.
6. `setup_proc_container`: This file helps in setting up the environment variables and sources `LOGIN.SH` (for AIPS) and `setup.bash` (for DiFx). 

The files, `.AIPSRC`, `Makefile`, `requirements.txt`, `script.exp`, `setup_proc_container`, were copied onto the container during the container building process. These files are necessary if one attempts to rebuild the containers. The locations to which these files are copied can be found against the `COPY` command in the `Dockerfile`. 
