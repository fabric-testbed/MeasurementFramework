# The meas-node status/health server.
# Ported from fabric-testbed/mflib's mflib-node/mflib_node/server.py so the
# MeasurementFramework repo can ship and manage it as a normal user_service
# (create/start/stop/remove/info) instead of depending on a separate mflib
# clone + pip install on the meas node.
#
# Exposes read-only health/status/inventory endpoints plus a small execute
# and file-transfer surface that mfportal uses to check on and interact with
# the meas node over its FABNetv6 address.

import argparse
import base64
import getpass
import json
import os
import shutil
import socket
import subprocess
import tempfile
from datetime import datetime, timezone
from typing import Optional

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel

_SLICE_INFO = os.environ.get("MFLIB_SLICE_INFO", "/etc/mflib/portal_registration.json")


class ExecuteRequest(BaseModel):
    command: str
    quiet: bool = False
    cwd: Optional[str] = None


class FileTransferRequest(BaseModel):
    remote_file_path: str
    content_base64: Optional[str] = None


class DirectoryTransferRequest(BaseModel):
    remote_directory_path: str
    archive_base64: str
    archive_format: str = "gztar"


def create_app(auth_token: Optional[str] = None, default_cwd: Optional[str] = None):
    app = FastAPI(title="MeasurementFramework meas-node server", version="1.0.0")
    state = {
        "auth_token": auth_token,
        "default_cwd": default_cwd,
    }

    def _authorize(authorization: Optional[str] = Header(default=None)):
        expected = state["auth_token"]
        if not expected:
            return
        if authorization != f"Bearer {expected}":
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

    @app.post("/execute")
    def execute(payload: ExecuteRequest, _: None = Depends(_authorize)):
        process = subprocess.run(
            payload.command,
            shell=True,
            capture_output=True,
            text=True,
            executable="/bin/bash",
            cwd=payload.cwd or state["default_cwd"],
        )
        return {
            "stdout": process.stdout,
            "stderr": process.stderr,
            "returncode": process.returncode,
        }

    @app.post("/upload-file")
    def upload_file(payload: FileTransferRequest, _: None = Depends(_authorize)):
        if payload.content_base64 is None:
            raise HTTPException(status_code=400, detail="content_base64 is required")
        parent = os.path.dirname(payload.remote_file_path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(payload.remote_file_path, "wb") as remote_file:
            remote_file.write(base64.b64decode(payload.content_base64))
        return {"success": True, "remote_file_path": payload.remote_file_path}

    @app.post("/download-file")
    def download_file(payload: FileTransferRequest, _: None = Depends(_authorize)):
        if not os.path.exists(payload.remote_file_path):
            raise HTTPException(status_code=404, detail="Remote file not found")
        with open(payload.remote_file_path, "rb") as remote_file:
            content_base64 = base64.b64encode(remote_file.read()).decode("ascii")
        return {
            "success": True,
            "remote_file_path": payload.remote_file_path,
            "content_base64": content_base64,
        }

    @app.post("/upload-directory")
    def upload_directory(
        payload: DirectoryTransferRequest,
        _: None = Depends(_authorize),
    ):
        if payload.archive_format != "gztar":
            raise HTTPException(status_code=400, detail="Only gztar archives are supported")

        os.makedirs(payload.remote_directory_path, exist_ok=True)
        with tempfile.TemporaryDirectory() as tmpdir:
            archive_path = os.path.join(tmpdir, "upload.tar.gz")
            with open(archive_path, "wb") as archive_file:
                archive_file.write(base64.b64decode(payload.archive_base64))
            shutil.unpack_archive(archive_path, payload.remote_directory_path, "gztar")

        return {
            "success": True,
            "remote_directory_path": payload.remote_directory_path,
        }

    return app


def main():
    parser = argparse.ArgumentParser(description="Run the MeasurementFramework meas-node status/health server")
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--token", default=os.environ.get("MFLIB_API_TOKEN"))
    parser.add_argument("--cwd", default=None)
    args = parser.parse_args()

    import uvicorn

    # Bind IPv6-only so the server is reachable via FABNetv6 but not IPv4.
    sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("::", args.port, 0, 0))
    sock.listen(10)

    print(f"[meas_node_server] listening on [::]:{args.port} (IPv6 / FABNetv6 only)")
    config = uvicorn.Config(create_app(auth_token=args.token, default_cwd=args.cwd))
    server = uvicorn.Server(config)
    server.run(sockets=[sock])


if __name__ == "__main__":
    main()
