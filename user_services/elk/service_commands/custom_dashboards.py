from datetime import datetime
import os
import json
import subprocess
import logging
import socket
import requests

import elk_utilities as eu


def import_dashboards():
    ret_val = ''
    logging.info("Starting Dashboard Imports")
    try:
      #meas_node_ip = socket.gethostbyname(socket.gethostname())
      meas_node_ip = [(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]
      username = "fabric"
      #os.chdir('../../../instrumentize/elk/credentials')
      with open(eu.nginx_password_filename, "r") as f:
        password = f.readline()
      password = password.rstrip()
      #os.chdir('../dashboards')
      #for file in os.listdir(os.getcwd()):
      
      #for file in os.listdir("/home/mfuser/mf_git/instrumentize/dashboards"):a
      print(eu.files_dir)
      for file in os.listdir(eu.files_dir):
        if file.endswith('.ndjson'):
          logging.info("Uploading " + file)
          api_ip = 'http://' + meas_node_ip + '/api/saved_objects/_import?createNewCopies=true'
          headers = {'kbn-xsrf': 'true',}
          files = {'file': (file, open(os.path.join(eu.files_dir, file), 'rb')),}
          response = requests.post(api_ip, headers=headers, files=files, auth=(username, password))
          ret_val += f"Uploaded dashboard {file}. "
    except Exception as e:
        logging.error(f"Error in importing dashboards: {e}")
        ret_val += f"Error in importing dashboards: {e} "
    return ret_val
