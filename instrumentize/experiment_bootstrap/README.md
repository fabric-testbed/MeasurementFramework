# Experiment Bootstrap

Scripts and Ansible playbooks that turn a fresh FABRIC node into a working `meas-node` (and, via the meas-node acting
as an Ansible controller, into a fully instrumented experiment slice). These are run against `/home/mfuser/mf_git`
after `mflib` has cloned this repo onto the node -- none of them are meant to be run from a developer workstation
except `build_meas_node_binaries.ipynb`/`.sh` (see below).

## Two stages

### 1. Local setup on the meas-node (`bootstrap.sh`)

Run directly on the meas-node right after it's cloned. No network installs beyond what's already bundled --
everything it needs comes from the tarball in [`meas_node_binaries/`](meas_node_binaries/README.md).

- [`bootstrap.sh`](bootstrap.sh) -- entry point. Adds `~/.local/bin` to `mfuser`'s `PATH`, then runs the two steps
  below in order.
- [`install_ansible.sh`](install_ansible.sh) -- extracts a pre-built `~/.local` + `~/.ansible` bundle so `ansible`/
  `ansible-playbook`/`ansible-galaxy` are available without hitting apt/pip/Galaxy over the network. Picks which
  tarball to extract from [`meas_node_binaries/`](meas_node_binaries/README.md) based on an `os_image_<image_name>`
  marker file FABRIC drops in `mfuser`'s home dir, falling back to a pinned default if there's no marker or no
  matching tarball.
- [`setup_service_dirs.py`](setup_service_dirs.py) -- creates `~/services/<service_name>/{log,files,data}` for every
  script in [`service_scripts/`](service_scripts/README.md) and runs that script to populate `files/`. See that
  directory's README for how individual services plug in.

### 2. Ansible playbooks run against the whole slice

Once `~/services/common/hosts.ini` exists (populated by the `common` service above) and `~/.ssh/mfuser_private_key`
can reach every experiment node, the meas-node acts as the Ansible controller for the entire slice. These wrapper
scripts shell out to `ansible-playbook -i hosts.ini --key-file ... -b <playbook>` and print a JSON summary
(`play_recap` + `success`) to stdout for `mflib` to parse:

- [`bootstrap_playbooks.py`](bootstrap_playbooks.py) -- runs [`bootstrap.yml`](bootstrap.yml): clones the
  [`ptp`](../ptp) repo onto the meas-node, then across all hosts updates the package cache, installs pip3 + the
  Python Docker SDK, installs LinuxPTP, installs Docker (or fixes up its daemon config/registry mirror if already
  present), and applies a couple of distro-specific repo fixes (CentOS/Rocky mirror URLs, PEP 668
  `--break-system-packages` handling). Set `SKIP_PTP=1` in the environment before running it to skip both the PTP
  repo download and the LinuxPTP role (tagged `ptp` in `bootstrap.yml`) -- useful when a node's kernel has no matching
  `linux-modules-extra-<kernel>` package available yet, since that failure otherwise aborts the rest of the play for
  that host (including the Docker install) partway through.
- [`bootstrap_docker.py`](bootstrap_docker.py) -- runs [`pip3_docker_sdk_playbook.yml`](pip3_docker_sdk_playbook.yml)
  (pip3 + Python Docker SDK) and [`docker_playbook.yml`](docker_playbook.yml) (Docker + IPv6 registry mirror) as two
  separate plays. Narrower, older sibling of `bootstrap_playbooks.py`/`bootstrap.yml` -- kept for callers that only
  want the Docker piece.

`ansible.cfg` in this directory sets shared Ansible behavior for these runs (large `forks`, disabled host key
checking, SSH multiplexing/pipelining, and task/role timing callbacks).

## Subdirectories

- [`meas_node_binaries/`](meas_node_binaries/README.md) -- the pre-built tarballs `install_ansible.sh` extracts, one
  per FABRIC base image, plus the scripts/notebook (`build_meas_node_binaries.sh`,
  `build_meas_node_binaries.ipynb`) used to (re)build them.
- [`service_scripts/`](service_scripts/README.md) -- one script per mflib-controlled service, run by
  `setup_service_dirs.py` during stage 1.

## Stale / superseded files

- `bootstrap_playbooks.py.old` -- predates `bootstrap_playbooks.py`/`bootstrap.yml`; ran `pip3_docker_sdk_playbook.yml`,
  `docker_playbook.yml`, and the PTP playbook as three separate plays. Kept for reference only.
- `install_ansible2.sh` -- currently empty and unused.
