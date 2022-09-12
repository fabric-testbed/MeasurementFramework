# Get info about the grafana_manager service. 

import os
from os.path import exists
import json
import grafanaUtilities as gu
import grafanaInterface as gi 



def main():
    ret_val = {
        "success": True,
        "msg": ""
    }

    # Data is stored in relative dir to this script.
    service_dir =  os.path.dirname(__file__)
    infoFilePath = os.path.join( service_dir, "infoFile.txt")
    configFilePath = os.path.join( service_dir, "configFile.txt")

    data = gu.get_data()

 
    default_settings = gu.get_defaults()

    interface = gi.GrafanaManager( host = "localhost",
                    username = "admin",
                    password = default_settings['grafana_admin_password'],
                    infoFilePath = infoFilePath,
                    infoFileDelimiter = ",",
                    key = None
                  ) 
                      
    if "get" in data:
            
        if "all_users_info" in data["get"]:
            result = interface.getAllUserInfo()
            ret_val['all_users_info'] = result['data']

        if "admin_password" in data["get"]:
            defaults = gu.get_defaults()
            ret_val["grafana_admin_password"] = defaults["grafana_admin_password"]
        
        # if "ht_access" in data["get"]:
        #     defaults = gu.get_defaults()
        #     ret_val["fabric_prometheus_ht_user"] = defaults["fabric_prometheus_ht_user"]
        #     ret_val["fabric_prometheus_ht_password"] = defaults["fabric_prometheus_ht_password"]

        if "ht_user" in data["get"]:
            ret_val["ht_user"] = defaults["fabric_prometheus_ht_user"]

        if "ht_password" in data["get"]:
            ret_val["ht_password"] = defaults["fabric_prometheus_ht_password"]

    elif "render" in data:
        if "url_path" in data["render"]:
            ret_val["render"] = interface.render(data["render"]["url_path"], gu.rendered_dir )

    else:
        ret_val["help"] = 'Valid request data values include "get": ["all_users_info", "admin_password", "ht_user", "ht_password"], "render":<render_url_path> '


    # #def test_FindUser(self):
    # result = interface.findUser('userLogin')
    # print(result)
    # #self.assertEqual(True, result['success'], result['msg'])


    print( gu.get_json_string(ret_val) )
    
if __name__ == "__main__":
    main()