import os
import json

import elk_utilities as eu
import custom_dashboards

def copy_files(src_dir, dst_dir):
    os.system(f"cp -r {src_dir}/* {dst_dir}")

def copy_file(src_file, dst_file):
    os.system(f"cp -r {src_file} {dst_file}")


def main():
    ret_val = { "success":True, "msg":"" }
    data = eu.get_data()
    
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
        if "add_custom_dashboards" in "cmd":
            ret_val['msg'] += custom_dashboards.import_dashboards()



            #
    print(eu.get_json_string(ret_val))
    #print(json.dumps(ret_val))

if __name__ == "__main__":
    main()