# run the install scripts in instrumentize/ansible/playbook... etc

import os
  
import subprocess

#ansible_dir =  "/home/mfuser/mf_git/instrumentize/ansible/fabric_experiment_instramentize"
#os.chdir(ansible_dir)
playbook_exe = "/home/mfuser/.local/bin/ansible-playbook"
#ansible_hosts_file = "/home/mfuser/mf_git/promhosts.ini"
ansible_hosts_file = '/home/mfuser/mf_git/instrumentize/ansible/fabric_experiment_instramentize/promhosts.ini'
playbook = "/home/mfuser/mf_git/instrumentize/ansible/playbook_fabric_experiment_install_prometheus.yml"
keyfile = "/home/mfuser/.ssh/mfuser"


cmd = [playbook_exe, "-i", ansible_hosts_file, "--key-file", keyfile, "-b", playbook]

r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

print(r.returncode)
print(r.stdout)
print(r.stderr)

# TODO parse the r.stdout to get the PLAY RECAP to return if this worked