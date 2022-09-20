
import os
from pathlib import Path
import json

services_dir = os.path.join(os.path.expanduser('~') ,"services")

this_service_dir = os.path.join(services_dir, "grafana_manager") 

rendered_dir = os.path.join(this_service_dir, "rendered")

data_filename = os.path.join(this_service_dir, "data", "data.json" )

files_dir = os.path.join(this_service_dir, "files")
dashboards_dir = os.path.join(this_service_dir, "Dashboards")

prometheus_default_install_vars_file = os.path.join(services_dir, "prometheus", "extra_files", "install_vars.json")

infoFilePath = os.path.join( this_service_dir, "infoFile.txt")
configFilePath = os.path.join( this_service_dir, "configFile.txt")

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

def get_defaults():
    with open(prometheus_default_install_vars_file, "r") as f:
        defaults = json.load(f)
    return defaults