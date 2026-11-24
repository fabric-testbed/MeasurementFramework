# mflib_mcp Service

Brings up [fabric-testbed/mflib_portal_mcp](https://github.com/fabric-testbed/mflib_portal_mcp)
-- an MCP (Model Context Protocol) server that answers natural-language
questions about this slice's nodes using fixed PromQL queries from the
Node Exporter Full dashboard -- as an additional container beside this
node's existing Prometheus/Grafana/nginx stack, reachable at
`https://<node>/mcp`.

## Self-start only, not a core service

Unlike `prometheus`/`grafana_manager`/`meas_node_server`, this service is
**not** created automatically on every meas node. It is staged (like every
`user_service`) at bootstrap, but only actually **created** when the meas
node was stood up through the portal's automated flow
(`MFPortal.create_meas_node_slice()`'s generated self-start script) -- see
`instrumentize/experiment_bootstrap/service_scripts/mflib_mcp.py`'s comment
for exactly why. A meas node created by hand (e.g. calling
`mflib.create("prometheus")` directly in a notebook) never gets it unless
you explicitly call `mflib.create("mflib_mcp")` yourself.

## create

`mflib.create("mflib_mcp")`:
1. Reads `/home/mfuser/mflib_mcp_token` if present (dropped by the portal
   before self-start, the same credential already used for that slice's
   `view_url`) -- generates and saves its own token instead if the file
   isn't there (e.g. a standalone/manual `create()` call).
2. Clones (or pulls, if already present) `mflib_portal_mcp` and runs its own
   shipped `docker compose up -d --build` unmodified -- it already joins the
   external `fabric_prometheus` network and resolves Grafana by container
   name, exactly as this role's other containers do.
3. Templates a `location /mcp { ... }` block into the currently-active nginx
   confd file (`grafana_with_ssl_only.conf`), with a literal bearer-token
   check (`if ($http_authorization != "Bearer <token>") { return 401; }`)
   before the `proxy_pass` -- the *only* access-control layer here, since the
   MCP server itself has no auth of its own (by design; see its own repo's
   README). Then validates (`nginx -t`) and restarts nginx.

Re-running `create` replaces the previously-installed `/mcp` block (e.g. if
the token changed) instead of duplicating it, and re-pulls/rebuilds the
container -- safe to call again.

## remove

Strips the nginx `/mcp` location and `docker compose down`s the container.
Leaves the cloned repo and token file in place so a later `create` doesn't
need to regenerate anything.

## info

Reports whether the container is running and whether a token file exists.
