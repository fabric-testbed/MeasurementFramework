#!/bin/bash

# Runs all the scripts needed to setup the meas node.

# Install requriremets for ansible - python3, pip3, galaxies etc..
/home/mfuser/mf_git/instrumentize/experiment_bootstrap/install_ansible.sh

# Setup service directories.
mkdir -p /home/mfuser/services
/usr/bin/python3 /home/mfuser/mf_git/instrumentize/experiment_bootstrap/setup_service_dirs.py 

