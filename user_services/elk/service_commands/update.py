from gettext import install
import os
import json
import datetime
import subprocess
import time

import elk_utilities as eu
import custom_dashboards

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

    logFilePath = os.path.join(eu.log_dir, "update.log")
    logging.basicConfig(filename=logFilePath, format='%(asctime)s %(name)-8s %(levelname)-8s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level="INFO")
    logging.info("-----Start Update Script.-----")


    ret_val = { "success":True, "msg":"" }
    data = eu.get_data()

#############
# testing dashboard single loading

    command_found = False
    elastic_dump_installed = False
    if "commands" in data:
        # Ensure certain commands are run in the needed order

        for cmd in data["commands"]:
            if "cmd" in cmd and cmd["cmd"] == "export_index":
                if not elastic_dump_installed:
                    # TODO: Automate this, make flag work correctly.
                    #os.system('sudo apt-get install npm -y')
                    #os.system('sudo npm install elasticdump -g')

                    elastic_dump_installed = True
                if "indices" in cmd and cmd["indices"]:
                    # Confirm dependencies are installed
                    # TODO: Actually check for this
                    os.system('echo "Confirming npm and elasticdump are installed:"')
                    os.system('echo "npm version:"')
                    os.system('npm --version')
                    os.system('echo "elasticdump version:"')
                    os.system('elasticdump --version')
                    os.system("echo")

                    # Exporting all indices
                    os.system('echo Data export started. Files will be placed in ' + eu.files_dir + '/indices')
                    os.system("echo ------------------------------------------------------------------------------------")
                    os.system("echo")

                    # Changes datetime format to year-month-day_hour:minute:second
                    time_stamp = str(datetime.datetime.now()).split(".")[0].replace(" ", "_")
                    total, successful = 0, 0
                    for index in cmd["indices"]:
                        total += 1
                        file_name = index + "_exported_" + time_stamp + ".json"
                        output_dir = eu.files_dir + '/indices/'
                        cmd = ['sudo', 'elasticdump', '--input=http://localhost:9200/' + index, '--output=' +
                               output_dir + file_name + '.download', '--type=data']

                        os.system("echo -n Exporting " + index)
                        # print('Exporting ' + index + ' as ' + file_name)
                        export_process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                                          stderr=subprocess.PIPE, text=True)
                        while export_process.poll() is None:
                            os.system("echo -n .")
                            time.sleep(1)
                        os.system("echo")
                        if export_process.poll() == 0:
                            os.system("echo Exported successfully as " + file_name)
                            os.system("sudo mv " + output_dir + file_name + ".download " + output_dir + file_name)
                            successful += 1
                        else:
                            os.system("echo Export failed. Dumping output for troubleshooting:")
                            os.system("echo " + str(export_process.communicate()))
                        os.system("echo \n")

                    os.system("echo ------------------------------------------------------------------------------------")
                    # Returning results
                    ret_val['export_results'] = str(successful) + "/" + str(total) + " indices exported successfully."
                    ret_val['export_location'] = eu.files_dir + "/indices"

                else:
                    ret_val['success'] = False
                    ret_val['export_index'] = "Failed to export any indices: Missing index names."

        for cmd in data["commands"]:
            if "cmd" in cmd and cmd["cmd"] == "upload_dashboards":
                ret_val['uploaded_dashboards'] = {}
                command_found = True
                logging.info("---upload_dashboards command found---")
                # move files from files dir to dashboards dir
                if "dashboard_filenames" in cmd:
                    logging.info("found dashboard_filenames")
                    for dashboard_filename in get_file_basenames( cmd["dashboard_filenames"] ):
                        logging.info(f"  Dashboard {dashboard_filename}")
                        src_dashboard_filename = os.path.join(eu.files_dir, dashboard_filename )
                        dst_dashboard_filename = os.path.join(eu.dashboards_dir, dashboard_filename )
                        logging.info(f"    Copy {src_dashboard_filename} to {dst_dashboard_filename}")
                        copy_file(src_dashboard_filename, dst_dashboard_filename)
                        
                        ret_val['uploaded_dashboards'][dashboard_filename] = {} 
                        ret_val['uploaded_dashboards'][dashboard_filename]['success'] = True

        for cmd in data["commands"]:
            if "cmd" in cmd and cmd["cmd"] == "add_dashboards":
                command_found = True
                logging.info("---add_dashboard command found---")
                ret_val["added_dashboards"] = {}

                # Check if user wants to force reinstall
                if "force" in cmd:
                    do_force = cmd["force"]
                    logging.info(f"add_dashboards force set to {do_force}")
                else:
                    do_force = False

                # Get list of installed dashboards to prevent double installing.
                installed_dashboards = eu.read_installed_dashboards()
                
                # import the dashboard into kibana
                if "dashboard_filenames" in cmd:
                    logging.info("found dashboard_filenames")
                    for dashboard_filename in get_file_basenames(  cmd["dashboard_filenames"] ):
                        logging.info(f"  Dashboard {dashboard_filename}" )

                        # Only install the dashboard if it has not been installed or if user wants to force reinstall
                        if do_force or dashboard_filename not in installed_dashboards:
                            logging.info( f"  Importing {os.path.join(eu.dashboards_dir, dashboard_filename )} to kibana" )
                            result = custom_dashboards.import_dashboard(dashboard_filename)
                            logging.info(result)
                            #ret_val["msg"] += f'Added dashboard {dashboard_filename}\n'
                            ret_val["added_dashboards"][dashboard_filename] = {}
                            ret_val["added_dashboards"][dashboard_filename]["success"] = result["success"]
                            ret_val["added_dashboards"][dashboard_filename]["msg"] = result["msg"]

                            if dashboard_filename in installed_dashboards:
                                logging.info("Forced reinstall of kibana dashboard.")
                            if result["success"] and dashboard_filename not in installed_dashboards:
                                installed_dashboards.append(dashboard_filename)
                                eu.write_installed_dashboards(installed_dashboards)
                        else:
                            ret_val["added_dashboards"][dashboard_filename] = {}
                            ret_val["added_dashboards"][dashboard_filename]["success"] = False
                            ret_val["added_dashboards"][dashboard_filename]["msg"] = "Already installed."

                        #else: Do nothing dashboard alread exists

                        # Version without force
                        # if dashboard_filename in installed_dashboards:
                        #     logging.info(f"{dashboard_filename} has already been installed so it will not be installed again." )
                        # else:
                        #     logging.info(os.path.join(eu.dashboards_dir, dashboard_filename ))
                        #     result = custom_dashboards.import_dashboard(dashboard_filename)
                        #     logging.info(result)
                        #     ret_val["msg"] += f'Added dashboard {dashboard_filename}\n'
                        #     ret_val[dashboard_filename] = {}
                        #     ret_val[dashboard_filename]["success"] = result["success"]
                        #     ret_val[dashboard_filename]["msg"] = result["msg"]
                        #     if (result["success"]):
                        #         installed_dashboards.append(dashboard_filename)
                        #         eu.write_installed_dashboards(installed_dashboards)
                            

                        #result["data"]  is not dependable json serializable
                        

    # if not command_found:
    #     # Command not recognized
    #     ret_val['msg'] += f"No recognized command found."    




####################






    if "cmd" in data:
        if "upload_custom_dashboards" in data["cmd"]:
            # get list of filenames
            if "dashboard_filenames" in data:
                # Dashboards should have been uploaded to the files directory.
                 #os.chdir(ansible_dir)
                for dfilename in data["dashboard_filenames"]:
                    src_dashboard_filename = os.path.join(eu.files_dir, dfilename)
                    dst_dashboard_filename = os.path.join(eu.dashboards_dir, dfilename)

                    copy_file(src_dashboard_filename, dst_dashboard_filename)
                    ret_val['msg'] += f'Have dashboard "{dfilename}.\n'
                    # do something with dashboard file
                    # maybe move them to the Dashboards dir
        if "add_custom_dashboards" in data["cmd"]:
             ret_val['msg'] += custom_dashboards.import_dashboards()

    print(eu.get_json_string(ret_val))
    #print(json.dumps(ret_val))

if __name__ == "__main__":
    main()