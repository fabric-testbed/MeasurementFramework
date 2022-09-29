######
# Generate master owl.conf and links.json files for meas_node
# This script should run before start.py
#######

import argparse
from configparser import ConfigParser
import json
from pathlib import Path

def generate_owl_config(port=5005, links_file="/owl_config/links.json", send_intvl = 1.0, 
                        capture_mode = 'save', pcap_intvl = 30, output_dir='/owl_output'):
    config = ConfigParser()
    config.optionxform = str

    config['GENERAL'] = {}
    config['GENERAL']['UdpPort'] = str(port)
    config['GENERAL']['LinksFile'] = links_file
    
    config['sender'] = {}
    config['sender']['SendInterval'] = str(send_intvl)

    config['receiver'] = {}
    config['receiver']['CaptureMode'] = capture_mode
    config['receiver']['PcapInterval'] = str(pcap_intvl)
    config['receiver']['OutputDir'] = output_dir

    with open ('/home/mfuser/services/owl/config/owl.conf', 'w') as configfile:
        config.write(configfile)


def generate_links(links):
    '''
    Generate /home/mfuser/services/owl/config/links.json file
    Args:
        links: JSON formatted string
    '''

    # TODO: Not exactly needed 
    jsonified_links = json.dumps(links, indent=4)

    with open ('/home/mfuser/services/owl/config/links.json', 'w') as json_out:
        json_out.write(jsonified_links)
        #json_out.write(links)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--port', type=int, default=5005)
    parser.add_argument('--links-file', type=str, default='/owl_config/links.json')
    parser.add_argument('--send-int', type=float, default = 1.0)
    parser.add_argument('--cap-mode', type=str, default = 'save', help='"save" or "live"')
    parser.add_argument('--pcap-int', type=int, default = 30)
    parser.add_argument('--output-dir', type=str, default = '/owl_output')
    parser.add_argument('--links', type=json.loads, default = '{"links": [{"src": "10.0.0.1","dst": "10.0.0.2"}]}',
                        help='{"links": [{"src": "10.0.0.1","dst": "10.0.0.2"}]}')

    args = parser.parse_args()

    Path("/home/mfuser/services/owl/config").mkdir(parents=True, exist_ok=True)

    generate_owl_config(port=args.port, links_file=args.links_file, send_intvl=args.send_int, 
                        capture_mode=args.cap_mode, pcap_intvl=args.pcap_int, output_dir=args.output_dir)

    generate_links(args.links)
