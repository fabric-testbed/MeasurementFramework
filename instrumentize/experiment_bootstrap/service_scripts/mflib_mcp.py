# mflib_mcp bootstrap
# Copies the service_commands files (create/info/remove + utilities) to the
# service dir set up for this service on the meas node. Mirrors
# meas_node_server.py's pattern exactly -- staging only, no logic here.

import argparse
import os

# This script will be called by the bootstrap process while setting up the
# meas node. The call will include the path for the directory setup for the
# service. Note staging happens for EVERY user_service unconditionally (see
# setup_service_dirs.py) -- that does not mean mflib_mcp gets created on
# every meas node. Only meas_node_self_start()'s generated self-start script
# (mflib/mflib/mfportal.py) actually calls this service's create.py; nothing
# else in mflib does (not instrumentize(), not any other create() dispatch).
# A meas node stood up by hand (e.g. mflib.create("prometheus") from a
# notebook, without going through the portal's automated self-start flow)
# never gets mflib_mcp automatically -- it's staged like every other
# service, but only self-start's explicit call actually runs it.
parser = argparse.ArgumentParser(description='Set up service to directory.')
parser.add_argument('--service_dir', help="Destination directory to copy service files into.")


def copy_files(src_dir, dst_dir):
    os.system(f"cp -r {src_dir}/* {dst_dir}")


if __name__ == "__main__":
    args = parser.parse_args()

    service_name = "mflib_mcp"
    this_script_dir = os.path.dirname(os.path.realpath(__file__))
    src_dir = os.path.join(this_script_dir, "..", "..", "..", "user_services", service_name, "service_commands")
    print(f"Copying files and subfolders from {src_dir} to {args.service_dir}")
    copy_files(src_dir, args.service_dir)
