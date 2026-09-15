# Grafana Manager Service

The Grafana manager service provides interfaces for interacting with Grafana.
Methods will be provided for:
* Getting Grafana admin password.
* Adding custom dashboards.
* User management - add, remove, change passwords, retrieve passwords.
* Adding custom datasources.

`create.py` also sets Grafana's `GF_SECURITY_CSRF_TRUSTED_ORIGINS` from
`external_hostname` in `/etc/mflib/portal_registration.json` (if present) and
restarts the Grafana container to apply it, before doing anything else --
this is what lets users reach Grafana through the portal's dynamic reverse
proxy without CSRF rejecting query API calls. Skipped if that field is
missing (older meas-nodes, or `PORTAL_DOMAIN` unset on the portal).