#!/bin/bash
sudo apt update   
sudo apt install -y python3-pip   
pip3 --version 
pip install ansible 
ansible --version 
ansible-galaxy --version 
mkdir -p mf_git 

#ansible-playbook playbook_fabric_experiment_bootstrap1.yml 
echo "Finished!" 



# git clone https://github.com/fabric-testbed/MeasurementFramework.git mf_git
# cd mf_git
# git checkout add_fabric_experiment_role
# bash mf_git/experiment_bootstrap1.sh

# "git clone https://github.com/fabric-testbed/MeasurementFramework.git mf_git;  cd mf_git; git checkout add_fabric_experiment_role; bash mf_git/experiment_bootstrap.sh"
