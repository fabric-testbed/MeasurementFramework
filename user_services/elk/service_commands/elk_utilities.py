
import os
from pathlib import Path
import json


services_dir = os.path.join(os.path.expanduser('~') ,"services")
service_dir = os.path.join(services_dir, "elk")
files_dir = os.path.join(service_dir, "files")
dashboards_dir = os.path.join(service_dir, "dashboards")
data_filename = os.path.join(service_dir, "data", "data.json" )
log_dir = os.path.join(service_dir, "log")

installed_dashboard_file = os.path.join(eu.service_dir, "installed_dashboards")

# services_dir = os.path.join(os.path.expanduser('~') ,"services")
# files_dir = os.path.join(services_dir, "files")
# dashboards_dir = os.path.join(services_dir, "dashboards")
# data_filename = os.path.join(services_dir, "elk", "data", "data.json" )

#file should be moved to teh services_dir?
nginx_password_filename = os.path.join('/','home', 'mfuser', 'mf_git', 'instrumentize', 'elk', 'credentials', 'nginx_passwd')

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

def read_installed_dashboards():
    try:
        with open(installed_dashboard_file) as data_file:
            data = json.load(data_file)
    except Exception as e:
        data = []
    return data

def write_installed_dashboards(installed_dashboards):
    try:
        with open(installed_dashboard_file, "w+") as f:
            json.dump(installed_dashboards,f)
    except Exception as e:
        error_msg = "Failed to write installed dashboards"
        print(e)

