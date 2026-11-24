#!/bin/bash

# Runs all the scripts needed to setup the meas node.

LOG_FILE="/home/mfuser/bootstrap.log"
exec > >(tee -a "$LOG_FILE") 2>&1

echo "===== [$(date -u +%FT%TZ)] bootstrap.sh starting (log: $LOG_FILE) ====="

# Add  path for local bin so ansible commands are available
echo PATH=$PATH:/home/mfuser/.local/bin >> /home/mfuser/.bashrc

echo "----- [$(date -u +%FT%TZ)] Installing ansible -----"
# Install requriremets for ansible - python3, pip3, galaxies etc..
/home/mfuser/mf_git/instrumentize/experiment_bootstrap/install_ansible.sh

echo "----- [$(date -u +%FT%TZ)] Setting up service directories -----"
# Setup service directories.
mkdir -p /home/mfuser/services
/usr/bin/python3 /home/mfuser/mf_git/instrumentize/experiment_bootstrap/setup_service_dirs.py

echo "===== [$(date -u +%FT%TZ)] bootstrap.sh finished ====="

