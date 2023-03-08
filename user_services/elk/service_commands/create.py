# Create ELK service
  
from datetime import datetime
import os
import json
import subprocess
import logging

def main():

    ret_val = {}
    ret_val['msg'] = ""

    playbook_exe = "/home/mfuser/.local/bin/ansible-playbook"
    ansible_hosts_file = "/home/mfuser/services/hosts.ini"
    playbook = "/home/mfuser/mf_git/instrumentize/elk/fabric_deploy.yml"
    keyfile = "/home/mfuser/.ssh/mfuser_private_key"


    # Data is stored in relative dir to this script.
    service_dir =  os.path.dirname(__file__)
    logFilePath = os.path.join(service_dir, "log", "create.log")
    logging.basicConfig(filename=logFilePath, format='%(asctime)s %(name)-8s %(levelname)-8s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level="INFO")
    logging.info("-----Start Ceate Script.-----")


    # For some reason the local ansible.cfg file is not being used
    os.environ["ANSIBLE_HOST_KEY_CHECKING"] = "False"
    os.environ["PYTHONUNBUFFERED"] = "1"

    cmd = [playbook_exe, "-i", ansible_hosts_file, "--key-file", keyfile, "-b", playbook, "-v"]
    logging.info(cmd)

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    isRecap = False
    play_recap = ""

    for line in iter(p.stdout.readline, b''):
        curLine = line.rstrip().decode("utf-8")
        logging.info(curLine)

        if curLine.find("RECAP") > 0:
            isRecap = True

        if isRecap:
            play_recap = play_recap + "\n" + curLine

    p.stdout.close()
    p.wait()

    if p.returncode == 0:
        ret_val["success"] =  True
        ret_val["msg"] = "ELK ansible script ran.."
    else:
        ret_val["success"] =  False
        ret_val["msg"] = "ELK playbook install failed.."
    logging.info(ret_val['msg'])
    ret_val["play_recap"] = play_recap

    logging.info("Ansible elk install playbooks completed.")

    logging.info("-----End Ceate Script.-----")
    print(json.dumps(ret_val))

if __name__ == "__main__":
    main()
