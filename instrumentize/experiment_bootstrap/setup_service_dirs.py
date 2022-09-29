# This script sets up the needed service directories for mflib to use for controlling MeasurementFramework services.
# Each service has a custom python script named after the service. <service_name>.py These custom scripts are in experiment_bootstrap/service_scripts/.
# This script will setup the needed directory for each service, then call the custom script passing the created directory path as an argument.
# See the example.py script for a simple example.


import subprocess
import sys 


import glob
import os
from pathlib import Path

import importlib.util

import logging 

logfile = os.path.join(os.path.expanduser("~"), "services", "setup_service.log")
logging.basicConfig(filename=logfile, format='%(asctime)s %(name)-8s %(levelname)-8s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level="INFO")


def make_base_service_dir():
    # Create the base service directory.
    logging.info("Creating base services dir.")
    base_service_dir = os.path.join(os.path.expanduser("~"), "services") 
    try:
        os.makedirs( base_service_dir)
        logging.info(f"Services dir created as { base_service_dir }.")
    except OSError as oserr:
        logging.info(f"Directory, {base_service_dir}, already exist.")
    return base_service_dir

def make_service_dir(base_service_dir, service_name):
    # Create a service directory for the given service_name/
    logging.info(f"Creating directories for {service_name}.")
    service_dir = os.path.join(base_service_dir, service_name) 
    try:
        os.makedirs( service_dir)
        logging.info(f"Services dir created as { service_dir }.")
    except OSError as oserr:
        logging.info(f"Directory, {service_dir}, already exist.")


    # make auxillary dirs
    # Log
    log_dir = os.path.join(service_dir, "log") 
    try:
        os.makedirs( log_dir)
        logging.info(f"Log dir created as { log_dir }.")
    except OSError as oserr:
        logging.info(f"Directory, {log_dir}, already exist.")

    # Files
    files_dir = os.path.join(service_dir, "files") 
    try:
        os.makedirs( files_dir)
        logging.info(f"Files dir created as { files_dir }.")
    except OSError as oserr:
        logging.info(f"Directory, {files_dir}, already exist.")

    # Data
    data_dir = os.path.join(service_dir, "data") 
    try:
        os.makedirs( data_dir)
        logging.info(f"Data dir created as { data_dir }.")
    except OSError as oserr:
        logging.info(f"Directory, {data_dir}, already exist.")


    return service_dir



def run_service_scripts(base_service_dir):
    # Run service scripts & create service directory for each.
     
    glob_txt = os.path.join(os.path.expanduser("~"), "mf_git", "instrumentize", "experiment_bootstrap", "service_scripts", "*.py")
    for file in glob.glob(glob_txt):
        try:
            service_dir = make_service_dir(base_service_dir, Path(file).stem)
            service = importlib.util.spec_from_file_location("")
            logging.info(f"Running service setup script {file}.")
            r = subprocess.run([sys.executable, file, "--service_dir", service_dir ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(r)
        except Exception as e:
            print(str(e))
            logging.error("run_service_scripts has failed.")
            logging.error(str(e))


if __name__ == "__main__":
    base_service_dir = make_base_service_dir()
    run_service_scripts(base_service_dir)
