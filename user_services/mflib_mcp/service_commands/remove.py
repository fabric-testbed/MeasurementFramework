# Remove the mflib_mcp service: stops/removes its container and strips the
# nginx /mcp location, but leaves the cloned mflib_portal_mcp source and the
# token file in place (a later create.py re-run reuses both).

import logging
import os

import mflib_mcp_utilities as mu


def main():
    ret_val = {"success": True, "msg": ""}

    log_dir = os.path.join(mu.this_service_dir, "log")
    os.makedirs(log_dir, exist_ok=True)
    logging.basicConfig(
        filename=os.path.join(log_dir, "remove.log"),
        format="%(asctime)s %(name)-8s %(levelname)-8s %(message)s",
        datefmt="%m/%d/%Y %I:%M:%S %p",
        level="INFO",
    )
    logging.info("-----Start mflib_mcp Remove Script.-----")

    try:
        mu.remove_nginx_location()
    except Exception as e:
        detail = e.stderr if hasattr(e, "stderr") else str(e)
        ret_val = {"success": False, "msg": f"Failed to remove nginx /mcp location: {detail}"}
        logging.error(ret_val["msg"])
        print(mu.get_json_string(ret_val))
        return

    try:
        mu.compose_down()
    except Exception as e:
        detail = e.stderr if hasattr(e, "stderr") else str(e)
        ret_val = {"success": False, "msg": f"docker compose down failed: {detail}"}
        logging.error(ret_val["msg"])
        print(mu.get_json_string(ret_val))
        return

    ret_val["msg"] = "mflib_mcp removed."
    logging.info(ret_val["msg"])
    logging.info("-----End mflib_mcp Remove Script.-----")
    print(mu.get_json_string(ret_val))


if __name__ == "__main__":
    main()
