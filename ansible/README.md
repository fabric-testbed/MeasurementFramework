# Monitoring Installation and Configuration.
This directory contains ansible scripts that install and configure Fabric monitoring systems.



## Install Prometheus Monitoring On Fabric Rack

* Run `ansible-playbook playbook_get_fabric_hosts.yml`  to download the fabric-hosts and vars file from fabric-deployment repo and place into `hosts` directory.  
* Download the `rack_vars` and place in the `private_vars` directory. TODO setup vars in private repo.
* Install to the rack using `ansible-playbook -i hosts/fabric-hosts playbook_fabric_rack_prometheus_install.yml --extra-vars "rack_to_install=<sitename>" --diff` where `<sitename>` is the short site name.
* Remove the downloaded files. `ansible-playbook playbook_remove_fabric_hosts.yml`

Notes:  
The `hosts` and `private_vars` directories are provided as a safe place to hold the needed vars files. Those directories have `.gitignore` files to help prevent commiting private/sensitive data to the repo. However if you delete the `.gitignore` file and leave data in those directories, the data maybe pushed back out to the repo. Be careful. 

If reinstalling you might want to use --extra-vars "install_node_exporters=no" to save time.



## Install Fabric Central Monitoring

* Create/Download the needed hosts file:
```
[metrics]
192.168.12.251 hostname=metrics.fabric-testbed.net
```
or
```
[metrics]
192.168.12.238 hostname=dev-metrics.fabric-testbed.net
```
* Create/Download the needed vars file. Most variables have defaults, however several will need to be defined. All private variables will also need to be defined. #TODO document them
* Install using `ansible-playbook -i central_hosts.ini --extra-vars "@<your_extra_vars.yml>" playbook_fabric_central_install.yml --diff --check`  
  Examples:
  * `ansible-playbook -i central_hosts.ini --extra-vars "@central_vars.yml" playbook_fabric_central_install.yml --diff --check`
  * `ansible-playbook -i hosts/dev_central_hosts.ini --extra-vars "@private_vars/dev_central_vars.yml" playbook_fabric_central_install.yml --diff --check`
  * `ansible-playbook -i dev_central_hosts.ini --extra-vars "@dev_central_vars.yml" playbook_fabric_central_install.yml --diff --check`