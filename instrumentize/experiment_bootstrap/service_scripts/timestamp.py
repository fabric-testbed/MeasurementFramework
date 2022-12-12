# Timestamp bootstrap

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
    service_name = "timestamp"
    this_script_dir = os.path.dirname(os.path.realpath(__file__))

    # For the timestamp service commands
    src_dir = os.path.join(this_script_dir, "..","..","..", "user_services", service_name, "service_commands")
    copy_files(src_dir, args.service_dir)
    

    # Copy timestamp service files
    file_src = os.path.join(this_script_dir, "..","..","..", "user_services", service_name, service_name, "service_files")
    file_dst = os.path.join(args.service_dir, "files")

    os.system(f"cp {file_src} {file_dst}")
    
    # Copy config file
    file_src = os.path.join(this_script_dir, "..","..","..", "user_services", service_name, service_name, "config_files")
    file_dst = os.path.join(args.service_dir, "files")
    
    os.system(f"cp {file_src} {file_dst}")
    
    # Copy Elastic index files
    file_src = os.path.join(this_script_dir, "..","..","..", "user_services", service_name, service_name, "elastic_index_files")
    file_dst = os.path.join(args.service_dir, "files")