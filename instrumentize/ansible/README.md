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
* Once you are done you may remove the downloaded files deleting the `instrumentize/ansible/temp_deployment_files` directory. Be cautious not to remove any hosts or variable files you created or altered.


-----

