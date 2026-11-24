# Create the meas_node_server service.
# Installs the FastAPI-based meas-node status/health server (server.py, in
# this same directory) and runs it as a systemd service bound to the node's
# FABNetv6 address, so mfportal can call it to check on the meas node's
# health status.

import logging
import os
import secrets
import subprocess
import time

import meas_node_server_utilities as mu


def main():
    ret_val = {"success": True, "msg": ""}

    log_file_path = os.path.join(mu.this_service_dir, "log", "create.log")
    logging.basicConfig(
        filename=log_file_path,
        format="%(asctime)s %(name)-8s %(levelname)-8s %(message)s",
        datefmt="%m/%d/%Y %I:%M:%S %p",
        level="INFO",
    )
    logging.info("-----Start meas_node_server Create Script.-----")

    if mu.is_active():
        saved = mu.get_saved_config()
        ret_val["msg"] = (
            "meas_node_server is already created and running. "
            "Use mflib.info('meas_node_server') for details."
        )
        ret_val["port"] = saved.get("port", mu.DEFAULT_PORT)
        logging.info(ret_val["msg"])
        print(mu.get_json_string(ret_val))
        return

    data = mu.get_data()
    port = data.get("port", mu.DEFAULT_PORT)
    token = mu.get_token_from_file() or data.get("token") or secrets.token_hex(32)

    try:
        mu.install_requirements()
    except subprocess.CalledProcessError as e:
        ret_val["success"] = False
        ret_val["msg"] = f"Failed to install server dependencies: {e.stderr}"
        logging.error(ret_val["msg"])
        print(mu.get_json_string(ret_val))
        return

    mu.save_config(port, token)

    try:
        mu.install_and_start_systemd_service(port, token)
    except subprocess.CalledProcessError as e:
        ret_val["success"] = False
        ret_val["msg"] = f"Failed to install/start {mu.SERVICE_NAME}: {e.stderr}"
        logging.error(ret_val["msg"])
        print(mu.get_json_string(ret_val))
        return

    time.sleep(3)
    healthy, detail = mu.check_health(port, token)
    ret_val["success"] = healthy
    ret_val["port"] = port
    ret_val["token"] = token
    if healthy:
        ret_val["msg"] = "meas_node_server created and running."
    else:
        ret_val["msg"] = f"meas_node_server started but health check failed: {detail}"

    logging.info(ret_val["msg"])
    logging.info("-----End meas_node_server Create Script.-----")
    print(mu.get_json_string(ret_val))


if __name__ == "__main__":
    main()
