"""
Helpers for the route_flow service: per-route traffic counters on the experiment
nodes plus an animated Grafana topology dashboard built from them.

Everything here runs on the meas node with no access to fablib or the slice object.
The topology comes from data written at meas-node creation time:

  1. this service's data/data.json  (MFLib create/update("route_flow", data=...)), or
  2. /home/mfuser/registered_slice.json  -> "experiment_topology"
     (written by the portal / MFPortal.meas_node_self_start() before self-start runs).

experiment_topology schema (built client-side by mflib.route_flow.collect_experiment_topology()):

  {
    "slice_name": "MySlice",
    "nodes": [
      {"name": "Node1", "site": "HAWI", "meas_ip": "2602:fcfb:...",   # meas_ip optional
       "ifaces": [{"dev": "eth1", "ip": "10.147.3.2", "network": "net1"}]},
      ...
    ],
    "routes": [{"a": "Node1", "b": "Node2", "label": "5 Mbit/s"}, ...]   # optional, default: every pair
  }
"""

import json
import math
import os
import subprocess
import urllib.parse

import requests
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

home_base = "/home/mfuser"
services_dir = os.path.join(home_base, "services")
this_service_dir = os.path.join(services_dir, "route_flow")
data_filename = os.path.join(this_service_dir, "data", "data.json")
topology_filename = os.path.join(this_service_dir, "topology.json")   # last topology used
registered_slice_filename = os.path.join(home_base, "registered_slice.json")
grafana_config_filename = os.path.join(services_dir, "grafana_manager", "configFile.txt")
hosts_ini = os.path.join(services_dir, "common", "hosts.ini")
playbook_exe = os.path.join(home_base, ".local", "bin", "ansible-playbook")
playbook = os.path.join(this_service_dir, "install_route_acct.yml")
acct_script = os.path.join(this_service_dir, "mf_route_acct.sh")

DASHBOARD_UID = "mflib-route-flow"
METRIC = "mf_route_bytes_total"


def get_json_string(data):
    return json.dumps(data, default=str)


def _read_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def load_topology():
    """Returns (topology, source) or (None, reason)."""
    data = _read_json(data_filename) or {}
    if data.get("experiment_topology"):
        return data["experiment_topology"], data_filename
    registered = _read_json(registered_slice_filename) or {}
    if registered.get("experiment_topology"):
        topo = dict(registered["experiment_topology"])
        topo.setdefault("slice_name", registered.get("slice_name", ""))
        # fill in meas IPs from the registered node list if the topology doesn't have them
        meas_ips = {n.get("name"): n.get("ip_addr") for n in registered.get("nodes", [])}
        for n in topo.get("nodes", []):
            n.setdefault("meas_ip", meas_ips.get(n["name"]))
        return topo, registered_slice_filename
    return None, f"no experiment_topology in {data_filename} or {registered_slice_filename}"


def save_topology(topo):
    with open(topology_filename, "w") as f:
        json.dump(topo, f, indent=2)


def node_ips(node):
    return [i["ip"] for i in node.get("ifaces", []) if i.get("ip")]


def routes(topo):
    """[(a, b, label)] -- the given routes, or every pair of nodes that have an experiment IP."""
    if topo.get("routes"):
        return [(r["a"], r["b"], r.get("label", "")) for r in topo["routes"]]
    names = [n["name"] for n in topo["nodes"] if node_ips(n)]
    return [(a, b, "") for i, a in enumerate(names) for b in names[i + 1:]]


def peers_by_node(topo):
    """{node: [[peer, peer_ip], ...]} for the counter script, following routes(topo)."""
    ips = {n["name"]: node_ips(n) for n in topo["nodes"]}
    peers = {}
    for a, b, _ in routes(topo):
        peers.setdefault(a, []).extend([b, ip] for ip in ips.get(b, []))
        peers.setdefault(b, []).extend([a, ip] for ip in ips.get(a, []))
    return peers


# ---------------------------------------------------------------- counters

def install_counters(topo, logger=None):
    """Runs install_route_acct.yml against hosts.ini's [Experiment_Nodes]."""
    peers = peers_by_node(topo)
    if not peers:
        return {"success": True, "msg": "No experiment IPs in topology; counters not installed."}
    vars_file = os.path.join(this_service_dir, "files", "route_flow_vars.json")
    os.makedirs(os.path.dirname(vars_file), exist_ok=True)
    with open(vars_file, "w") as f:
        json.dump({"route_flow_peers": peers, "route_flow_script": acct_script}, f)
    env = dict(os.environ, ANSIBLE_HOST_KEY_CHECKING="False", ANSIBLE_SSH_RETRIES="5",
               ANSIBLE_CONFIG=os.path.join(services_dir, "common", "ansible.cfg"))
    # inventory host vars (e.g. self-start's [Experiment_Nodes:vars] key) take precedence over --key-file
    cmd = [playbook_exe, "-i", hosts_ini, "--key-file", os.path.join(home_base, ".ssh", "mfuser_private_key"),
           "-b", playbook, "--extra-vars", f"@{vars_file}"]
    if logger:
        logger.info(cmd)
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
    if logger:
        logger.info(r.stdout)
        logger.info(r.stderr)
    recap = r.stdout[r.stdout.rfind("PLAY RECAP"):] if "PLAY RECAP" in r.stdout else r.stdout[-2000:]
    return {"success": r.returncode == 0,
            "msg": "Route counters installed." if r.returncode == 0 else "Route counter playbook failed.",
            "play_recap": recap}


# ---------------------------------------------------------------- grafana

def grafana_api_key():
    cfg = {}
    with open(grafana_config_filename) as f:
        for line in f:
            if "-" in line:
                k, v = line.split("-", 1)
                cfg[k.strip()] = v.strip()
    return cfg.get("apiKey")


def grafana(method, path, body=None):
    r = requests.request(method, "https://localhost/grafana/api" + path, verify=False, timeout=30,
                         headers={"Authorization": "Bearer " + grafana_api_key(),
                                  "Content-Type": "application/json"},
                         data=json.dumps(body) if body is not None else None)
    r.raise_for_status()
    return r.json()


def prometheus_ds_uid():
    for ds in grafana("GET", "/datasources"):
        if ds.get("type") == "prometheus":
            return ds["uid"]
    raise RuntimeError("No Prometheus datasource in Grafana (grafana_manager not created yet?)")


def upload_dashboard(dashboard):
    uid = prometheus_ds_uid()
    dashboard = json.loads(json.dumps(dashboard).replace("__DS_UID__", uid))
    r = grafana("POST", "/dashboards/db", {"dashboard": dashboard, "overwrite": True})
    return {"success": r.get("status") == "success", "msg": "Route flow dashboard uploaded.",
            "url": "/grafana/d/" + dashboard["uid"]}


# ---------------------------------------------------------------- dashboard

COLORS = ["#73BF69", "#5794F2", "#FF9830", "#F2495C", "#B877D9", "#FADE2A", "#8AB8FF", "#FF780A"]


def build_dashboard(topo, refresh="10s"):
    """
    Animated topology (one curve per direction per route, dashes + dot moving with the
    traffic, faster for higher rates) plus one sent/received time series per node.

    Grafana's text panel won't render inline SVG, so the picture is an SVG inside
    <img src="data:...">, and the live numbers are hidden query variables substituted
    into it on every refresh.
    """
    slice_name = topo.get("slice_name") or "slice"
    nodes = [n for n in topo["nodes"] if node_ips(n)]
    names = [n["name"] for n in nodes]
    by_name = {n["name"]: n for n in nodes}
    num = {n: i + 1 for i, n in enumerate(names)}
    color = {n: COLORS[i % len(COLORS)] for i, n in enumerate(names)}
    rts = [(a, b, lbl) for a, b, lbl in routes(topo) if a in by_name and b in by_name]

    # nodes evenly on a circle, first one at the top
    W, H, R = 900, 620, 200
    CY = H / 2 + 10
    pos = {n: (W / 2 + R * math.sin(2 * math.pi * i / len(names)),
               CY - R * math.cos(2 * math.pi * i / len(names))) for i, n in enumerate(names)}
    label_size = 15 if len(names) <= 3 else 13

    DS = {"type": "prometheus", "uid": "__DS_UID__"}
    sel = lambda a, b, d: f'{METRIC}{{mf_node="{a}",mf_peer="{b}",direction="{d}"}}'

    def qvar(name, expr):
        q = f"query_result({expr})"
        return {"type": "query", "name": name, "datasource": DS, "query": q, "definition": q,
                "regex": "/.* ([-0-9.e+]+) [0-9]+$/", "refresh": 2, "hide": 2, "sort": 0,
                "includeAll": False, "multi": False, "current": {}, "options": []}

    variables, flows = [], []
    for a, b, _ in rts:
        for src, dst in ((a, b), (b, a)):
            k = f"f{num[src]}_{num[dst]}"
            m = f"sum(rate({sel(src, dst, 'tx')}[1m]))*8/1e6"
            variables.append(qvar(k + "_m", f"round({m}, 0.01)"))
            # animation period (s): faster for more traffic; 0 (= no animation) when idle
            variables.append(qvar(k + "_d", f"round(clamp_max(16/({m} + 0.5), 6) * ({m} > bool 0.05), 0.01)"))
            flows.append((k, src, dst))
    for n in names:
        for d in ("tx", "rx"):
            variables.append(qvar(f"n{num[n]}_{d}",
                                  f'round(sum(rate({METRIC}{{mf_node="{n}",direction="{d}"}}[1m]))*8/1e6, 0.01)'))

    def curve(p, q, r=60):
        (x1, y1), (x2, y2) = p, q
        dx, dy = x2 - x1, y2 - y1
        L = math.hypot(dx, dy) or 1
        nx, ny = dy / L, -dx / L          # left of the direction of travel (SVG y points down)
        sx, sy = x1 + dx / L * r + nx * 10, y1 + dy / L * r + ny * 10
        ex, ey = x2 - dx / L * r + nx * 10, y2 - dy / L * r + ny * 10
        cx, cy = (x1 + x2) / 2 + nx * 45, (y1 + y2) / 2 + ny * 45
        # label 30% along the curve (near the sender) so the two directions of a route,
        # and routes crossing in the middle, don't put their labels on top of each other
        t = 0.3
        mx = (1 - t) ** 2 * sx + 2 * (1 - t) * t * cx + t * t * ex
        my = (1 - t) ** 2 * sy + 2 * (1 - t) * t * cy + t * t * ey
        return f"M{sx:.0f} {sy:.0f} Q{cx:.0f} {cy:.0f} {ex:.0f} {ey:.0f}", mx + nx * 18, my + ny * 18

    parts = [f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {W} {H}' font-family='Inter,Helvetica,Arial,sans-serif'>"]
    for k, src, dst in flows:
        d, lx, ly = curve(pos[src], pos[dst])
        c = color[src]
        parts.append(f"<path d='{d}' fill='none' stroke='{c}' stroke-opacity='0.18' stroke-width='9' stroke-linecap='round'/>")
        parts.append(f"<path d='{d}' fill='none' stroke='{c}' stroke-width='3' stroke-dasharray='10 12'>"
                     f"<animate attributeName='stroke-dashoffset' from='22' to='0' dur='${{{k}_d}}s' repeatCount='indefinite'/></path>")
        parts.append(f"<circle r='6.5' fill='{c}' stroke='#111' stroke-width='1.5'><animateMotion dur='${{{k}_d}}s' "
                     f"repeatCount='indefinite' path='{d}'/></circle>")
        parts.append(f"<text x='{lx:.0f}' y='{ly + 5:.0f}' text-anchor='middle' font-size='{label_size}' font-weight='600' fill='{c}'>"
                     f"{src} to {dst}: ${{{k}_m}} Mb/s</text>")
    for a, b, lbl in rts:
        if lbl:
            (x1, y1), (x2, y2) = pos[a], pos[b]
            parts.append(f"<text x='{(x1 + x2) / 2:.0f}' y='{(y1 + y2) / 2 + 5:.0f}' text-anchor='middle' "
                         f"font-size='13' fill='#8e8e8e'>{lbl}</text>")
    for n in names:
        x, y = pos[n]
        node = by_name[n]
        ip_lines = [f"{i.get('dev', '')} {i['ip']}".strip() for i in node.get("ifaces", []) if i.get("ip")]
        if node.get("meas_ip"):
            ip_lines.append(f"meas {node['meas_ip']}")
        # addresses go on the outer side of the node, away from the curves
        below = y >= CY - 1
        ty = y + 74 if below else y - 66 - 17 * (len(ip_lines) - 1)
        parts.append(f"<circle cx='{x:.0f}' cy='{y:.0f}' r='52' fill='#181b1f' stroke='{color[n]}' stroke-width='4'/>"
                     f"<text x='{x:.0f}' y='{y - 14:.0f}' text-anchor='middle' font-size='19' font-weight='700' fill='#e0e0e0'>{n}</text>"
                     f"<text x='{x:.0f}' y='{y + 5:.0f}' text-anchor='middle' font-size='13' fill='#a0a0a0'>{node.get('site', '')}</text>"
                     f"<text x='{x:.0f}' y='{y + 23:.0f}' text-anchor='middle' font-size='12' fill='#e0e0e0'>"
                     f"out ${{n{num[n]}_tx}} / in ${{n{num[n]}_rx}}</text>")
        for j, line in enumerate(ip_lines):
            fill, weight = (color[n], "600") if not line.startswith("meas ") else ("#a0a0a0", "400")
            parts.append(f"<text x='{x:.0f}' y='{ty + 17 * j:.0f}' text-anchor='middle' font-size='13' "
                         f"font-weight='{weight}' fill='{fill}'>{line}</text>")
    parts.append("</svg>")
    src_uri = "data:image/svg+xml," + urllib.parse.quote("".join(parts), safe="${}_")
    anim = {"id": 1, "type": "text", "title": f"{slice_name} - animated route traffic (Mbit/s, refreshes every {refresh})",
            "gridPos": {"x": 0, "y": 0, "w": 24, "h": 17},
            "options": {"mode": "html",
                        "content": f'<img src="{src_uri}" style="width:100%;height:100%;object-fit:contain"/>'}}

    series, w = [], max(6, 24 // max(1, len(names)))
    for i, n in enumerate(names):
        tg = []
        for p in names:
            if p != n and any(n in (a, b) and p in (a, b) for a, b, _ in rts):
                tg.append({"expr": f"rate({sel(n, p, 'tx')}[1m])*8", "legendFormat": f"to {p}",
                           "refId": f"T{num[p]}", "datasource": DS})
                tg.append({"expr": f"-rate({sel(n, p, 'rx')}[1m])*8", "legendFormat": f"from {p}",
                           "refId": f"R{num[p]}", "datasource": DS})
        series.append({"id": 2 + i, "type": "timeseries", "datasource": DS,
                       "title": f"{n} ({by_name[n].get('site', '')}): sent (+) / received (-)",
                       "gridPos": {"x": (w * i) % 24, "y": 17 + 8 * ((w * i) // 24), "w": w, "h": 8},
                       "targets": tg, "fieldConfig": {"defaults": {"unit": "bps"}, "overrides": []},
                       "options": {"legend": {"displayMode": "list", "placement": "bottom"},
                                   "tooltip": {"mode": "multi"}}})

    return {"uid": DASHBOARD_UID, "title": f"{slice_name} - route traffic", "refresh": refresh,
            "time": {"from": "now-15m", "to": "now"}, "schemaVersion": 37,
            "tags": ["mflib", "route_flow", slice_name],
            "templating": {"list": variables}, "panels": [anim] + series}


# ---------------------------------------------------------------- create / update

def setup(logger):
    """Shared body of create.py and update.py. Returns the ret_val dict."""
    ret_val = {"success": True, "msg": ""}
    topo, source = load_topology()
    if topo is None:
        ret_val["msg"] = f"Nothing to do: {source}."
        return ret_val
    logger.info(f"Topology from {source}: {topo}")
    save_topology(topo)
    ret_val["topology_source"] = source

    counters = install_counters(topo, logger)
    ret_val["counters"] = counters
    ret_val["msg"] += counters["msg"] + "\n"
    ret_val["success"] &= counters["success"]

    try:
        dash = upload_dashboard(build_dashboard(topo))
        ret_val["dashboard"] = dash
        ret_val["msg"] += dash["msg"] + "\n"
        ret_val["success"] &= dash["success"]
    except Exception as e:
        logger.exception("Dashboard upload failed")
        ret_val["success"] = False
        ret_val["msg"] += f"Dashboard upload failed: {e}\n"
    return ret_val
