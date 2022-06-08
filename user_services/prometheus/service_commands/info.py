# Get prometheus info.
  
import os
import json

import prom_utilites as pu

def main():

    ret_val = {}

    data = pu.get_data()

    if data:
        if "grafana_admin_password" in data:
            ret_val["grafana_admin_password"] = pu.get_grafana_admin_password()
        if "ansible_output" in data:
            ret_val["ansible_output"]  = pu.get_last_ansible_out_str()
    # Assume it will go well.
    else:
        # get everything for now
        ret_val["grafana_admin_password"] = pu.get_grafana_admin_password()
        ret_val["ansible_output"]  = pu.get_last_ansible_out_str()

    print( pu.get_json_string(ret_val) )


if __name__ == "__main__":
    main()