Currenlty implemented as if called from the users device.

Meaning that it needs the full name and address that it why the ansible.cfg points to the bootstrap hosts.


# How to Run
	- bash: ansible-playbook {Whichever play needed.}
	- EX 1: ansible-playbook All_FileBeat_service_stopped.yml
	- EX 2: ansible-playbook All_FileBeat_service_restarted.yml
	

# Implementation
	- Filebeat
		- Currently all nodes stopped
		- Currently all nodes restarted
	- Metricbeat
		- Currently all nodes stopped
		- Currently all nodes restarted
	- Packetbeat
		- Currently all nodes stopped
		- Currently all nodes restarted

# Work in progress
	- Individual nodes managed
	- Python code

# Issues
	- Delay from command to updating logs on dashboard
		- couple of minutes
		
