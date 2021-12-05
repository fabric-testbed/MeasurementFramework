#!/bin/bash
echo "Updating apt"
sudo apt update   
echo "Installing pip3"
sudo apt install -y python3-pip   
pip3 --version 
echo "Installing ansible"
pip install ansible 
ansible --version 
ansible-galaxy --version 
 
echo "Finished!" 


