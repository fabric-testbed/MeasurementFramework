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

    # Upload each dashboard to Grafana
    if "load_defaults" in data and data["load_defaults"]:
        # Upload defaults
        result = interface.uploadDashboards(DEFAULT_DASHBOARD_DIRECTORY)
    elif "load_user" in data and data["load_user"]:
        # Upload users
        # for now just grab files in files dir, should add abiltiy to copy incoming files to the user directory
        # for that we will need to know the file names so we can move them to the user dashboard directory
        result = interface.uploadDashboards(USER_DASHBOARD_DIRECTORY)
    
    # for now just permit one action so the returned result is simple
    # add in more options for createing users etc...

    #return result
    print( json.dumps(result) )
    
if __name__ == "__main__":
    main()