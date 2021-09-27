Role Name
=========
__linuxptp__ Deploy linuxptp v3.0 on Linux host or KVM nodes

Requirements
------------
- Requires Ansible 2.9 or greater (on the Ansible command center)
- Need to know PTP_SERVER_IP and MANAGEMENT_IP of the host machine
- Currently supported Operating system(destination machines) are 
  - Ubuntu 18.04 or greater
  - CentOS 8 or greater


Role Variables
--------------

**PTP_REPO_URL:** 'http://git.code.sf.net/p/linuxptp/code' [static path to the git repo]

**PTP_PACKAGE_NAME:** 'linuxptp' [Used to form source code path]

**PTP_PACKAGE_TAG:** 'v3.0' [Used to form source code path]

**ALL_NICS:** [Set to True if all NICS on the destination machine need to be PTP Synchronized. Can be overridden when calling role]

**PTP_SERVER_IP:**  [IP of the PTP Server. Is set at the group vars for the playbooks]

**MANAGEMENT_IP_FOR_PTP:** [Defaults to the IP used in the default route.]


Dependencies
------------

None

Example Playbook
----------------
<pre>
  - hosts: all
    roles:
      - { role: linuxptp}
      #- { role: linuxptp,ALL_NICS: False}
</pre>          
License
-------

BSD

Author Information
------------------

Hussamuddin Nasir
(nasir@netlab.uky.edu)
