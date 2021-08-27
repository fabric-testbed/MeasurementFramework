This directory intended for GENI specific scripts.

# Creating hosts file for ansible playbook

## If OMNI is installed on your system
* Run the create_user_files.sh script and enter your slice name
* Your inventory file will be downloaded into this folder
* Your hosts.ini file will be generated and placed in the MeasurementFramework/ansible/hosts directory 

## If OMNI is not installed on your system
* Log into your GENI portal
* Go to your slice's manage resources page
* Click on Details 
* At the bottom of the page click Show Ansible Inventory
* Save the Ansible Inventory file to this folder as 'inventory'
* Run auto_host.py located in this folder
* You will now have a hosts.ini file placed in the MeasurementFramework/ansible/hosts directory
