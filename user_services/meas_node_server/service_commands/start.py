# Start the meas_node_server service using its existing systemd unit.

import logging
import os
import subprocess

import meas_node_server_utilities as mu


def main():
    ret_val = {"success": True, "msg": ""}

    log_file_path = os.path.join(mu.this_service_dir, "log", "start.log")
    logging.basicConfig(
        filename=log_file_path,
        format="%(asctime)s %(name)-8s %(levelname)-8s %(message)s",
        datefmt="%m/%d/%Y %I:%M:%S %p",
        level="INFO",
    )
    logging.info("-----Start meas_node_server Start Script.-----")

    if not os.path.exists(mu.UNIT_PATH):
        ret_val["success"] = False
        ret_val["msg"] = "meas_node_server has not been created yet. Use mflib.create('meas_node_server') first."
        logging.error(ret_val["msg"])
        print(mu.get_json_string(ret_val))
        return

    try:
        subprocess.run(
            ["sudo", "systemctl", "start", mu.SERVICE_NAME],
            check=True, capture_output=True, text=True,
        )
        ret_val["msg"] = "meas_node_server started."
    except subprocess.CalledProcessError as e:
        ret_val["success"] = False
        ret_val["msg"] = f"Failed to start {mu.SERVICE_NAME}: {e.stderr}"

    logging.info(ret_val["msg"])
    logging.info("-----End meas_node_server Start Script.-----")
    print(mu.get_json_string(ret_val))


if __name__ == "__main__":
    main()
