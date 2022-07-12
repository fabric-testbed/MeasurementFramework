# Create the grafana_manager service. 
# Prometheus service has to be setup prior to running this script.

import os
from os.path import exists
import json
import grafanaUtilities as gu
import grafanaInterface as gi 

import logging 


def main():
    ret_val = {
        "success": True,
        "msg": ""
    }

    # Data is stored in relative dir to this script.
    service_dir =  os.path.dirname(__file__)
    infoFilePath = os.path.join( service_dir, "infoFile.txt")
    configFilePath = os.path.join( service_dir, "configFile.txt")

    logFilePath = os.path.join( service_dir, "log", "create.log")
    logging.basicConfig(filename=logfilePath, format='%(asctime)s %(name)-8s %(levelname)-8s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level="INFO")
    logging.info("-----Start Ceate Script.-----")

    data = gu.get_data()

    if os.path.exists(configFilePath):
        # Service has already been created, don't run again.
        ret_val['msg'] = "Grafana Manager service has already been created. Use mflib.info('grafana_manager') for more information."
        print( gu.get_json_string(ret_val) )
        logging.info("create.py script is not running again since the config file has aleady been created.")
        return 



    # To create the grafana service Prometheus must already be setup
    if not os.path.exists(gu.prometheus_default_install_vars_file):
        ret_val["msg"] = "Prometheus services, which include Grafana, has not been set up. Unable to manage Grafana dashboards."
 
    default_settings = gu.get_defaults()

    interface = gi.GrafanaManager( host = "localhost",
                    username = "admin",
                    password = default_settings['grafana_admin_password'],
                    infoFilePath = infoFilePath,
                    infoFileDelimiter = ",",
                    key = None
                  ) 
    
    
    # Create the config file.
    result = interface.createConfigFile(configFilePath, '-')
    logging.info(result)
    ret_val['msg'] += result['msg']
    
    # Create the admin token
    result = interface.createAdminToken()
    logging.info(result)
    ret_val['msg'] += result['msg']

    # Create local prometheus datasource
    result = interface.createDatasource(os.path.join(service_dir, 'Datasources/localPrometheus.json'))
    logging.info(result)
    ret_val['msg'] += result["msg"]

    # Upload all the default dashboards. Note could change this to just do certain dashboards later.
    result = interface.uploadDashboards(os.path.join(service_dir, 'Dashboards' ))
    logging.info(result)
    ret_val['msg'] += result['msg']

    logging.info(ret_val)
    print( gu.get_json_string(ret_val) )
    logging.info("-----End Create Script-----")
    
if __name__ == "__main__":
    main()