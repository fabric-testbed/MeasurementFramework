# Start Timestamp serivice by running start_timestamp_service.yaml
import os
from os.path import exists
import json
import logging
import subprocess

def main():
    ret_val = {}
    ret_val['msg'] = ""

    playbook_exe = "/home/mfuser/.local/bin/ansible-playbook"
    ansible_hosts_file = "/home/mfuser/services/common/hosts.ini"
    playbook = "/home/mfuser/mf_git/user_services/timestamp/playbooks/start_timestamp_service.yaml"
    keyfile = "/home/mfuser/.ssh/mfuser_private_key"

    # Data is stored in relative dir to this script.
    service_dir =  os.path.dirname(__file__)
    logFilePath = os.path.join(service_dir, "log", "start.log")
    logging.basicConfig(filename=logFilePath, format='%(asctime)s %(name)-8s %(levelname)-8s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level="INFO")
    logging.info("-----Start Timestamp Start Script.-----")

    # For some reason the local ansible.cfg file is not being used
    os.environ["ANSIBLE_HOST_KEY_CHECKING"] = "False"

    cmd = [playbook_exe, "-i", ansible_hosts_file, "--key-file", keyfile, "-b", playbook]
    logging.info(cmd)

    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    decoded_out = r.stdout.decode("utf-8")
    play_recap = decoded_out[decoded_out.find("PLAY RECAP"):]
    decoded_err = r.stderr.decode("utf-8")

    #logging.info(r)
    logging.info("STDOUT")
    logging.info(decoded_out)
    logging.info("STDERR")
    logging.error(decoded_err)

    if r.returncode == 0:
        ret_val["success"] =  True
        ret_val["msg"] = "Timestamp start playbook ran.."
    else:
        ret_val["success"] =  False
        ret_val["msg"] += "Timestamp start playbook install failed.."
    logging.info(ret_val['msg'])
    ret_val["play_recap"] = play_recap

    logging.info("Timestamp start.yaml playbook completed.")

    logging.info("-----End Timestamp Start Script.-----")
    print(json.dumps(ret_val))

if __name__ == "__main__":
    main()