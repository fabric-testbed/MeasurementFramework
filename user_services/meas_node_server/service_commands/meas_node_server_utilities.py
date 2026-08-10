import glob
import json
import os
import subprocess
import sys
import tempfile

services_dir = os.path.join(os.path.expanduser("~"), "services")
this_service_dir = os.path.dirname(os.path.realpath(__file__))

data_filename = os.path.join(services_dir, "meas_node_server", "data", "data.json")
config_filename = os.path.join(services_dir, "meas_node_server", "data", "config.json")

SERVICE_NAME = "meas-node-server"
UNIT_PATH = f"/etc/systemd/system/{SERVICE_NAME}.service"
ENV_FILE_PATH = "/etc/mflib/meas-node-server.env"
DEFAULT_PORT = 5000
SERVER_SCRIPT = os.path.join(this_service_dir, "server.py")
REQUIREMENTS_FILE = os.path.join(this_service_dir, "requirements.txt")


def get_data():
    # Get incoming data which will be in the data.json file.
    try:
        with open(data_filename) as data_file:
            return json.load(data_file)
    except Exception:
        return {}


def get_json_string(data):
    # Format data as a json string.
    try:
        return json.dumps(data)
    except Exception as e:
        error_msg = {
            "json_error": "Data was unable to be converted to a JSON string",
            "json_exception": type(e).__name__,
        }
        return json.dumps(error_msg)


def save_config(port, token):
    os.makedirs(os.path.dirname(config_filename), exist_ok=True)
    with open(config_filename, "w") as f:
        json.dump({"port": port, "token": token}, f)
    os.chmod(config_filename, 0o600)


def get_saved_config():
    try:
        with open(config_filename) as f:
            return json.load(f)
    except Exception:
        return {}


def _needs_break_system_packages():
    # Same PEP 668 externally-managed-environment check used in bootstrap.yml.
    marker = glob.glob("/usr/lib/python3*/EXTERNALLY-MANAGED") + glob.glob(
        "/usr/lib64/python3*/EXTERNALLY-MANAGED"
    )
    return bool(marker)


def install_requirements():
    # --ignore-installed avoids "Cannot uninstall X, RECORD file not found"
    # errors when a dependency (eg. typing_extensions) is already present
    # as an apt/debian package rather than a pip-tracked one.
    cmd = ["sudo", "pip3", "install", "-q", "--ignore-installed", "-r", REQUIREMENTS_FILE]
    if _needs_break_system_packages():
        cmd.append("--break-system-packages")
    subprocess.run(cmd, check=True, capture_output=True, text=True)


def install_and_start_systemd_service(port, token):
    # Token is passed via an EnvironmentFile (root-only-readable) rather than
    # a --token CLI arg so it doesn't show up in `ps aux` / systemctl status.
    env_text = f"MFLIB_API_TOKEN={token}\n"
    unit_text = "\n".join(
        [
            "[Unit]",
            "Description=MeasurementFramework meas-node status/health server",
            "After=network-online.target",
            "Wants=network-online.target",
            "",
            "[Service]",
            "Type=simple",
            f"EnvironmentFile={ENV_FILE_PATH}",
            f"ExecStart={sys.executable} {SERVER_SCRIPT} --port {port}",
            "Restart=on-failure",
            "RestartSec=5",
            "User=mfuser",
            "",
            "[Install]",
            "WantedBy=multi-user.target",
        ]
    ) + "\n"

    with tempfile.NamedTemporaryFile("w", suffix=".env", delete=False) as f:
        f.write(env_text)
        tmp_env_path = f.name

    with tempfile.NamedTemporaryFile("w", suffix=".service", delete=False) as f:
        f.write(unit_text)
        tmp_unit_path = f.name

    try:
        subprocess.run(
            ["sudo", "mkdir", "-p", os.path.dirname(ENV_FILE_PATH)],
            check=True, capture_output=True, text=True,
        )
        subprocess.run(
            ["sudo", "cp", tmp_env_path, ENV_FILE_PATH],
            check=True, capture_output=True, text=True,
        )
        subprocess.run(
            ["sudo", "chmod", "600", ENV_FILE_PATH],
            check=True, capture_output=True, text=True,
        )
        subprocess.run(
            ["sudo", "chown", "mfuser:mfuser", ENV_FILE_PATH],
            check=True, capture_output=True, text=True,
        )
        subprocess.run(
            ["sudo", "cp", tmp_unit_path, UNIT_PATH],
            check=True, capture_output=True, text=True,
        )
        subprocess.run(
            ["sudo", "systemctl", "daemon-reload"],
            check=True, capture_output=True, text=True,
        )
        subprocess.run(
            ["sudo", "systemctl", "enable", SERVICE_NAME],
            check=True, capture_output=True, text=True,
        )
        subprocess.run(
            ["sudo", "systemctl", "restart", SERVICE_NAME],
            check=True, capture_output=True, text=True,
        )
    finally:
        os.remove(tmp_env_path)
        os.remove(tmp_unit_path)


def is_active():
    result = subprocess.run(["systemctl", "is-active", "--quiet", SERVICE_NAME])
    return result.returncode == 0


def check_health(port, token):
    cmd = [
        "curl", "-sf",
        "-H", f"Authorization: Bearer {token}",
        f"http://[::1]:{port}/healthz",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        return True, result.stdout
    return False, result.stderr or f"curl exited {result.returncode}"


def get_status(port, token):
    cmd = [
        "curl", "-sf",
        "-H", f"Authorization: Bearer {token}",
        f"http://[::1]:{port}/status",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        try:
            return json.loads(result.stdout)
        except Exception:
            return {"raw": result.stdout}
    return {"error": result.stderr or f"curl exited {result.returncode}"}
