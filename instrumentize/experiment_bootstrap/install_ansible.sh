#!/bin/bash
#echo "-----Updating apt-----"
#sudo apt update   
#echo "-----Installing pip3-----"
#sudo apt install -y python3-pip   
#pip3 --version 
#echo "-----Installing python requirements-----"

##pip3 install -r /home/mfuser/mf_git/instrumentize/prometheus/ansible/roles/fabric_experiment/meta/requirements.txt

#pip install ansible 
# Not sure why need to hard code full path here
#/home/mfuser/.local/bin/pip --version 
#/home/mfuser/.local/bin/ansible --version 
#/home/mfuser/.local/bin/ansible-galaxy --version 
 

##echo "-----Install Galaxy Roles-----"
##/home/mfuser/.local/bin/ansible-galaxy install -r /home/mfuser/mf_git/instrumentize/prometheus/ansible/roles/fabric_experiment/meta/requirements.yml
##echo "-----Install Galaxy Collections----"
##/home/mfuser/.local/bin/ansible-galaxy collection install -r /home/mfuser/mf_git/instrumentize/prometheus/ansible/roles/fabric_experiment/meta/requirements.yml

# Pinned to a specific pre-built tarball for the node's base image. Update
# this whenever the meas-node base image changes -- see
# meas_node_binaries/README.md for how these are built and why they're
# image-specific (a tarball built for the wrong python3.X version breaks
# ansible with ModuleNotFoundError).
MEAS_NODE_BINARIES_TGZ="/home/mfuser/mf_git/instrumentize/experiment_bootstrap/meas_node_binaries/meas_node_binaries_default_ubuntu_24.tgz"

tar xzf "$MEAS_NODE_BINARIES_TGZ" -C /
chown -R mfuser:mfuser /home/mfuser/.local /home/mfuser/.ansible

#echo "pip freeze:"
#pip freeze

echo "-----Finished!-----" 
