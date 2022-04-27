# Example of a minimal setup for MeasurementFramework service setup for Fabric Experiment on meas node.
# Idea is to copy all needed files to the services directory setup on the meas node.

import argparse
import os

# This script will be called by the bootstrap process while setting up the meas node.
# The call will include the path for the directory setup for the service. 
parser = argparse.ArgumentParser(description='Set up service to directory.')
parser.add_argument('--service_dir', help="Destination directory to copy service files into.")

def copy_files(src_dir, dst_dir):
    os.system(f"cp -r {src_dir}/* {dst_dir}")

if __name__ == "__main__":
    args = parser.parse_args()
    
    # src_dir is the path to the folder containing the files for controlling the service from mflib.
    # In this simple case all the files are in one folder. 
    service_name = "example"
    this_script_dir = os.path.dirname(os.path.realpath(__file__))
    src_dir = os.path.join(this_script_dir, "..","..","..", "user_services", service_name, "service_commands")
    copy_files(src_dir, args.service_dir)
    # Note the files do not need to come from a simple local copy as shown here. They could be pulled from anywhere such as a git repo or auto generated.
    