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

# Optional: name of the FABRIC image this was built on (e.g. default_ubuntu_24),
# passed in as $1. Tagged onto the tarball's filename so it's obvious which
# image a given tarball was built against without having to extract it first.
IMAGE_NAME="${1:-}"
BINARIES_DIR="$MF_GIT/instrumentize/experiment_bootstrap/meas_node_binaries"
if [ -n "$IMAGE_NAME" ]; then
  OUT_TGZ="$BINARIES_DIR/meas_node_binaries_${IMAGE_NAME}.tgz"
else
  OUT_TGZ="$BINARIES_DIR/meas_node_binaries.tgz"
fi

# Set before the pip install below (rather than after) so pip's "not on PATH"
# warning doesn't fire, and so it's already in effect for the ansible-galaxy/
# ansible calls further down.
export PATH="$PATH:$HOME_BASE/.local/bin"

echo "-----Updating apt-----"
sudo apt update

echo "-----Installing pip3-----"
sudo apt install -y python3-pip
pip3 --version

echo "-----Installing python requirements-----"
# --break-system-packages: needed on Ubuntu 24.04+ (PEP 668); harmless no-op
# flag is unavailable on older pip, so pin an image where it's supported.
python3 -m pip install --user --break-system-packages -r "$REQUIREMENTS_TXT"

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
mkdir -p "$BINARIES_DIR"
tar czf "$OUT_TGZ" -C / \
  home/mfuser/.local \
  home/mfuser/.ansible \
  home/mfuser/.mf_binaries_build_info

echo "-----Finished! Wrote $OUT_TGZ-----"
echo "Commit this file, and if install_ansible.sh should now pin to it, update"
echo "MEAS_NODE_BINARIES_TGZ there too."
