# Monitoring Installation and Configuration.
This directory contains ansible scripts that install and configure Fabric monitoring systems.



## Install Prometheus Monitoring On Fabric Rack

* Download the fabric-hosts and vars file from fabric-deployment repo and place into `hosts` directory.  `ansible-playbook playbook_get_fabric_hosts.yml`
* Download the `rack_vars` and place in the `private_vars` directory. TODO setup vars in private repo.
* Install to the rack using `ansible-playbook -i hosts/fabric-hosts playbook_fabric_rack_install.yml --extra-vars "rack_to_install='<sitename>'" --diff` where `<sitename>` is the short site name.
* Remove the downloaded files. `ansible-playbook playbook_remove_fabric_hosts.yml`

Notes:  
The `hosts` and `private_vars` directories are provided as a safe place to hold the needed vars files. Those directories have `.gitignore` files to help prevent commiting private/sensitive data to the repo. However if you delete the `.gitignore` file and leave data in those directories, the data maybe pushed back out to the repo. Be careful. 