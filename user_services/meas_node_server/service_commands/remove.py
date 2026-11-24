# Stop and remove the meas_node_server systemd service and its config,
# so a later create.py call sets it up fresh (new token/port).

import logging
import os
import subprocess

import meas_node_server_utilities as mu


def main():
    ret_val = {"success": True, "msg": ""}

    log_file_path = os.path.join(mu.this_service_dir, "log", "remove.log")
    logging.basicConfig(
        filename=log_file_path,
        format="%(asctime)s %(name)-8s %(levelname)-8s %(message)s",
        datefmt="%m/%d/%Y %I:%M:%S %p",
        level="INFO",
    )
    logging.info("-----Start meas_node_server Remove Script.-----")

    errors = []
    for cmd in (
        ["sudo", "systemctl", "stop", mu.SERVICE_NAME],
        ["sudo", "systemctl", "disable", mu.SERVICE_NAME],
    ):
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            errors.append(result.stderr.strip())

    subprocess.run(["sudo", "rm", "-f", mu.UNIT_PATH], capture_output=True, text=True)
    subprocess.run(["sudo", "rm", "-f", mu.ENV_FILE_PATH], capture_output=True, text=True)
    subprocess.run(["sudo", "systemctl", "daemon-reload"], capture_output=True, text=True)

    if os.path.exists(mu.config_filename):
        os.remove(mu.config_filename)

    if errors:
        ret_val["msg"] = "meas_node_server removed with warnings: " + "; ".join(errors)
    else:
        ret_val["msg"] = "meas_node_server removed."

    logging.info(ret_val["msg"])
    logging.info("-----End meas_node_server Remove Script.-----")
    print(mu.get_json_string(ret_val))


if __name__ == "__main__":
    main()
