# Monitoring Installation and Configuration.
This directory contains ansible scripts that install and configure Fabric monitoring systems.


-----
## Dev-Install Prometheus Monitoring On Fabric Rack
For developing the Fabric Rack system:
* Run `ansible-playbook playbook_get_fabric_deployment_files.yml`. This will download the fabric-hosts and vars file from fabric-deployment repo and place them into `tmp_deployment_files` directory.  
* Install to the rack using `ansible-playbook -i tmp_deployment_files/fabric-hosts playbook_fabric_rack_prometheus_install.yml --vault-password-file <vault-password-file> --extra-vars "rack_to_install=<sitename>" --diff` where `<sitename>` is the short site name and `<valut-password-file>` is the path to the file that contains the vault password.
Once you are done you maner remove the downloaded files using `ansible-playbook playbook_remove_fabric_deploymnet_files.yml`. Be cautious not to remove any hosts or variable files you created or altered.
  
Notes:
The `tmp_deployment_files` directory is provided as a safe place to hold the needed hosts and vars files. Those directories have `.gitignore` files to help prevent commiting private/sensitive data to the repo. However if you delete the `.gitignore` file and leave data in those directories, the data maybe pushed back out to the repo. Be careful. 

The `hosts` and `private_vars` directories are provided as a safe place to hold the needed vars files. Those directories have `.gitignore` files to help prevent commiting private/sensitive data to the repo. However if you delete the `.gitignore` file and leave data in those directories, the data maybe pushed back out to the repo. Be careful. 

If reinstalling you might want to use --extra-vars "install_node_exporters=no" to save time.


-----
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
  * For central metrics `ansible-playbook -i hosts/central_hosts.ini --extra-vars "@private_vars/central_vars.yml" playbook_fabric_central_install.yml --diff --check`
  * For dev central metrics `ansible-playbook -i hosts/dev_central_hosts.ini --extra-vars "@private_vars/dev_central_vars.yml" playbook_fabric_central_install.yml --diff --check`
  
-----
## Install Prometheus Monitoring on a GENI Slice

### Initial Testing Instructions
These instructions are for testing and assume you have access to a slice with public ips, you have your GENI key, and you have created the private_vars files. 

Need to create the inventory file for the GENI slice and the corresponding variables file. Use the resulting geni_slice_hosts.ini and geni_slice_vars to install the system to the slice. 

To install from a machine on which you have geni keys use: 

* ~Install Everything~ `ansible-playbook --key-file "~/.ssh/id_geni_ssh_rsa" -i hosts/geni_slice_hosts.ini --extra-vars "@private_vars/geni_slice_vars.yml" playbook_geni_slice_install.yml --diff --check`

* ~Install Just the Monitor~ `ansible-playbook --key-file "~/.ssh/id_geni_ssh_rsa" -i hosts/geni_slice_hosts.ini --extra-vars "@private_vars/geni_slice_vars.yml" playbook_geni_slice_install.yml --diff --tags monitor --check`

* ~Install Just the Exporters~ `ansible-playbook --key-file "~/.ssh/id_geni_ssh_rsa" -i hosts/geni_slice_hosts.ini --extra-vars "@private_vars/geni_slice_vars.yml" playbook_geni_slice_install.yml --diff --tags exporters --check`

### GENI test after ansible scripts are run.
#### Prometheus
Go to the monitor node's Prometheus web UI at https://<monitor_node_ip>:9090  
You will have to type in the username and password that you set in the variable file.
Click on the "Status" drop down and choose "Targets".  Assuming the system has been up for a few minutes all of the target's state should be a green UP.  
Click on the "Graph" link and type "up" in the search box. Click "Execute". You should see a ping job for each node, a node jobe for each node and then the docker adn prometheus jobs.

#### Grafana
Go to the Grafana web UI at https://<monitor_node_ip>/grafana  
Type in "admin" for the user and the password you set in the variables file.  
Click on the compass icon to the left to open the Explore page. Type "up" for the metrics query the click "Run Query". You should see the same list you saw in the Prometheus test.  
Hover over the four squares icon and click Manage.  Click Import. Type in "1860" and click "Load". Keep defaults but Choose "Prometheus" as the datascource in the bottom drop down. Click "Import".  
Now in your Dashboards list you will See "Node Exporter Full". Open the dashboard and see if the drop down for the "Hosts" has all of the nodes for the slice.
#### Check status on Monitor node
SSH into the monitor node. Type `docker ps` to see if all the containers are running. Depending on your install variable you should have: 
* prometheus
* grafana
* nginx
* blackbox
* docker_exporter

This should match what results when you run the query "docker_container_running_state" on the Explore page in Grafana.  

-----
