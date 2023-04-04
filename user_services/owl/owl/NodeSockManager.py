import json
import argparse
import configparser
import logging
import time
import socket
import subprocess
import sys
import os
from random import randrange
from threading import Timer
from pathlib import Path

# hideous but needed to ues udp_sender from here?

cwd = os.getcwd()
sys.path.insert(0, f'{cwd}/sock_ops')

from sock_ops import udp_sender as sender
from sock_ops import udp_capturer as capturer


class NodeSockManager():
    def __init__(self, config_file='/owl_config/owl.conf'):

        config = configparser.ConfigParser()
        config.read(config_file)

        self.udp_port = int(config['GENERAL']['UdpPort'])
        self.pcap_interval = int(config['receiver']['PcapInterval'])
        self.capture_mode = config['receiver']['CaptureMode']
        self.send_interval = float(config['sender']['SendInterval'])

        self.links = Path('/owl_config/links.json')   
        self.output_dir = Path('/owl_output')
        self.ptp_so_file = Path('sock_ops/time_ops/ptp_time.so')

        logging.basicConfig(filename=f'{self.output_dir}/owl.log',
                        level=logging.DEBUG, 
                        format='%(created)f %(message)s')
        self.logger = logging.getLogger('owl-log')

        self.sender_instances = {}
        self.listen_instance = None

        # Find all the IPV4 addresses on the node
        self.host_ipv4s = self._find_IPs()
        self.logger.info(f"IP addresses on this node: {self.host_ipv4s}")

        # Go ahead and start
        self.start()


    def start(self):
        _listen_ip, _dests = self._read_links()
        self._start_capturer(_listen_ip)
        self._start_sender(_dests)


    def stop(self):
        # Clean up!
        if self.listen_instance:
            self.logger.info("stopping tcpdump")
            self.listen_instance.stop()
            time.sleep(1)
            self.listen_instance = None

        if len(self.sender_instances) > 0:
            for dest_ip, instance in self.sender_instances.items():
                self.logger.info("stopping send to: ", dest_ip)
                instance.stop()
                time.sleep(1)
                self.sender_instances[dest_ip] = None

        sleep(2)

        assert self.listen_instance is None
        assert len(self.sender_instances) == 0



    def _find_IPs(self):
        s = subprocess.check_output(["hostname", "-I"])
        return s.decode('UTF-8').split()


    def _read_links(self):
        '''
        Returns:
            listener(str): either "UP" or "DOWN" (for the host node)
            dests([str,]): destination IPs (for the host node)
        '''
        
        listen_ip = "DOWN" # Default is down
        dests = []

        try:
            f = open(self.links)
            data = json.load(f)
    
            for link in data["links"]:
                if link["src"] in self.host_ipv4s:
                    dests.append(link["dst"])
    
                if link["dst"] in self.host_ipv4s:
                    listen_ip = link["dst"]

        except FileNotFoundError:
            self.logger.error(f"No service request file {self.links} found.")
            # Will return DOWN for receiver status, an empty list for dests

        finally:
            self.logger.info(f"read_links: {listen_ip}, {dests}")

        return listen_ip, dests
    

    def _start_capturer(self, listen_ip):
    
        if listen_ip != "DOWN":
            # If it is a real IP address
            self.listen_instance = capturer.TcpdumpOps(listen_ip, self.udp_port)
            
            if self.capture_mode == "live":
                self.logger.info("Starting live capture")
                self.listen_instance.start_live_capture()
            else:
                self.logger.info(f"Starting capture. Pcap files in {self.output_dir}")
                self.listen_instance.start_capture(self.output_dir, self.pcap_interval)

        else: # DOWN
            pass
    

    def _start_sender(self, dests):
        seq_n = randrange(10000)

        for dest_ip in dests:
            if dest_ip not in self.sender_instances.keys():
                self.logger.info(f"new destination IP  found: {str(dest_ip)} ")
                self.sender_instances[dest_ip] = sender.UDP_sender(
                                                    self.send_interval, 
                                                    dest_ip, 
                                                    self.udp_port, 
                                                    seq_n,
                                                    self.ptp_so_file,
                                                    sys_clock=False)
   


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('conf', type=str, help='path to config file')
    parser.add_argument('--duration', type=int, default=0,  help='number of seconds to run')
    args = parser.parse_args()

    manager = NodeSockManager(args.conf)

    # Stop the program at a certain interval only if the arg is given.
    if args.duration:
        time.sleep(args.duration)
        manager.stop()
        self.logger.info("finished")

