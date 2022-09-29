
  
from datetime import datetime
import os
import subprocess
import json



def main():
    ret_val = {}

    playbook_exe = "/home/mfuser/.local/bin/ansible-playbook"
    ansible_hosts_file = '/home/mfuser/services/common/hosts.ini'
 
    keyfile = "/home/mfuser/.ssh/mfuser_private_key"


    # For some reason the local ansible.cfg file is not being used
    os.environ["ANSIBLE_HOST_KEY_CHECKING"] = "False"

    
    # PIP + DOCKER SDK
    ret_val["pip3_docker_sdk"] = {}
    playbook = "/home/mfuser/mf_git/instrumentize/experiment_bootstrap/pip3_docker_sdk_playbook.yml"

    cmd = [playbook_exe, "-i", ansible_hosts_file, "--key-file", keyfile, "-b", playbook]

    r_pip_docker = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    decoded_out_pip_docker = r_pip_docker.stdout.decode("utf-8")
    play_recap_pip_docker = decoded_out_pip_docker[decoded_out_pip_docker.find("PLAY RECAP"):]
    decoded_err_pip_docker = r_pip_docker.stderr.decode("utf-8")

    if r_pip_docker.returncode == 0:
        ret_val["pip3_docker_sdk"]["msg"] = "Pip & Docker SDK ansible script ran.."
        ret_val["pip3_docker_sdk"]["success"] = True
    else:
        ret_val["pip3_docker_sdk"]["msg"] = f"Pip & Docker SDK playbook install failed..{decoded_err_pip_docker}"
        ret_val["pip3_docker_sdk"]["success"] = False

    ret_val["pip3_docker_sdk"]["play_recap"] = play_recap_pip_docker


    # DOCKER
    ret_val["docker"] = {}
    playbook = "/home/mfuser/mf_git/instrumentize/experiment_bootstrap/docker_playbook.yml"

    cmd = [playbook_exe, "-i", ansible_hosts_file, "--key-file", keyfile, "-b", playbook]

    r_docker = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    decoded_out_docker = r_docker.stdout.decode("utf-8")
    play_recap_docker = decoded_out_docker[decoded_out_docker.find("PLAY RECAP"):]
    decoded_err_docker = r_docker.stderr.decode("utf-8")

    if r_docker.returncode == 0:
        ret_val["docker"]["msg"] = "Docker installs OK.."
        ret_val["docker"]["success"] = True
    else:
        ret_val["docker"]["msg"] = f"Docker install failed...{decoded_err_docker}"
        ret_val["docker"]["success"] = False

    ret_val["docker"]["play_recap"] = play_recap_docker


    # PTP
    ret_val["ptp"] = {}
    playbook = "/home/mfuser/mf_git/instrumentize/ptp/ansible/playbook_fabric_experiment_ptp.yml"

    cmd = [playbook_exe, "-i", ansible_hosts_file, "--key-file", keyfile, "-b", playbook]

    r_ptp = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    decoded_out_ptp = r_ptp.stdout.decode("utf-8")
    play_recap_ptp = decoded_out_ptp[decoded_out_ptp.find("PLAY RECAP"):]
    decoded_err_ptp = r_ptp.stderr.decode("utf-8")

    if r_ptp.returncode == 0:
        ret_val["ptp"]["msg"] = "PTP installs OK.."
        ret_val["ptp"]["success"] = True
    else:
        ret_val["ptp"]["msg"] = f"PTP install failed...{decoded_err_ptp}"
        ret_val["ptp"]["success"] = False 

    ret_val["ptp"]["play_recap"] = play_recap_ptp


    ret_val["success"] = (r_pip_docker.returncode == 0) and (r_docker.returncode == 0) and (r_ptp.returncode == 0)



    print(json.dumps(ret_val))


    
if __name__ == "__main__":
    main()
