# Create ELK service
  
from datetime import datetime
import os
import json
import subprocess
import logging
import socket
import requests

def main():

    ret_val = {}
    ret_val['msg'] = ""

    playbook_exe = "/home/mfuser/.local/bin/ansible-playbook"
    ansible_hosts_file = "/home/mfuser/mf_git/elkhosts.ini"
    playbook = "/home/mfuser/mf_git/instrumentize/elk/fabric_deploy.yml"
    keyfile = "/home/mfuser/.ssh/mfuser_private_key"


    # Data is stored in relative dir to this script.
    service_dir =  os.path.dirname(__file__)
    logFilePath = os.path.join(service_dir, "log", "create.log")
    logging.basicConfig(filename=logFilePath, format='%(asctime)s %(name)-8s %(levelname)-8s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level="INFO")
    logging.info("-----Start Ceate Script.-----")


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
        ret_val["msg"] = "ELK ansible script ran.."
    else:
        ret_val["success"] =  False
        ret_val["msg"] = "ELK playbook install failed.."
    logging.info(ret_val['msg'])
    ret_val["play_recap"] = play_recap

    logging.info("Ansible elk install playbooks completed.")

    # Should be moved to update.py? or to kibana_manager service?
    # logging.info("Starting Dashboard Imports")
    # try:
    #   meas_node_ip = socket.gethostbyname(socket.gethostname())
    #   username = "fabric"
    #   #os.chdir('../../../instrumentize/elk/credentials')
    #   f = open("/home/mfuser/mf_git/instrumentize/elk/credentials/nginx_passwd", "r")
      
    #   password = f.readline()
    #   f.close()
    #   password = password.rstrip()
    #   #os.chdir('../dashboards')
    #   #for file in os.listdir(os.getcwd()):
    #   for file in os.listdir("/home/mfuser/mf_git/instrumentize/dashboards"):
    #     if file.endswith('.ndjson'):
    #       logging.info("Uploading " + file)
    #       api_ip = 'http://' + meas_node_ip + '/api/saved_objects/_import?createNewCopies=true'
    #       headers = {'kbn-xsrf': 'true',}
    #       files = {'file': (file, open(file, 'rb')),}
    #       response = requests.post(api_ip, headers=headers, files=files, auth=(username, password))
    #       ret_val["msg"] += f"Uploaded dashboard {file}. "
    # except Exception as e:
    #     logging.error(f"Error in importing dashboards: {e}")
    #     ret_val["msg"] += f"Error in importing dashboards: {e} "
    


    logging.info("-----End Ceate Script.-----")
    print(json.dumps(ret_val))

if __name__ == "__main__":
    main()
