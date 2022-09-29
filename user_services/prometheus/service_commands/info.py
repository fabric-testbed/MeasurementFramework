# Get prometheus info.
  
import os
import json

import prom_utilites as pu

def main():

    ret_val = {}

    data = pu.get_data()



    if "get" in data:
        install_vars = pu.get_install_vars()

        if "grafana_admin_password" in data["get"]:
            ret_val["grafana_admin_password"] = install_vars["grafana_admin_password"]

        if "ht_user" in data["get"]:
            ret_val["ht_user"] = install_vars["fabric_prometheus_ht_user"]

        if "ht_password" in data["get"]:
            ret_val["ht_password"] = install_vars["fabric_prometheus_ht_password"]


    else:
        ret_val["help"] = 'Valid request data values include "get": ["grafana_admin_password", "ht_user", "ht_password"]. '


    print( pu.get_json_string(ret_val) )


if __name__ == "__main__":
    main()