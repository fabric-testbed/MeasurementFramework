# Update the grafana_manager service. 

import os
from os.path import exists
import json
import grafanaUtilities as gu
import grafanaInterface as gi 
import logging 


def copy_files(src_dir, dst_dir):
    os.system(f"cp -r {src_dir}/* {dst_dir}")

def copy_file(src_file, dst_file):
    os.system(f"cp -r {src_file} {dst_file}")

def get_file_basenames(files):
    basenames = []
    for f in files:
        basenames.append(os.path.basename(f))
    return basenames

def main():
    ret_val = {
        "success": True,
        "msg": ""
    }

    logFilePath = os.path.join(gu.this_service_dir, "log", "update.log")
    logging.basicConfig(filename=logFilePath, format='%(asctime)s %(name)-8s %(levelname)-8s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level="INFO")
    logging.info("-----Start Update Script.-----")


    data = gu.get_data()
 
    default_settings = gu.get_defaults()

    interface = gi.GrafanaManager( host = "localhost",
                    username = "admin",
                    password = default_settings['grafana_admin_password'],
                    infoFilePath = gu.infoFilePath,
                    infoFileDelimiter = ",",
                    key = None
                  ) 

    interface.parseConfigFile( gu.configFilePath,"-")

    command_found = False
    if "commands" in data:
        # Ensure certain commands are run in the needed order


        for cmd in data["commands"]:
            if "cmd" in cmd and cmd["cmd"] == "upload_dashboards":
                command_found = True
                logging.info("Uploading Dashboards")
                # move files from files dir to dashboards dir
                if "dashboard_filenames" in cmd:
                    
                    for dashboard_filename in get_file_basenames( cmd["dashboard_filenames"] ):
                        logging.info(f"Dashboard {dashboard_filename}")
                        src_dashboard_filename = os.path.join(gu.files_dir, dashboard_filename )
                        dst_dashboard_filename = os.path.join(gu.dashboards_dir, dashboard_filename )
                        logging.info(f"Copy {src_dashboard_filename} to {dst_dashboard_filename}")
                        copy_file(src_dashboard_filename, dst_dashboard_filename)
                        ret_val['msg'] += f'Have dashboard file {dashboard_filename}.\n'

        for cmd in data["commands"]:
            if "cmd" in cmd and cmd["cmd"] == "add_dashboards":
                command_found = True
                logging.info("Adding dashboard")
                # create (add) the dashboard to grafana
                if "dashboard_filenames" in cmd:
                    for dashboard_filename in get_file_basenames(  cmd["dashboard_filenames"] ):
                        logging.info(f"Adding {dashboard_filename} to grafana." )
                        logging.info(os.path.join(gu.dashboards_dir, dashboard_filename ))
                        result = interface.createDashboard(os.path.join(gu.dashboards_dir, dashboard_filename ))
                        logging.info(result)
                        ret_val["msg"] += f'Added dashboard {dashboard_filename}\n'
                        ret_val[dashboard_filename]["success"] = result["success"]
                        ret_val[dashboard_filename]["msg"] = result["msg"]
                        #result["data"]  is not dependable json serializable
                        

    if not command_found:
        # Command not recognized
        ret_val['msg'] += f"No recognized command found."    

    print( gu.get_json_string(ret_val) )
    
if __name__ == "__main__":
    main()