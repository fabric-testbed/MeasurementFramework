
import os
import subprocess
import tempfile
import time
from pathlib import Path
import json

import requests
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

services_dir = os.path.join(os.path.expanduser('~') ,"services")

this_service_dir = os.path.join(services_dir, "grafana_manager")

rendered_dir = os.path.join(this_service_dir, "rendered")

data_filename = os.path.join(this_service_dir, "data", "data.json" )

files_dir = os.path.join(this_service_dir, "files")
dashboards_dir = os.path.join(this_service_dir, "Dashboards")

prometheus_default_install_vars_file = os.path.join(services_dir, "prometheus", "extra_files", "install_vars.json")

infoFilePath = os.path.join( this_service_dir, "infoFile.txt")
configFilePath = os.path.join( this_service_dir, "configFile.txt")

# instrumentize/prometheus/ansible/roles/fabric_experiment/defaults/main.yml's
# install_name (fabric_prometheus) is never overridden anywhere in this repo,
# so base_install_dir/container names below are the fixed, resolved values --
# not read from install_vars.json, since install_name isn't passed into it.
portal_registration_file = "/etc/mflib/portal_registration.json"
grafana_compose_dir = "/opt/fabric_prometheus"
grafana_compose_file = os.path.join(grafana_compose_dir, "docker-compose.yml")
grafana_env_file = os.path.join(grafana_compose_dir, "grafana", "env_file")
grafana_compose_service = "grafana"  # the docker-compose.yml service key, not its container_name


def get_external_hostname():
    """
    Reads external_hostname from /etc/mflib/portal_registration.json (the
    hostname users reach this meas node's Grafana through, via the portal's
    dynamic reverse proxy -- see set_grafana_csrf_trusted_origin()).
    Returns None if the file, or the field, doesn't exist -- an older
    meas-node, or PORTAL_DOMAIN unset on the portal.
    """
    try:
        with open(portal_registration_file) as f:
            data = json.load(f)
    except Exception:
        return None
    return data.get("external_hostname") or None


def set_grafana_csrf_trusted_origin(hostname):
    """
    Sets GF_SECURITY_CSRF_TRUSTED_ORIGINS=hostname in the grafana container's
    env_file (rendered once by the prometheus role's grafana_env.j2, at
    grafana_env_file) and recreates the container via docker compose so it
    picks it up.

    Deliberately NOT `docker restart`: env_file is only read by Docker at
    container *creation* time, not on restart -- a plain restart just
    relaunches the existing container with whatever environment was baked
    in when `docker compose up` first created it, silently ignoring the
    updated file (this was tried and confirmed not to work: Grafana kept
    rejecting the origin after a restart). `docker compose up -d
    --force-recreate` tears down and recreates the container from the
    current env_file/compose config, matching how
    fabric_experiment_install_tasks.yml originally started it
    (community.docker.docker_compose_v2, project_src=base_install_dir).
    `--no-deps` scopes the recreate to just the grafana service.

    `hostname` must be bare (no scheme, no port) -- Grafana's CSRF
    middleware does an exact hostname string match, no wildcards.

    Returns {"success": bool, "msg": str}.
    """
    if not os.path.exists(grafana_env_file):
        return {
            "success": False,
            "msg": f"{grafana_env_file} not found -- has the prometheus service been created yet?",
        }

    with open(grafana_env_file) as f:
        lines = [
            line for line in f.read().splitlines()
            if not line.startswith("GF_SECURITY_CSRF_TRUSTED_ORIGINS=")
        ]
    lines.append(f"GF_SECURITY_CSRF_TRUSTED_ORIGINS={hostname}")

    # grafana_env_file is owned by grafana:root (see config_grafana_tasks.yml),
    # but this runs as the unprivileged mfuser -- write via a temp file + sudo
    # cp instead of open(..., "w") directly, same pattern as
    # meas_node_server_utilities.install_and_start_systemd_service.
    with tempfile.NamedTemporaryFile("w", delete=False) as f:
        f.write("\n".join(lines) + "\n")
        tmp_path = f.name

    try:
        copy_result = subprocess.run(
            ["sudo", "cp", tmp_path, grafana_env_file],
            capture_output=True, text=True,
        )
    finally:
        os.remove(tmp_path)

    if copy_result.returncode != 0:
        return {
            "success": False,
            "msg": f"Failed to write {grafana_env_file}: {copy_result.stderr.strip()}",
        }

    if not os.path.exists(grafana_compose_file):
        return {
            "success": False,
            "msg": f"Wrote {grafana_env_file} but {grafana_compose_file} not found -- can't recreate the grafana container.",
        }

    result = subprocess.run(
        [
            "sudo", "docker", "compose",
            "-f", grafana_compose_file,
            "up", "-d", "--force-recreate", "--no-deps",
            grafana_compose_service,
        ],
        cwd=grafana_compose_dir,
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        return {
            "success": False,
            "msg": f"Wrote {grafana_env_file} but failed to recreate the grafana container: {result.stderr.strip()}",
        }
    return {
        "success": True,
        "msg": f"Set GF_SECURITY_CSRF_TRUSTED_ORIGINS={hostname} in {grafana_env_file} and recreated the grafana container to apply it.",
    }


def wait_for_grafana_ready(timeout=30, interval=2):
    """
    Polls https://localhost/grafana/api/health (unauthenticated) until
    Grafana responds or `timeout` seconds pass. Used after a container
    restart (set_grafana_csrf_trusted_origin()) so callers that immediately
    make authenticated API calls against Grafana don't race its startup.
    Returns True if Grafana answered, False on timeout.
    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            r = requests.get("https://localhost/grafana/api/health", verify=False, timeout=5)
            if r.status_code == 200:
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(interval)
    return False

def get_data():
    # Get incoming data which will be in the data.json file.
    try:
        with open(data_filename) as data_file:
            data = json.load(data_file)
    except Exception as e:
        data = {}
    return data

def get_json_string(data):
    # Format data as a json string.
    try:
        json_str = json.dumps(data)
    except Exception as e:
        error_msg = {}
        error_msg['json_error'] = "Data was unable to be converted to a JSON string"
        error_msg['json_exception'] = type(e).__name__  
        json_str = json.dumps(error_msg)
    return json_str

def get_defaults():
    with open(prometheus_default_install_vars_file, "r") as f:
        defaults = json.load(f)
    return defaults