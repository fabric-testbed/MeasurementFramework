# Info for the route_flow service: the topology in use, whether counters are being
# scraped, and the dashboard path.

import json
import os

import route_flow_utils as rfu


def main():
    ret_val = {"success": True, "msg": ""}
    try:
        with open(rfu.topology_filename) as f:
            topo = json.load(f)
    except OSError:
        ret_val["msg"] = "route_flow has not been set up yet (no topology.json)."
        print(rfu.get_json_string(ret_val))
        return
    ret_val["topology"] = topo
    ret_val["routes"] = rfu.routes(topo)
    ret_val["peers"] = rfu.peers_by_node(topo)
    ret_val["dashboard"] = "/grafana/d/" + rfu.DASHBOARD_UID
    print(rfu.get_json_string(ret_val))


if __name__ == "__main__":
    main()
