# Update the grafana_manager service. 

import os
from os.path import exists
import json
import grafanaUtilities as gu
import grafanaInterface as gi 

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


    data = gu.get_data()
 
    default_settings = gu.get_defaults()

    interface = gi.GrafanaManager( host = "localhost",
                    username = "admin",
                    password = default_settings['grafana_admin_password'],
                    infoFilePath = gu.infoFilePath,
                    infoFileDelimiter = ",",
                    key = None
                  ) 


    if "commands" in data:
        # Ensure certain commands are run in the needed order

        for cmd in data["commands"]:
            if "cmd" in cmd and cmd["cmd"] == "upload_dashboards":
                # move files from files dir to dashboards dir
                if "dashboard_filenames" in cmd:

                    for dashboard_filename in get_file_basenames( cmd["dashboard_filenames"] ):
                        src_dashboard_filename = os.path.join(gu.files_dir, dashboard_filename )
                        dst_dashboard_filename = os.path.join(gu.dashboards_dir, dashboard_filename )

                        copy_file(src_dashboard_filename, dst_dashboard_filename)
                        ret_val['msg'] += f'Have dashboard file {dashboard_filename}.\n'

        for cmd in data["commands"]:
            if "cmd" in cmd and cmd["cmd"] == "add_dashboards":

                # create (add) the dashboard to grafana
                if "dashboard_filenames" in cmd:
                    for dashboard_filename in get_file_basenames(  cmd["dashboard_filenames"] ):
                        result = interface.createDashboard(os.path.join(gu.dashboards_dir, dashboard_filename ))
                        ret_val["msg"] += f'Added dashboard {dashboard_filename}\n' 
                        ret_val[dashboard_filename] = result

                            
    # if "cmd" in data:
            
    #     if "upload_dashboards" in data["cmd"]:
    #         # move files from files dir to dashboards dir
    #         if "dashboard_filenames" in data["cmd"]["upload_dashboards"]:

    #             for dashboard_filename in get_file_basenames( data["cmd"]["upload_dashboards"] ):
    #                 src_dashboard_filename = os.path.join(gu.files_dir, dashboard_filename )
    #                 dst_dashboard_filename = os.path.join(gu.dashboards_dir, dashboard_filename )

    #                 copy_file(src_dashboard_filename, dst_dashboard_filename)
    #                 ret_val['msg'] += f'Have dashboard file {dashboard_filename}.\n'

    #     if "add_dashboard" in data["cmd"]:
    #         # create (add) the dashboard to grafana
    #         if "dashboard_filenames" in data["cmd"]["add_dashboards"]:
    #             for dashboard_filename in get_file_basenames( data["cmd"]["add_dashboards"] ):
    #                 result = interface.createDashboard(os.path.join(gu.dashboards_dir, dashboard_filename ))
    #                 ret_val["msg"] += f'Added dashboard {dashboard_filename}\n'

        # if data["cmd"] == "new_user":
        #     pass 
            
        #     #result = interface.createNewUser('user', 'user@user.com', 'userLogin', 'userPassword')
        #     result = interface.createNewUser('user', 'user@user.com', 'userLogin', 'userPassword')
        #     # print(result)
        
        # #def test_StoreUserInfo(self):
        # result = interface.storeUserInfo('testingUser', 'testingUserPassword')
        # print(result)
        # #self.assertEqual(True, result['success'], result['msg'])

        # elif data["cmd"] = "get_user_info":
        #     result = interface.getAllUserInfo()
        #     ret_val['msg'] += result['msg']
        #     # print(result)
        
    # #def test_FindUser(self):
    # result = interface.findUser('userLogin')
    # print(result)
    # #self.assertEqual(True, result['success'], result['msg'])

    # #def test_GetAllUsers(self):
    # result = interface.getAllUsers()
    # print(result)
    # #self.assertEqual(True, result['success'], result['msg'])

    # #def test_CreateAdminToken(self):
    # result = interface.createAdminToken()
    # #print(result)
    # ret_val['msg'] += result['msg']
    # #self.assertEqual(True, result['success'], result['msg'])



    # # Create datasource
    # result = interface.createDatasource(os.path.join(service_dir, 'Datasources/localPrometheus.json'))
    # ret_val['msg'] += result["msg"]

    #def test_CreateDashboard(self):
    ##result = interface.createDashboard(os.path.join(service_dir, 'Dashboards/networkDashboard.json' ))
    ##ret_val['msg'] += result['msg']
    #print(result)
    #self.assertEqual(True, result['success'], result['msg'])

    # #def test_DeleteDashboard(self):
    # result = interface.deleteDashboard('dHEquNzGz')
    # print(result)
    # #self.assertEqual(True, result['success'], result['msg'])

    # #def test_GetHomeDashboard(self):
    # result = interface.getHomeDashboard()
    # print(result)
    # #self.assertEqual(True, result['success'], result['msg'])


    # # #def test_UploadDashboards(self):
    # result = interface.uploadDashboards(os.path.join(service_dir, 'Dashboards' ))
    # ret_val['msg'] += result['msg']
    # # result = interface.uploadDashboards('Dashboards')
    # # print(result)
    # # #self.assertEqual(True, result['success'], result['msg'])


        else:
            # Command not recognized
            ret_val['msg'] += f"Unrecognized command '{data['cmd']} given."    

    print( gu.get_json_string(ret_val) )
    
if __name__ == "__main__":
    main()