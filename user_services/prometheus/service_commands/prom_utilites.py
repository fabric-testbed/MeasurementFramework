import os
from pathlib import Path
import json
from datetime import datetime
import os
import subprocess
import glob

import string
import random


service_dir = os.path.join(os.path.expanduser('~') ,"services", "prometheus")

data_filename = os.path.join(service_dir, "data.json" )
extra_files_dir = os.path.join(service_dir, "extra_files")
ansible_out_dir = os.path.join(service_dir, "ansible_out")

def get_data():
    # Get incoming data which will be in the data.json file.
    try:
        with open(data_filename) as data_file:
            data = json.load(data_file)
    except Exception as e:
        data = {}
    return data

def get_json_string(data):
    # Format data as a json string.
    try:
        json_str = json.dumps(data)
    except Exception as e:
        error_msg = {}
        error_msg['json_error'] = "Data was unable to be converted to a JSON string"
        error_msg['json_exception'] = type(e).__name__
        json_str = json.dumps(error_msg)
    return json_str



def save_ansible_output(stdout, stderr):
    now = datetime.now()
    ansible_output_file = os.path.join( ansible_out_dir, "experiment_install_prometheus_out_{0}".format( now.strftime("%Y_%m_%d_%H_%M_%S") ) )

    decoded_out = stdout.decode("utf-8")
    play_recap = decoded_out[decoded_out.find("PLAY RECAP"):]
    decoded_err = stderr.decode("utf-8")

    with open(ansible_output_file, "w") as aof:
        aof.write("STDOUT:\n")
        aof.write(decoded_out)
        aof.write("\nSTDERR:\n")
        aof.write(decoded_err)



      # Save the ansible recap for easy access
    ansible_recap_file = os.path.join( service_dir, "ansible_out", "experiment_install_prometheus_recap_{0}".format( now.strftime("%b_%d_%Y_%H_%M_%S") ) )

    with open(ansible_recap_file, "w") as arf:
        arf.write(play_recap)

def create_grafana_admin_password():
    """
    If the password file does not already exist, it is created and True is returned.
    Otherwise returns False
    """
    password_file = os.path.join(extra_files_dir, "grafana_admin_password" )
    if not os.path.exists(password_file):
        # Create new password and save to file
        letters = string.ascii_letters
        randpass =  "".join(random.choice(letters) for i in range(10))
        with open(password_file,'w') as pout:
            pout.write(randpass)
        return True
    return False


def get_grafana_admin_password():
    password_file = os.path.join(extra_files_dir, "grafana_admin_password" )
    if os.path.exists(password_file):
        with open(password_file, 'r') as pin:
            password = pin.read()
    else:
        return None
    return password



def get_last_ansible_out_str():
    ret_val = ""
    glob_str = os.path.join(ansible_out_dir, "experiment_install_prometheus_out_*")
    files = glob.glob(glob_str)
    if files:
        files = sorted(files, reverse=True)
        with open(files[0], 'r') as f:
            ret_val = f.read()
    return ret_val