# Create the service overview. 
# Nothing to do. Just check if functions work for getting info.

import os
from os.path import exists
import json
import overview_utilities as ou



def main():
    ret_val = {
        "success": True,
        "msg": None
    }


    data = ou.get_data()


    # Write a default setting for returning jsons.
    default_settings = {}
    
    if "readme_format" in data:
        default_settings["readme_format"] = data["readme_format"] 
    else:
        default_settings["readme_format"] = "combined"
    
    default_settings_filename =  os.path.join(ou.services_dir, "overview", "default_settings.json")
    print(default_settings_filename)
    if not os.path.exists(default_settings_filename):
        with open(default_settings_filename, "w" ) as settings_file:
            settings_file.write( json.dumps(default_settings) )


    # service_list = ou.get_services_list()
    # # Check if the service list works, if so we are good to go.
    # if service_list:
    #     ret_val["success"] = True 
    # else:
    #     ret_val["success"] = False 

    

    print( ou.get_json_string(ret_val) )
    
if __name__ == "__main__":
    main()