# Fabric Prometheus Ansible Roles 
This directory contains the ansible files needed to create the fabric_prometheus roles.
* Two roles are for the infrastructure monitoring:
  * fabric_central - setting up the central metrics server 
  * fabric_rack - setting up a single rack
* geni - for adding monitoring to a geni slice
* common - for tasks and files that are common to all roles. Files in the common directories should be editied with extreme caution as they will effect all roles that reference them.

See the MeasurmentFramework/ansible directory for playbooks to run the installs.
