# Current Issues
	- Name Descripencies between diffrent distros
		- Current implementation 
		https://docs.ansible.com/ansible/latest/collections/ansible/builtin/package_module.html
		- Only allow small number of host OS's to auto install.
			- Sustain writen guide on how to install more.

# Changes Made
	- Changed from state 'latest' to 'present'
		- 

# Tested on and Issues:
	- Ubuntu 20.04 (UBUNTU20-64-STD) => 
		- Does not have epel-release
			- {"ansible_facts": {"pkg_mgr": "apt"}, "changed": false, "msg": "No package matching 'epel-release' is available"}
	- CentOS 7 (CENTOS7-64-STD) => Normal Run
