
# Overview
This directory contains the needed files for creating omni in a docker container.  
The container is meant to simplify the use of OMNI without having to go through the install and its dependencies.  
It has just been tested for a few omni-commands used below.  

See [GENI OMNI Tutorial](https://groups.geni.net/geni/wiki/GENIExperimenter/Tutorials/RunHelloOmni) and
and [OMNI Install Quickstart](https://github.com/GENI-NSF/geni-tools/wiki/QuickStart) for more information.

# Build Docker Container
To build use `docker build . -t omni_image` 

# Use

Place the omni_bundle(downloaded from the Portal)  in a directory on your machine and run the docker container from that directory.
 
`docker run --rm -w /root/working --mount type=bind,source=$PWD,target=/root/working -it omni_image /bin/bash`

This will start the command prompt running omni as `root@containerid:~/working# `
# Commands
## configure using  
    `omni-configure`
## get the slice inventory by using 
    `readyToLogin <slice-name> --useSliceAggregates --ansible-inventory -o`
~                                                                               
