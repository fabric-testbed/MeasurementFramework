######
# Get contents of owl.conf and link.json stored on the meas_node
#######

import json
import configparser


def get_owl_files():
    config = configparser.ConfigParser()

    conf_path = '/home/mfuser/services/owl/files/owl.conf'
    links_path = '/home/mfuser/services/owl/files/links.json'

    config.read(conf_path)

    conf_file = {}
    for section in config.sections():
        conf_file[section] = {}
        for option in config.options(section):
            conf_file[section][option] = config.get(section, option)

    links_file = {}
    with open(links_path) as json_file:
        links_file = json.load(json_file)
    
    # Add links info to config file dictionary 
    conf_file.update(links_file)
    
    print(json.dumps(conf_file))


if __name__ == "__main__":
    get_owl_files()
