# Stop the meas_node_server service without removing its configuration.

import logging
import os
import subprocess

import meas_node_server_utilities as mu


def main():
    ret_val = {"success": True, "msg": ""}

    log_file_path = os.path.join(mu.this_service_dir, "log", "stop.log")
    logging.basicConfig(
        filename=log_file_path,
        format="%(asctime)s %(name)-8s %(levelname)-8s %(message)s",
        datefmt="%m/%d/%Y %I:%M:%S %p",
        level="INFO",
    )
    logging.info("-----Start meas_node_server Stop Script.-----")

    try:
        subprocess.run(
            ["sudo", "systemctl", "stop", mu.SERVICE_NAME],
            check=True, capture_output=True, text=True,
        )
        ret_val["msg"] = "meas_node_server stopped."
    except subprocess.CalledProcessError as e:
        ret_val["success"] = False
        ret_val["msg"] = f"Failed to stop {mu.SERVICE_NAME}: {e.stderr}"

    logging.info(ret_val["msg"])
    logging.info("-----End meas_node_server Stop Script.-----")
    print(mu.get_json_string(ret_val))


if __name__ == "__main__":
    main()
