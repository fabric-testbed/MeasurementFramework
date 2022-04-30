# run the install scripts in instrumentize/ansible/playbook... etc
  
from datetime import datetime
import os
import subprocess

import prom_utilites as pu

ret_val = {}

#ansible_dir =  "/home/mfuser/mf_git/instrumentize/ansible/fabric_experiment_instramentize"
#os.chdir(ansible_dir)
playbook_exe = "/home/mfuser/.local/bin/ansible-playbook"
#ansible_hosts_file = "/home/mfuser/mf_git/promhosts.ini"
ansible_hosts_file = '/home/mfuser/mf_git/instrumentize/ansible/fabric_experiment_instramentize/promhosts.ini'
playbook = "/home/mfuser/mf_git/instrumentize/ansible/playbook_fabric_experiment_install_prometheus.yml"
keyfile = "/home/mfuser/.ssh/mfuser"


# For some reason the local ansible.cfg file is not being used
os.environ["ANSIBLE_HOST_KEY_CHECKING"] = "False"

pu.create_install_vars()
   
cmd = [playbook_exe, "-i", ansible_hosts_file, "--key-file", keyfile, "--extra-var", f'"@{ pu.install_vars_file }"', "-b", playbook ]

ret_val["grafana_admin_pass"] = pu.get_grafana_admin_password()

r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# print(r.returncode)
# print(r.stdout)
# print(r.stderr)

decoded_out = r.stdout.decode("utf-8")
play_recap = decoded_out[decoded_out.find("PLAY RECAP"):]
decoded_err = r.stderr.decode("utf-8")

if r.returncode == 0:
    ret_val["success"] =  True
    ret_val["msg"] = "Prometheus successfully installed."
else:
    ret_val["success"] =  True
    ret_val["msg"] = "Prometheus playbook install failed.."

ret_val["play_recap"] = play_recap

pu.save_ansible_output(r.stdout, r.stderr)


print(pu.get_json_string(ret_val))
