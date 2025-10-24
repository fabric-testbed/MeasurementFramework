# Public Metrics et al.

Setup instructions for installing the public, infrastructure, and research VMs. From here on Public will refer to one of the 3 systems.

For each VM
### Install Minio
* Setup the drive mapping for the data directory. This is done using `--extra-vars` to set the playbook variable `mount_data_drive` to  `yes` 

`ansible-playbook -i tmp_teployment_files/fabric-hosts playbook_fabric_minio_<public/infrastructure/research>_metrics_install.yml --extra-vars "mount_data_drive=yes"
` 

This will:
  *  format/mount the data drive to `/opt/data` 
  *  setup the MinIO user
  *  create needed directories for the MinIO install
  *  install and start MinIO
  *  creates a named Docker network which will be used by the next install step
After drive has successfully been mounted and mapped, then the `--extra-vars "mount_data_drive=yes"` should not be used again on subsequent playbook runs.

Any needed updates or reinstalls of MinIO should be done by running `ansible-playbook -i tmp_teployment_files/fabric-hosts playbook_fabric_minio_<public/infrastructure/research>_metrics_install.yml`
`
### Install Metrics Containers

The metrics containers can be installed and started using 
`ansible-playbook -i tmp_teployment_files/fabric-hosts playbook_fabric_<public/infrastructure/research>_metrics_install.yml`

The Public Metrics system consists of several containers:
* MinIO - Long term metric storage (already installed above)
* Mimir - Inserts and retrives metrics using MinIO for storage.
* Grafana - Presents metrics to users for visualization or download.
* Prometheus - needed?





Set data source 
promteheus but name mMmir
url http://infrastructure-metrics_mimir:8080/prometheus
custom headers
 X-Scope-OrgID
 value demo
 