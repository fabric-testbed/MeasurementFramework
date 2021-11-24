# Monitoring Installation and Configuration.
This directory contains ansible scripts that install and configure Fabric monitoring systems.


-----
## Dev-Install Prometheus Monitoring On Fabric Rack
For developing the Fabric Rack system:
* Run `ansible-playbook playbook_get_fabric_deployment_files.yml`. This will download the fabric-hosts and vars file from fabric-deployment repo and place them into `tmp_deployment_files` directory.  
* Install to the rack using `ansible-playbook -i tmp_deployment_files/fabric-hosts playbook_fabric_rack_prometheus_install.yml --vault-password-file <vault-password-file> --extra-vars "rack_to_install=<sitename>" --diff` where `<sitename>` is the short site name and `<valut-password-file>` is the path to the file that contains the vault password.
* Once you are done you may remove the downloaded files using `ansible-playbook playbook_remove_fabric_deploymnet_files.yml`. Be cautious not to remove any hosts or variable files you created or altered.
  
Notes:
* The `tmp_deployment_files` directory is provided as a safe place to hold the needed hosts and vars files. Those directories have `.gitignore` files to help prevent commiting private/sensitive data to the repo. However if you delete the `.gitignore` file and leave data in those directories, the data maybe pushed back out to the repo. Be careful. 

* Deprecating this ~The `hosts` and `private_vars` directories are provided as a safe place to hold the needed vars files. Those directories have `.gitignore` files to help prevent commiting private/sensitive data to the repo. However if you delete the `.gitignore` file and leave data in those directories, the data maybe pushed back out to the repo. Be careful. ~

* If reinstalling you might want to use --extra-vars "install_node_exporters=no" to save time.
* Important! Dev racks uky and renc are hardcoded to have the base install dirs backed up before deleting them for complete overwrites. Productions racks should never be manipulated except by ansible scriptes so the will always be deleted on a reinstall. 

### Test If Install Worked

Test if rack is gathering data. Tunnel into the head node from a machine on the operator head node. 
`ssh -L 9090:localhost:9090 <user>@192.168.12.10` Then go to `https://localhost:9090`
on your local browser.


Tip: If you need to acces multiple racks at the same time try: `ssh -L 100,rack_no>:localhost:9090 <user>@192.168.12.10` Then go to `https://localhost:100<rack_no>`



-----
## Install Fabric Central Monitoring



* Run `ansible-playbook playbook_get_fabric_deployment_files.yml`. This will download the fabric-hosts and vars file from fabric-deployment repo and place them into `tmp_deployment_files` directory. 
* Install using the following. If you do not have an ansible config file you will need to add `--vault-password-file <vault_password_file>` 
  * For central metrics `ansible-playbook -i tmp_deployment_files/fabric-hosts playbook_fabric_central_install.yml --diff` 
  * For dev central metrics `ansible-playbook -i tmp_deployment_files/fabric-hosts playbook_fabric_dev_central_install.yml --diff` 
* Once you are done you may remove the downloaded files using `ansible-playbook playbook_remove_fabric_deploymnet_files.yml`. Be cautious not to remove any hosts or variable files you created or altered.


-----
## Install Prometheus Monitoring on a GENI Slice

### Initial Testing Instructions
These instructions are for testing and assume you have access to a slice with public ips, you have your GENI key, and you have created the private_vars files. 

Need to create the inventory file for the GENI slice and the corresponding variables file. Use the resulting geni_slice_hosts.ini and geni_slice_vars to install the system to the slice. 

To install from a machine on which you have geni keys use: 

* Install Everything `ansible-playbook --key-file "~/.ssh/id_geni_ssh_rsa" -i hosts/geni_slice_hosts.ini --extra-vars "@private_vars/geni_slice_vars.yml" playbook_geni_slice_install.yml --diff --check`

* Install Just the Monitor `ansible-playbook --key-file "~/.ssh/id_geni_ssh_rsa" -i hosts/geni_slice_hosts.ini --extra-vars "@private_vars/geni_slice_vars.yml" playbook_geni_slice_install.yml --diff --tags monitor --check`

* Install Just the Exporters `ansible-playbook --key-file "~/.ssh/id_geni_ssh_rsa" -i hosts/geni_slice_hosts.ini --extra-vars "@private_vars/geni_slice_vars.yml" playbook_geni_slice_install.yml --diff --tags exporters --check`

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
