# Overview service provides an overview of the installed services on the measurenode.
# Is intended to be more of a testing/debugging tool than a user service. 

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
    src_dir = "../../../user_services/overview/service_commands"
    print(f"Copying files and subfolders from {src_dir} to {args.service_dir}")
    copy_files(src_dir, args.service_dir)