# Get prometheus info.

import os
import json 

import prom_utilites as pu

def main():
    # Assume it will go well.
    retVal = {
        "success": True,
        "msg": ""
    }

    retVal["grafana_admin_password"] = pu.get_grafana_admin_password()

    print( pu.get_json_string())
    # read some info

    # get the latest recap


    
if __name__ == "__main__":
    main()