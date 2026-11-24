# route_flow service

Per-route traffic for the experiment nodes, shown as an animated topology in Grafana.

* **Counters**: each experiment node runs `mf-route-acct.service`
  (`/usr/local/bin/mf_route_acct.sh`). It keeps count-only iptables rules (comment
  `mfacct`) for every peer IP and writes their byte counters every 5 s to
  node_exporter's textfile collector as

  ```
  mf_route_bytes_total{mf_node="Node1", mf_peer="Node2", direction="tx|rx"}
  ```

  A node normally has a single experiment NIC, so the NIC counters can't split traffic
  by destination; these can.
* **Dashboard**: `<slice> - route traffic` (uid `mflib-route-flow`). The nodes are drawn
  on a circle, with one animated curve per direction per route (moving dashes and a
  dot, faster for more traffic, coloured by the sender) and each node's experiment and
  measurement IPs. Below that are per-node sent/received time series. Grafana's text
  panel won't render inline SVG, so the picture is an SVG in `<img src="data:...">`
  and the numbers are hidden query variables that refresh every 10 s.

## Where the topology comes from

The meas node has no fablib or slice object, so it gets the topology as JSON at
creation time. It looks in this order:

1. `data/data.json` → `"experiment_topology"` (MFLib `create`/`update("route_flow", data=...)`)
2. `/home/mfuser/registered_slice.json` → `"experiment_topology"` (portal / self-started
   meas nodes; written before `mflib-meas-node-self-start.service` runs)

```json
{
  "slice_name": "MySlice",
  "nodes": [
    {"name": "Node1", "site": "HAWI", "meas_ip": "2602:...",
     "ifaces": [{"dev": "eth1", "ip": "10.147.3.2", "network": "net1"}]}
  ],
  "routes": [{"a": "Node1", "b": "Node2", "label": "target 5 Mb/s"}]
}
```

`routes` is optional; the default is every pair of nodes with an experiment IP. The
client builds this with `mflib.route_flow.collect_experiment_topology(slice)`. The
experiment interfaces must already have their IP addresses at that point.

## Commands

| Script | What it does |
|---|---|
| `create.py` | Install the counters on `[Experiment_Nodes]` (ansible, `install_route_acct.yml`) and upload the dashboard. Without a topology it does nothing and still reports success, so it is safe in the self-start sequence. |
| `update.py` | Same, for a new/changed topology (re-run after IPs or nodes change). |
| `info.py` | Topology in use, routes, peers per node and the dashboard path. |

Requires the prometheus (node_exporter with the textfile collector) and grafana_manager
services to be created first.
