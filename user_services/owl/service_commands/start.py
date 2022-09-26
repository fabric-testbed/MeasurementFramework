import argparse
from configparser import ConfigParser
import json


def generate_owl_config(port, links_file, send_intvl, capture_mode, pcap_intvl, output_dir ):
    config = ConfigParser()
    config.optionxform = str
    config['GENERAL'] = {}
    config['GENERAL']['UdpPort'] = port
    config['GENERAL']['LinksFile'] = links_file
    
    config['sender'] = {}
    config['sender']['SendInterval'] = send_intvl

    config['receiver'] = {}
    config['receiver']['CaptureMode'] = capture_mode
    config['receiver']['PcapInterval'] = pcap_intvl
    config['receiver']['OutputDir'] = output_dir

    with open ('/home/mfuser/services/owl/config/owl.conf', 'w') as configfile:
        config.write(configfile)


def generate_links(links):
    '''
    Generate /home/mfuser/services/owl/config/links.json file
    Args:
        links([(src, dst),]:
    '''

    l = []
    for link in links:
        d={}
        d['src'] = link[0]
        d['dst'] = link[1]
        l.append(d)

    links_dict = {}
    links_dict["links"] = l

    jsonified_links = json.dumps(links_dict, indent=4)

    with open ('/home/mfuser/services/owl/config/links.json', 'w') as json_out:
        json_out.write(jsonified_links)


def start_owl(args):
    pass


if __name__ == "__main__":
    pass
