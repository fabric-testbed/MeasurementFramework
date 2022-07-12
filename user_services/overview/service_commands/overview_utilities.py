
import os
from pathlib import Path
import json

services_dir = os.path.join(os.path.expanduser('~') ,"services")

data_filename = os.path.join(services_dir, "overview", "data", "data.json" )

def get_services_list():
    # Read the services directories and parse service names
    service_list = []

    for item in os.listdir(services_dir):
        if os.path.isdir(os.path.join(services_dir, item)):
            service_list.append(item)

    return service_list

def get_services_readme():
    # Concats all the service readmes in to one readme string to return.
    overview_readme = "# Service README Collection\n This README is a collection of all the READMEs for all the available services.\n\n"
    service_list = get_services_list()
    for service in service_list:
        readme_filename = os.path.join(services_dir, service, "README.md")
        overview_readme += f"\n------------------------------\n# {service} README.md\n------------------------------\n" 
        if os.path.exists(readme_filename):
            with open(readme_filename) as readme_file:
                readme_str = readme_file.read()
            overview_readme += readme_str 
        else: 
            overview_readme += f"{service} README not found.\n"

    return overview_readme 



def get_service_readme_list():
    services = get_services_list()
    ret_val = []   
    for service in services:
        readme = get_service_readme(service)
        ret_val.append( { "name":service, "readme":readme } )
    return ret_val  

def get_service_readme(service):
    readme_filename = os.path.join(services_dir, service, "README.md")
    if os.path.exists(readme_filename):
        with open(readme_filename) as readme_file:
            readme_str = readme_file.read()
    else:
        return None 
    return readme_str


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

