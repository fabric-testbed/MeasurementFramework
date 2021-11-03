# Changes needed before Merging
	- In /elk/bootstrap/bootstrap.yml
		- lines 103-107
		- Currently using private fork for testing
		- version 
		- and check
	- Changes to the .gitignore 

# Current Issues
	- Name Descripencies between diffrent distros
		- Current implementation 
		https://docs.ansible.com/ansible/latest/collections/ansible/builtin/package_module.html
		- Only allow small number of host OS's to auto install.
			- Sustain writen guide on how to install more.

# Changes Made
	- Changed from state 'latest' to 'present'
	- Removed 'update cache' <= Seems to cause issues with apt 
		- changed: false, "msg": "Failed to lock apt for exclusive operation"
	- Moved alot of install from the base into the elk/tasks

# Tested on and Issues:
	- Ubuntu 20.04 (UBUNTU20-64-STD) => 
		- Does not have epel-release
	- CentOS 7 (CENTOS7-64-STD) => Normal Run

# Working
	- Bootstrap.yml