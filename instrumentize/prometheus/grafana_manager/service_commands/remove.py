# Not sure what remove would do in this case?
# Grafana will continue to run with or without dashboards and users.
# Too dangerous to remove users and dashboards - they should persist. Specific removals should be in the update.
print '{ "success": true, "msg": "Nothing to remove."}'