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

# The tarball's ~/.local/lib/python3.X/site-packages is built for one
# specific python3 minor version (see MEAS_NODE_BINARIES_TGZ comment
# above). If this node's actual python3 doesn't match -- wrong/missing
# os_image_* marker, or no tarball built for this image yet -- ansible
# ends up unimportable (ModuleNotFoundError: No module named 'ansible')
# even though the `ansible` command exists. Verify it actually works and
# fall back to a real pip install (the original approach, before the
# tarball) for this node's own python3 if not.
echo "-----Verifying ansible install-----"
if /usr/bin/python3 -c "import ansible" 2>/dev/null; then
  echo "ansible is importable by $(/usr/bin/python3 --version 2>&1) -- tarball matched this node."
else
  echo "WARNING: ansible from $MEAS_NODE_BINARIES_TGZ is not importable by $(/usr/bin/python3 --version 2>&1) (version mismatch) -- falling back to pip install."

  if ! /usr/bin/python3 -m pip --version >/dev/null 2>&1; then
    echo "pip3 not found -- installing python3-pip."
    sudo apt-get update -qq && sudo apt-get install -y -qq python3-pip
  fi

  PIP_EXTRA_ARGS=""
  if find /usr/lib/python3*/EXTERNALLY-MANAGED /usr/lib64/python3*/EXTERNALLY-MANAGED >/dev/null 2>&1; then
    PIP_EXTRA_ARGS="--break-system-packages"
  fi
  /usr/bin/python3 -m pip install --user $PIP_EXTRA_ARGS ansible

  if /usr/bin/python3 -c "import ansible" 2>/dev/null; then
    echo "ansible installed successfully via pip fallback."
  else
    echo "ERROR: ansible still not importable after pip fallback."
  fi
fi

echo "-----Finished!-----"
