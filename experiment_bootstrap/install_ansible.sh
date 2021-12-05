#!/bin/bash
echo "Updating apt"
sudo apt update   
echo "Installing pip3"
sudo apt install -y python3-pip   
pip3 --version 
echo "Installing ansible"
pip install ansible 
# Not sure why need to hard code full path here
/home/ansible/.local/bin/ansible --version 
/home/ansible/.local/bin/ansible-galaxy --version 
 
echo "Finished!" 