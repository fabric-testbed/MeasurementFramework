# Create the service overview. 
# Nothing to do. Just check if functions work for getting info.

import os
from os.path import exists
import json
import grafanaUtilities as gu
import grafanaInterface as gi 



def main():
    ret_val = {
        "success": True,
        "msg": None
    }


    data = gu.get_data()

    # To create the grafana service Prometheus must already be setup
    if not os.path.exists(gu.prometheus_default_install_vars_file):
        ret_val["msg"] = "Prometheus services, which include Grafana, has not been set up. Unable to manage Grafana dashboards."
 
    default_settings = gu.get_defaults()

    interface = gi.GrafanaManager( host = "localhost",
                    username = "admin",
                    password = default_settings['grafana_admin_password'],
                    infoFilePath = "infofile",
                    infoFileDelimiter = ",",
                    key = None
                  ) 
    
    interface.createConfigFile('configFile.txt', '-')



    #def test_CreateConfigFile(self):
    result = interface.createConfigFile('configFile.txt', '-')
    #assertEqual(True, result['success'], result['msg'])
    print(result)

    #def test_ParseConfigFile(self):
    result = interface.parseConfigFile('configFile.txt', '-')
    print(result)
    #self.assertEqual(True, result['success'], result['msg'])

    #def test_CreateNewUser(self):
    result = interface.createNewUser('user', 'user@user.com', 'userLogin', 'userPassword')
    print(result)
    #self.assertEqual(True, result['success'], result['msg'])

    #def test_StoreUserInfo(self):
    result = interface.storeUserInfo('testingUser', 'testingUserPassword')
    print(result)
    #self.assertEqual(True, result['success'], result['msg'])

    #def test_GetAllUserInfo(self):
    result = interface.getAllUserInfo()
    print(result)
    #self.assertEqual(True, result['success'], result['msg'])

    #def test_FindUser(self):
    result = interface.findUser('userLogin')
    print(result)
    #self.assertEqual(True, result['success'], result['msg'])

    #def test_GetAllUsers(self):
    result = interface.getAllUsers()
    print(result)
    #self.assertEqual(True, result['success'], result['msg'])

    #def test_CreateAdminToken(self):
    result = interface.createAdminToken()
    print(result)
    #self.assertEqual(True, result['success'], result['msg'])

    #def test_CreateDashboard(self):
    result = interface.createDashboard('Dashboards/networkDashboard.json')
    print(result)
    #self.assertEqual(True, result['success'], result['msg'])

    #def test_DeleteDashboard(self):
    result = interface.deleteDashboard('dHEquNzGz')
    print(result)
    #self.assertEqual(True, result['success'], result['msg'])

    #def test_GetHomeDashboard(self):
    result = interface.getHomeDashboard()
    print(result)
    #self.assertEqual(True, result['success'], result['msg'])


    #def test_UploadDashboards(self):
    result = interface.uploadDashboards('Dashboards')
    print(result)
    #self.assertEqual(True, result['success'], result['msg'])


    

    print( gu.get_json_string(ret_val) )
    
if __name__ == "__main__":
    main()