from datetime import datetime
import os
import subprocess
import json


def main():
    ret_val = {}

    home_base = "/homes/mfuser"
    playbook_exe = home_base + "/.local/bin/ansible-playbook"
    ansible_hosts_file = home_base + "/services/common/hosts.ini"

    keyfile = home_base + "/.ssh/mfuser_private_key"

    # For some reason the local ansible.cfg file is not being used
    os.environ["ANSIBLE_HOST_KEY_CHECKING"] = "False"
    os.environ["ANSIBLE_SSH_RETRIES"] = "5"
    os.environ["ANSIBLE_CONFIG"] = home_base + "/mf_git/instrumentize/experiment_bootstrap/ansible.cfg"

    ret_val["ansible_bootstrap"] = {}
    playbook = home_bsae + "/mf_git/instrumentize/experiment_bootstrap/bootstrap.yml"

    cmd = [
        playbook_exe,
        "-i",
        ansible_hosts_file,
        "--key-file",
        keyfile,
        "-b",
        playbook,
    ]

    r_bootstrap = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    decoded_out_bootstrap = r_bootstrap.stdout.decode("utf-8")
    play_recap_bootstrap = decoded_out_bootstrap[
        decoded_out_bootstrap.find("PLAY RECAP") :
    ]
    decoded_err_bootstrap = r_bootstrap.stderr.decode("utf-8")

    if r_bootstrap.returncode == 0:
        ret_val["ansible_bootstrap"]["msg"] = "Bootstrap ansible script ran.."
        ret_val["ansible_bootstrap"]["success"] = True
    else:
        ret_val["ansible_bootstrap"]["msg"] = f"Bootstrap playbook install failed..{decoded_err_bootstrap}"
        ret_val["ansible_bootstrap"]["success"] = False

    ret_val["ansible_bootstrap"]["play_recap"] = play_recap_bootstrap


    ret_val["success"] = (
        (r_bootstrap.returncode == 0)
    )

    print(json.dumps(ret_val))


if __name__ == "__main__":
    main()
