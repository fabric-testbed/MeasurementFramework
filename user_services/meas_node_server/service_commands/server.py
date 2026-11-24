# The meas-node status/health server.
# Ported from fabric-testbed/mflib's mflib-node/mflib_node/server.py so the
# MeasurementFramework repo can ship and manage it as a normal user_service
# (create/start/stop/remove/info) instead of depending on a separate mflib
# clone + pip install on the meas node.
#
# Every endpoint is read-only and needs the bearer token. There is
# deliberately no command-execution or file-transfer endpoint: mfportal
# proxies this port to the internet, so anything here is reachable by
# whoever holds the token. Add a narrow, fixed endpoint for each new need
# (like /grafana-admin-password) rather than a general one.

import argparse
import getpass
import hmac
import json
import os
import socket
import subprocess
import sys
from datetime import datetime, timezone
from typing import Optional

from fastapi import Depends, FastAPI, Header, HTTPException

_SLICE_INFO = os.environ.get("MFLIB_SLICE_INFO", "/etc/mflib/portal_registration.json")
# Written by prometheus/create.py (prom_utilites.install_vars_file).
_PROMETHEUS_INSTALL_VARS = os.environ.get(
    "MFLIB_PROMETHEUS_INSTALL_VARS",
    "/home/mfuser/services/prometheus/extra_files/install_vars.json",
)


def create_app(auth_token: str):
    if not auth_token:
        raise ValueError("meas_node_server requires an auth token")
    # No /docs, /redoc or /openapi.json: they would be served without the token.
    app = FastAPI(title="MeasurementFramework meas-node server", version="1.1.0",
                  docs_url=None, redoc_url=None, openapi_url=None)
    expected = f"Bearer {auth_token}".encode()

    def _authorize(authorization: Optional[str] = Header(default=None)):
        if not authorization or not hmac.compare_digest(authorization.encode(), expected):
            raise HTTPException(status_code=401, detail="Unauthorized")

    @app.get("/health")
    def health(_: None = Depends(_authorize)):
        return {"status": "ok"}

    @app.get("/status")
    def status(_: None = Depends(_authorize)):
        try:
            with open("/proc/uptime") as f:
                up_sec = float(f.read().split()[0])
        except Exception:
            up_sec = None
        return {
            "status": "ok",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "uptime_seconds": up_sec,
        }

    @app.get("/ip")
    def ip_info(_: None = Depends(_authorize)):
        try:
            r = subprocess.run(
                ["ip", "-j", "addr", "show"],
                capture_output=True, text=True, timeout=5,
            )
            ifaces = json.loads(r.stdout) if r.returncode == 0 else []
        except Exception as e:
            ifaces = {"error": str(e)}
        return {"hostname": socket.gethostname(), "interfaces": ifaces}

    @app.get("/slice")
    def slice_info(_: None = Depends(_authorize)):
        if not os.path.exists(_SLICE_INFO):
            raise HTTPException(
                status_code=404,
                detail=f"{_SLICE_INFO} not found — node may not be registered yet",
            )
        try:
            with open(_SLICE_INFO) as f:
                return json.load(f)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/metadata")
    def metadata(_: None = Depends(_authorize)):
        return {
            "name": os.environ.get("MFLIB_NODE_NAME", socket.gethostname()),
            "username": os.environ.get("MFLIB_NODE_USERNAME", getpass.getuser()),
            "management_ip": os.environ.get("MFLIB_MANAGEMENT_IP", "127.0.0.1"),
        }

    @app.get("/grafana-admin-password")
    def grafana_admin_password(_: None = Depends(_authorize)):
        # 404 until prometheus/create.py has generated the password.
        try:
            with open(_PROMETHEUS_INSTALL_VARS) as f:
                password = json.load(f).get("grafana_admin_password")
        except (OSError, ValueError):
            password = None
        if not password:
            raise HTTPException(status_code=404, detail="Grafana admin password not generated yet")
        return {"grafana_admin_password": password}

    return app


def main():
    parser = argparse.ArgumentParser(description="Run the MeasurementFramework meas-node status/health server")
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--token", default=os.environ.get("MFLIB_API_TOKEN"))
    args = parser.parse_args()
    if not args.token:
        sys.exit("[meas_node_server] no token: set MFLIB_API_TOKEN (create.py does this). Refusing to start.")

    import uvicorn

    # IPv6-only on every IPv6 address of the node (not just FABNetv6: a node
    # whose management interface has a public IPv6 address is reachable there
    # too). The token is what protects it.
    sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("::", args.port, 0, 0))
    sock.listen(10)

    print(f"[meas_node_server] listening on [::]:{args.port} (IPv6 / FABNetv6 only)")
    config = uvicorn.Config(create_app(auth_token=args.token))
    server = uvicorn.Server(config)
    server.run(sockets=[sock])


if __name__ == "__main__":
    main()
