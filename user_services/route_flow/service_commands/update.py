# Update the route_flow service: per-route traffic counters on the experiment nodes
# and the animated topology dashboard in Grafana.
# Topology comes from data/data.json ("experiment_topology") or, for portal / self-started
# meas nodes, from /home/mfuser/registered_slice.json. See route_flow_utils.py.
# The prometheus and grafana_manager services must already be created.

import logging
import os

import route_flow_utils as rfu


def main():
    logFilePath = os.path.join(rfu.this_service_dir, "log", "update.log")
    logging.basicConfig(filename=logFilePath, format="%(asctime)s %(name)-8s %(levelname)-8s %(message)s",
                        datefmt="%m/%d/%Y %I:%M:%S %p", level="INFO")
    logger = logging.getLogger("route_flow")
    logger.info("-----Start Update Script.-----")
    try:
        ret_val = rfu.setup(logger)
    except Exception as e:
        logger.exception("route_flow update failed")
        ret_val = {"success": False, "msg": f"route_flow update failed: {e}"}
    logger.info(ret_val)
    print(rfu.get_json_string(ret_val))
    logger.info("-----End Update Script.-----")


if __name__ == "__main__":
    main()
