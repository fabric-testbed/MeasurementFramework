#!/bin/bash
set -euo pipefail

# Rebuilds meas_node_binaries.tgz from scratch.
#
# Run this ONCE on a throwaway reference machine that matches the meas-node
# base image (same Ubuntu release, same default python3 version) as the
# nodes this tarball will later be extracted onto. Re-run it whenever that
# base image changes -- the tarball hardcodes a python3.X site-packages
# path, so a python version drift between build machine and target node is
# exactly what breaks "ansible-playbook" with ModuleNotFoundError.
#
# Must be run as mfuser (matches the ownership install_ansible.sh expects).

if [ "$(whoami)" != "mfuser" ]; then
  echo "This must be run as mfuser (current user: $(whoami)). Aborting." >&2
  exit 1
fi

HOME_BASE="/home/mfuser"
MF_GIT="$HOME_BASE/mf_git"
REQUIREMENTS_TXT="$MF_GIT/instrumentize/prometheus/ansible/roles/fabric_experiment/meta/requirements.txt"
REQUIREMENTS_YML="$MF_GIT/instrumentize/prometheus/ansible/roles/fabric_experiment/meta/requirements.yml"
OUT_TGZ="$MF_GIT/instrumentize/experiment_bootstrap/meas_node_binaries.tgz"

echo "-----Updating apt-----"
sudo apt update

echo "-----Installing pip3-----"
sudo apt install -y python3-pip
pip3 --version

echo "-----Installing python requirements-----"
# --break-system-packages: needed on Ubuntu 24.04+ (PEP 668); harmless no-op
# flag is unavailable on older pip, so pin an image where it's supported.
python3 -m pip install --user --break-system-packages -r "$REQUIREMENTS_TXT"

export PATH="$PATH:$HOME_BASE/.local/bin"

echo "-----Install Galaxy Roles-----"
ansible-galaxy install -r "$REQUIREMENTS_YML"

echo "-----Install Galaxy Collections-----"
ansible-galaxy collection install -r "$REQUIREMENTS_YML"

echo "-----Recording build metadata-----"
BUILD_INFO="$HOME_BASE/.mf_binaries_build_info"
{
  echo "built_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "python3_version=$(python3 --version 2>&1)"
  echo "ansible_version=$(ansible --version | head -1)"
  grep -E '^(NAME|VERSION)=' /etc/os-release
} > "$BUILD_INFO"
cat "$BUILD_INFO"

echo "-----Packaging tarball-----"
tar czf "$OUT_TGZ" -C / \
  home/mfuser/.local \
  home/mfuser/.ansible \
  home/mfuser/.mf_binaries_build_info

echo "-----Finished! Wrote $OUT_TGZ-----"
echo "Commit this file and instrumentize/experiment_bootstrap/meas_node_binaries.tgz together."
