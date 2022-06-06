import os
from os.path import exists

from GrafanaManager.grafanaInterface import GrafanaManager

# Grafana Host
DEFAULT_GRAFANA_HOST = 'localhost'

# File location for Grafana username and password
DEFAULT_USER_INFO_LOCATION = ''
# Default configuration file path
DEFAULT_CONFIG_FILE_PATH = '/home/mfuser/services/grafana_dashboard/grafanaConfig.txt'
# Default configuration file delimiter
DEFAULT_CONFIG_FILE_DELIMITER = '-'

# Remote repository containing Grafana Interface
GITHUB_REPO = 'https://github.com/glitchkyle/GrafanaManager.git'
# Remote repository destination directory
GITHUB_REPO_DESTINATION = '/home/mfuser/services/grafana_dashboard/GrafanaManager'

def getAdminInformation(infoFile):
    """
    Reads in Grafana Username and Password information

    :param infoFile: Path to info file containing Grafana Admin information
    :type infoFile: str
    :return: Grafana admin username
    :rtype: str
    :return: Grafana admin password
    :rtype: str
    """
    username = 'admin'
    password = 'admin'
    
    return username, password

def main():
    response = {
        "success": False,
        "msg": None
    }

    grafanaAdminUsername, grafanaAdminPassword = getAdminInformation(DEFAULT_USER_INFO_LOCATION)

    # # Clone GrafanaManager Repository if it does not exist
    # if not exists(GITHUB_REPO_DESTINATION):
    #     os.system(f'sudo git clone {GITHUB_REPO} {GITHUB_REPO_DESTINATION}')

    # from GrafanaManager.grafanaInterface import GrafanaManager

    # if not exists(GITHUB_REPO_DESTINATION):
    #    response['msg'] = "Failed to clone Grafana Manager repository."
    #    return response

    # Create new Grafana Manager object
    interface = GrafanaManager(DEFAULT_GRAFANA_HOST, grafanaAdminUsername, grafanaAdminPassword)

    # Create new API token
    tokenCreationStatus = interface.createAdminToken()

    # Check if new API token creation was successful
    if tokenCreationStatus['success'] == True:

        # Create Config File
        configFileCreationStatus = interface.createConfigFile(DEFAULT_CONFIG_FILE_PATH, DEFAULT_CONFIG_FILE_DELIMITER)

        if configFileCreationStatus['success'] == True:
            response['success'] =  True
            response['msg'] = configFileCreationStatus['msg']
        else:
            response['msg'] = "Failed to create configuration file."

    else:
        response['msg'] = tokenCreationStatus['msg']
        response['data'] = tokenCreationStatus['data']

    #return response
    print( json.dumps(response) )

if __name__ == "__main__":
    main()