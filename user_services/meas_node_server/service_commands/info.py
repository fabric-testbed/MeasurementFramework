# Get status info from the running meas_node_server (does not change state).

import logging
import os

import meas_node_server_utilities as mu


def main():
    ret_val = {"success": True, "msg": ""}

    log_file_path = os.path.join(mu.this_service_dir, "log", "info.log")
    logging.basicConfig(
        filename=log_file_path,
        format="%(asctime)s %(name)-8s %(levelname)-8s %(message)s",
        datefmt="%m/%d/%Y %I:%M:%S %p",
        level="INFO",
    )
    logging.info("-----Start meas_node_server Info Script.-----")

    saved = mu.get_saved_config()
    if not saved:
        ret_val["success"] = False
        ret_val["msg"] = "meas_node_server has not been created yet."
        print(mu.get_json_string(ret_val))
        return

    port = saved.get("port", mu.DEFAULT_PORT)
    token = saved.get("token")

    ret_val["port"] = port
    ret_val["active"] = mu.is_active()
    ret_val["status"] = mu.get_status(port, token)

    logging.info(ret_val)
    logging.info("-----End meas_node_server Info Script.-----")
    print(mu.get_json_string(ret_val))


if __name__ == "__main__":
    main()
