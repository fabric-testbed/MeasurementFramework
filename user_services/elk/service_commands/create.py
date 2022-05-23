# Create ELK service
  
from datetime import datetime
import os
import json
import subprocess

def main():
    ret_val = {}

    playbook_exe = "/home/mfuser/.local/bin/ansible-playbook"
    ansible_hosts_file = "/home/mfuser/mf_git/elkhosts.ini"
    playbook = "/home/mfuser/mf_git/instrumentize/elk/fabric_deploy.yml"
    keyfile = "/home/mfuser/.ssh/mfuser"

    # For some reason the local ansible.cfg file is not being used
    os.environ["ANSIBLE_HOST_KEY_CHECKING"] = "False"

    cmd = [playbook_exe, "-i", ansible_hosts_file, "--key-file", keyfile, "-b", playbook]

    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    decoded_out = r.stdout.decode("utf-8")
    play_recap = decoded_out[decoded_out.find("PLAY RECAP"):]
    decoded_err = r.stderr.decode("utf-8")

    if r.returncode == 0:
        ret_val["success"] =  True
        ret_val["msg"] = "ELK ansible script ran.."
    else:
        ret_val["success"] =  True
        ret_val["msg"] = "ELK playbook install failed.."

    ret_val["play_recap"] = play_recap
    print(json.dumps(ret_val))
    
if __name__ == "__main__":
    main()