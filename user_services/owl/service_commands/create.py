### TODO: Change this to OWL
# Create ELK service
  
from datetime import datetime
import os
import json
import subprocess

def main():
    ret_val = {}

    #playbook_exe = "/home/mfuser/.local/bin/ansible-playbook"
    #ansible_hosts_file = "/home/mfuser/mf_git/elkhosts.ini"
    #playbook = "/home/mfuser/mf_git/instrumentize/elk/fabric_deploy.yml"
    #keyfile = "/home/mfuser/.ssh/mfuser"

    playbook_exe = "/home/mfuser/MeasurementFramework/user_services/owl/owl-venv/bin/ansible-playbook"
    ansible_hosts_file = "/etc/ansible/hosts"
    playbook = "/home/mfuser/MeasurementFramework/user_services/owl/Playbooks/create_owl.yaml"
    keyfile = "/home/mfuser/.ssh/id_rsa"


    # For some reason the local ansible.cfg file is not being used
    os.environ["ANSIBLE_HOST_KEY_CHECKING"] = "False"

    cmd = [playbook_exe, "-i", ansible_hosts_file, "--key-file", keyfile, , playbook]

    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    decoded_out = r.stdout.decode("utf-8")
    play_recap = decoded_out[decoded_out.find("PLAY RECAP"):]
    decoded_err = r.stderr.decode("utf-8")

    if r.returncode == 0:
        ret_val["success"] =  True
        ret_val["msg"] = "create_owl.yaml script ran successfully."
    else:
        ret_val["success"] =  False
        ret_val["msg"] = "create_owl.yaml script run FAILED."

    ret_val["play_recap"] = play_recap
    print(json.dumps(ret_val))
    
if __name__ == "__main__":
    main()
