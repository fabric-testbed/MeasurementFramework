######
# Remove OWL container on experimenters' nodes by running
# remove_owl.yaml script
#######


from datetime import datetime
import os
import json
import subprocess

def main():
    ret_val = {}

    playbook_exe = "/home/mfuser/.local/bin/ansible-playbook"
    ansible_hosts_file = "/home/mfuser/services/common/hosts.ini"
    playbook = "/home/mfuser/mf_git/user_services/owl/Playbooks/remove_owl.yaml"
    keyfile = "/home/mfuser/.ssh/mfuser_private_key"

    ###  For GENI testing
    #playbook_exe = "/home/mfuser/MeasurementFramework/user_services/owl/owl-venv/bin/ansible-playbook"
    #ansible_hosts_file = "/etc/ansible/hosts"
    #playbook = "/home/mfuser/MeasurementFramework/user_services/owl/Playbooks/remove_owl.yaml"
    #keyfile = "/home/mfuser/.ssh/id_rsa"

    # For some reason the local ansible.cfg file is not being used
    os.environ["ANSIBLE_HOST_KEY_CHECKING"] = "False"

    cmd = [playbook_exe, "-i", ansible_hosts_file, "--key-file", keyfile, '-b', playbook]
    print(cmd)

    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    decoded_out = r.stdout.decode("utf-8")
    play_recap = decoded_out[decoded_out.find("PLAY RECAP"):]
    decoded_err = r.stderr.decode("utf-8")

    if r.returncode == 0:
        ret_val["success"] =  True
        ret_val["msg"] = "remove_owl.yaml ran. OWL conatiner and image successfully removed."
    else:
        ret_val["success"] = False 
        ret_val["msg"] = "remove_owl.yaml playbook failed. OWL container and image not \
                removed from hosts"

    ret_val["play_recap"] = play_recap
    print(json.dumps(ret_val))
    
if __name__ == "__main__":
    main()
