# meas_node_server Service
Installs and runs the meas-node status/health server (`server.py`, a small
FastAPI app) as a systemd service (`meas-node-server.service`) on the meas
node, bound to its FABNetv6 address (IPv6-only, see `server.py`). mfportal
uses this to check on a meas node's health/status and to run basic
inventory/execute/file-transfer calls against it remotely.

## create
`mflib.create("meas_node_server")` installs the FastAPI/uvicorn
dependencies, generates an auth token (or uses one passed in via `data`,
e.g. `mflib.create("meas_node_server", data={"port": 5000, "token": "..."})`),
writes it to a root-only-readable env file, and starts the systemd service.
The returned dict includes `port` and `token` — the caller (mfportal) needs
both to reach the server afterwards.

Re-running `create` while the service is already active is a no-op that
just reports the existing port; use `remove` first to rotate the token or
change the port.

## start / stop
Starts/stops the existing systemd unit without touching its configuration.

## remove
Stops, disables, and deletes the systemd unit and env file, and clears the
saved port/token so a later `create` starts fresh.

## info
Returns whether the systemd service is active and the server's own
`/status` response (uptime, timestamp).
