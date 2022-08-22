
  
from datetime import datetime
import os
import subprocess
import json



def main():
    ret_val = {}

    playbook_exe = "/home/mfuser/.local/bin/ansible-playbook"
    #ansible_hosts_file = "/home/mfuser/mf_git/promhosts.ini"
    #ansible_hosts_file = '/home/mfuser/mf_git/instrumentize/ansible/fabric_experiment_instramentize/promhosts.ini'
    ansible_hosts_file = '/home/mfuser/services/common/hosts.ini'
 
    keyfile = "/home/mfuser/.ssh/mfuser_private_key"


    # For some reason the local ansible.cfg file is not being used
    os.environ["ANSIBLE_HOST_KEY_CHECKING"] = "False"

    
    # PIP + DOCKER SDK
    playbook = "/home/mfuser/mf_git/instrumentize/experiment_bootstrap/pip3_docker_sdk_playbook.yml"

    cmd = [playbook_exe, "-i", ansible_hosts_file, "--key-file", keyfile, "-b", playbook]

    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    decoded_out = r.stdout.decode("utf-8")
    play_recap = decoded_out[decoded_out.find("PLAY RECAP"):]
    decoded_err = r.stderr.decode("utf-8")

    if r.returncode == 0:
        ret_val["msg"] = "Pip & Docker SDK ansible script ran.."
    else:
        ret_val["msg"] = "Pip & Docker SDK playbook install failed.."

    ret_val["play_recap_pip3_docker_sdk"] = play_recap


    # DOCKER
    playbook = "/home/mfuser/mf_git/instrumentize/experiment_bootstrap/docker_playbook.yml"

    cmd = [playbook_exe, "-i", ansible_hosts_file, "--key-file", keyfile, "-b", playbook]

    r2 = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    decoded_out2 = r2.stdout.decode("utf-8")
    play_recap2 = decoded_out2[decoded_out2.find("PLAY RECAP"):]
    decoded_err2 = r2.stderr.decode("utf-8")

    if r2.returncode == 0:
        ret_val["msg"] = "Docker installs OK.."
    else:
        ret_val["msg"] = "Docker install failed."

    ret_val["play_recap_docker"] = play_recap2


    # PTP
    playbook = "/home/mfuser/mf_git/instrumentize/ptp/ansible/playbook_fabric_experiment_ptp.yml "

    cmd = [playbook_exe, "-i", ansible_hosts_file, "--key-file", keyfile, "-b", playbook]

    r3 = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    decoded_out3 = r3.stdout.decode("utf-8")
    play_recap3 = decoded_out3[decoded_out3.find("PLAY RECAP"):]
    decoded_err3 = r3.stderr.decode("utf-8")

    if r3.returncode == 0:
        ret_val["msg"] = "Docker installs OK.."
    else:
        ret_val["msg"] = "Docker install failed."

    ret_val["play_recap_ptp"] = play_recap3


    ret_val["success"] = (r.returncode == 0) and (r2.returncode == 0) and (r3.returncode == 0)



    print(json.dumps(ret_val))


    
if __name__ == "__main__":
    main()
