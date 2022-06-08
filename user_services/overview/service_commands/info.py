# Get some basic info about all the services.

import os
import json 

import overview_utilities as ou


def main():
    # Assume it will go well.
    retVal = {
        "success": True,
        "msg": None
    }

    # Check for default settings
    default_settings_filename =  os.path.join(ou.services_dir, "overview", "default_settings.json")
    if os.path.exists(default_settings_filename):
        with open(default_settings_filename, "r" ) as settings_file:
            default_settings = json.load(settings_file)
        readme_format = default_settings["readme_format"]
    else:
        readme_format = "list"

    print(readme_format)
    try:
        retVal["data_recieved"] = ou.get_data()
        retVal["services"] = ou.get_services_list()
        if readme_format == "combined":
            retVal["readmes"] = ou.get_services_readme()
        else:
            retVal["readmes"] = ou.get_service_readme_list()
    except Exception as e:
        retVal["msg"] =  "Failed to form valid JSON - exeption " + type(e).__name__  
        retVal["success"] = False 

    print( ou.get_json_string(retVal) )
    
if __name__ == "__main__":
    main()