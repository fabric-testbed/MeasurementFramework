#!/bin/bash
echo "-----Updating apt-----"
sudo apt update   
echo "-----Installing pip3-----"
sudo apt install -y python3-pip   
pip3 --version 
echo "-----Installing python requirements-----"

pip3 install -r prometheus/ansible/roles/fabric_experiment/meta/requirements.txt

#pip install ansible 
# Not sure why need to hard code full path here
/home/ansible/.local/bin/pip --version 
/home/ansible/.local/bin/ansible --version 
/home/ansible/.local/bin/ansible-galaxy --version 
 

echo "-----Install Galaxy Roles-----"
/home/ansible/.local/bin/ansible-galaxy install -r prometheus/ansible/roles/fabric_experiment/meta/requirements.yml
echo "-----Install Galaxy Collections----"
/home/ansible/.local/bin/ansible-galaxy collection install -r prometheus/ansible/roles/fabric_experiment/meta/requirements.yml

echo "pip freeze:"
pip freeze

echo "-----Finished!-----" 