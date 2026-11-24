# mflib_mcp service
This is an introduction page for the mflib_mcp service.
It runs fabric-testbed/mflib_portal_mcp (an MCP server for this slice's
Node Exporter Full dashboard) as a container beside the node's existing
Prometheus/Grafana/nginx stack, reachable at `https://<node>/mcp`. Unlike
the other services in this directory, it is only created automatically as
part of the portal's self-start flow, not on every meas node -- see
service_commands/README.md for details.
