FROM ubuntu:18.04

# Disable interactive for apt installs
ARG DEBIAN_FRONTEND=noninteractive
# Install omni requirements
RUN apt-get update && \
	  apt-get install -y python-m2crypto python-dateutil \
          python-openssl libxmlsec1 xmlsec1 \
          libxmlsec1-openssl libxmlsec1-dev


# A little confusing here since gcf is also a dir in geni-tools-2.11. Appearently geni-tool-2.11 same as gcf?
# Copy in omni code
COPY ./geni-tools-2.11 /usr/local/bin/gcf
# Setup omni paths and aliases
COPY ./bashrc /root/.bashrc

# Just put everything in single directory and map that directory to all the omni defaults.
RUN mkdir /root/working
RUN ln -s /root/working /root/.gcf 
RUN ln -s /root/working /root/Downloads

# To use place the omni_bundle in a directory on your machine and run this from that directory.
# 
# docker run --rm -w /root/working --mount type=bind,source=$PWD,target=/root/working -it omni_image /bin/bash
 
# configure using  
#    omni-configure
# get the slice inventory by using 
#    readyToLogin <slice-name> --useSliceAggregates --ansible-inventory -o
