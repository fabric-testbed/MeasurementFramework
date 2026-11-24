# Create the mflib_mcp service.
#
# Brings up fabric-testbed/mflib_portal_mcp (an MCP server exposing the
# meas node's Node Exporter Full dashboard as LLM-callable tools) as an
# additional container beside this node's existing Prometheus/Grafana/nginx
# stack, and adds a bearer-token-gated `/mcp` location to the node's nginx
# so it's reachable at https://<node>/mcp the same way Grafana is reachable
# at /grafana/.
#
# Only ever invoked by mflib's meas_node_self_start()-generated self-start
# script (see instrumentize/experiment_bootstrap/service_scripts/mflib_mcp.py
# for why this is staged on every meas node but not created on every one).
# Also safe to call directly via mflib.create("mflib_mcp") on a hand-created
# node -- it just generates its own bearer token in that case instead of
# using one dropped by the portal.

import logging
import os

import mflib_mcp_utilities as mu


def main():
    ret_val = {"success": True, "msg": ""}

    log_dir = os.path.join(mu.this_service_dir, "log")
    os.makedirs(log_dir, exist_ok=True)
    logging.basicConfig(
        filename=os.path.join(log_dir, "create.log"),
        format="%(asctime)s %(name)-8s %(levelname)-8s %(message)s",
        datefmt="%m/%d/%Y %I:%M:%S %p",
        level="INFO",
    )
    logging.info("-----Start mflib_mcp Create Script.-----")

    token = mu.get_token_from_file()
    if not token:
        token = mu.generate_token()
        mu.write_token_to_file(token)
        logging.info("No portal-issued token found -- generated one locally.")

    try:
        mu.clone_or_update_repo()
    except Exception as e:
        detail = e.stderr if hasattr(e, "stderr") else str(e)
        ret_val = {"success": False, "msg": f"Failed to clone/update mflib_portal_mcp: {detail}"}
        logging.error(ret_val["msg"])
        print(mu.get_json_string(ret_val))
        return

    try:
        mu.compose_up()
    except Exception as e:
        detail = e.stderr if hasattr(e, "stderr") else str(e)
        ret_val = {"success": False, "msg": f"docker compose up failed: {detail}"}
        logging.error(ret_val["msg"])
        print(mu.get_json_string(ret_val))
        return

    try:
        mu.install_nginx_location(token)
    except Exception as e:
        detail = e.stderr if hasattr(e, "stderr") else str(e)
        ret_val = {"success": False, "msg": f"nginx /mcp location install failed: {detail}"}
        logging.error(ret_val["msg"])
        print(mu.get_json_string(ret_val))
        return

    ret_val["msg"] = "mflib_mcp created and running."
    ret_val["mcp_path"] = "/mcp"
    logging.info(ret_val["msg"])
    logging.info("-----End mflib_mcp Create Script.-----")
    print(mu.get_json_string(ret_val))


if __name__ == "__main__":
    main()
