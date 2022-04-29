# run the install scripts in instrumentize/ansible/playbook... etc
  
from datetime import datetime
import os
import subprocess

import prom_utilites as pu

#ansible_dir =  "/home/mfuser/mf_git/instrumentize/ansible/fabric_experiment_instramentize"
#os.chdir(ansible_dir)
playbook_exe = "/home/mfuser/.local/bin/ansible-playbook"
#ansible_hosts_file = "/home/mfuser/mf_git/promhosts.ini"
ansible_hosts_file = '/home/mfuser/mf_git/instrumentize/ansible/fabric_experiment_instramentize/promhosts.ini'
playbook = "/home/mfuser/mf_git/instrumentize/ansible/playbook_fabric_experiment_install_prometheus.yml"
keyfile = "/home/mfuser/.ssh/mfuser"

# For some reason the local ansible.cfg file is not being used
os.environ["ANSIBLE_HOST_KEY_CHECKING"] = "False"


grafana_admin_pass = pu.get_grafana_admin_password()
if grafana_admin_pass == None:
    grafana_admin_pass = pu.create_grafana_admin_password()
    
   
cmd = [playbook_exe, "-i", ansible_hosts_file, "--key-file", keyfile, "--extra-vars", f"grafana_admin_password={grafana_admin_pass}" "-b", playbook ]

print(grafana_admin_pass)

#cmd = [playbook_exe, "-i", ansible_hosts_file, "--key-file", keyfile, "-b", playbook ]

r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# print(r.returncode)
# print(r.stdout)
# print(r.stderr)

decoded_out = r.stdout.decode("utf-8")
play_recap = decoded_out[decoded_out.find("PLAY RECAP"):]
decoded_err = r.stderr.decode("utf-8")

if r.returncode == 0:
    print("Prometheus successfully installed.")
else:
    print("Prometheus install playbook failed.")

print(play_recap)

pu.save_ansible_output(r.stdout, r.stderr)


