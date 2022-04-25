Role Name
=========
__linuxptp__ Deploy linuxptp v3.1.1 on Linux host or KVM nodes

Requirements
------------
- Requires Ansible 2.9 or greater (on the Ansible command center)
- Currently supported Operating system(destination machines) are 
  - Ubuntu 18.04 or greater
  - CentOS 8 or greater

Example Playbook
----------------
<pre>
  - hosts: all
    roles:
      - linuxptp
      #- { role: linuxptp,ALL_NICS: False}
</pre>          

Example Run
----------------
<pre>
ansible-playbook -i <INVENTORY_FILE> playbook_fabric_experiment_ptp.yml --tags=ptp_install
ansible-playbook -i <INVENTORY_FILE> playbook_fabric_experiment_ptp.yml --tags=ptp_start
ansible-playbook -i <INVENTORY_FILE> playbook_fabric_experiment_ptp.yml --tags=ptp_stop
</pre>          
License
-------

BSD

Author Information
------------------

Hussamuddin Nasir
(nasir@netlab.uky.edu)
