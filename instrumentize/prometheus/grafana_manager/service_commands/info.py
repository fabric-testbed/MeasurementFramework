# This file only retrives information. It does not affect the service.

import json
from GrafanaManager.grafanaInterface import GrafanaManager

# Default location for uploaded JSON dashboards
#DEFAULT_DASHBOARD_DIRECTORY = '/home/mfuser/services/grafana_dashboard/files'
DEFAULT_DASHBOARD_DIRECTORY = '/home/mfuser/services/grafana_manager/default_dashboards'

USER_DASHBOARD_DIRECTORY = '/home/mfuser/services/grafana_manager/files'   # user_dashboards'
DATA_DIRECTORY = '/home/mfuser/services/grafana_manager'

# Default configuration file name
#DEFAULT_CONFIG_FILE_PATH = '/home/mfuser/services/grafana_dashboard/grafanaConfig.txt'
DEFAULT_CONFIG_FILE_PATH = '/home/mfuser/services/grafana_manager/grafanaConfig.txt'
# Default configuration file delimiter
DEFAULT_CONFIG_FILE_DELIMITER = '-'

def main():
    # Get incoming data which will be in the data.json file.
    try:
        with open("data.json") as data_file:
            data = json.load(data_file)
    except Exception as e:
        data = None 
    

    interface = GrafanaManager()

    # Read from config file
    interface.parseConfigFile(DEFAULT_CONFIG_FILE_PATH, DEFAULT_CONFIG_FILE_DELIMITER)

    # Get info as requested.
    if "?" in data:
        # 
        pass
    elif "?" in data:
        pass
    else: # return everything
        pass
        
    result = {}
    result["success"] = True 
    result["msg"] = "Method Not Yet Implemented."
    print( json.dumps(result) )
    
if __name__ == "__main__":
    main()