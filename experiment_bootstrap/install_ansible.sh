#!/bin/bash
echo "-----Updating apt-----"
sudo apt update   
echo "-----Installing pip3-----"
sudo apt install -y python3-pip   
pip3 --version 
echo "-----Installing ansible-----"
pip install ansible 
# Not sure why need to hard code full path here
/home/ansible/.local/bin/ansible --version 
/home/ansible/.local/bin/ansible-galaxy --version 
 


echo "-----Install Galaxy Roles-----"
/home/ansible/.local/bin/ansible-galaxy install -r fabric_prometheus/ansible/roles/fabric_experiment/meta/requirements.yml
echo "-----Install Galaxy Collections----"
/home/ansible/.local/bin/ansible-galaxy collection install -r fabric_prometheus/ansible/roles/fabric_experiment/meta/requirements.yml



echo "-----Finished!-----" 