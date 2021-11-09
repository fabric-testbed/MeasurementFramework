# Changes needed before Merging
	- In /elk/bootstrap/bootstrap.yml
		- lines 103-107
		- Currently using private fork for testing
		- version 
		- and check
	- In /elk/tasks
		- lines 89-95
		- version
	- Changes to the .gitignore 

# For Geni the Bootstrapping happens from 'Meas_Net'

# Current Issues
	- Name Descripencies between diffrent distros
		- Current implementation 
		https://docs.ansible.com/ansible/latest/collections/ansible/builtin/package_module.html
		- Only allow small number of host OS's to auto install.
			- Sustain writen guide on how to install more.

# Changes Made
	- Removed roles
		- base
	- Changed to only install needed packages
		- only on the nodes that need it

# Tested on and Issues:
	- Ubuntu 20.04 (UBUNTU20-64-STD) => 
		- Does not have epel-release
	- CentOS 7 (CENTOS7-64-STD) => Normal Run

# Working
	- Bootstrap.yml
	- site.yml

# Could change to OS family for some of the calls