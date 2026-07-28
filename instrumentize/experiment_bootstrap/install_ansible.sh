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

HOME_BASE="/home/mfuser"
BINARIES_DIR="$HOME_BASE/mf_git/instrumentize/experiment_bootstrap/meas_node_binaries"

# Default pre-built tarball, used when the node's base image can't be
# identified or no tarball has been built for it yet. Update this whenever
# the default meas-node base image changes -- see meas_node_binaries/README.md
# for how these are built and why they're image-specific (a tarball built for
# the wrong python3.X version breaks ansible with ModuleNotFoundError).
MEAS_NODE_BINARIES_TGZ="$BINARIES_DIR/meas_node_binaries_default_ubuntu_24.tgz"

# FABRIC images drop an empty marker file named os_image_<image_name> in
# mfuser's home dir identifying the base image the node was built from. If a
# tarball built for that exact image exists, prefer it over the default.
OS_IMAGE_MARKER=$(find "$HOME_BASE" -maxdepth 1 -name 'os_image_*' -print -quit)
if [ -n "$OS_IMAGE_MARKER" ]; then
  IMAGE_NAME="$(basename "$OS_IMAGE_MARKER")"
  IMAGE_NAME="${IMAGE_NAME#os_image_}"
  CANDIDATE_TGZ="$BINARIES_DIR/meas_node_binaries_${IMAGE_NAME}.tgz"
  if [ -f "$CANDIDATE_TGZ" ]; then
    MEAS_NODE_BINARIES_TGZ="$CANDIDATE_TGZ"
    echo "Found $OS_IMAGE_MARKER -- using image-specific tarball $MEAS_NODE_BINARIES_TGZ"
  else
    echo "Found $OS_IMAGE_MARKER but no matching tarball ($CANDIDATE_TGZ) -- falling back to default $MEAS_NODE_BINARIES_TGZ"
  fi
fi

tar xzf "$MEAS_NODE_BINARIES_TGZ" -C /
chown -R mfuser:mfuser /home/mfuser/.local /home/mfuser/.ansible

#echo "pip freeze:"
#pip freeze

echo "-----Finished!-----" 
