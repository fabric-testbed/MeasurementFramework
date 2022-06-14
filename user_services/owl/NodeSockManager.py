import json
import argparse
import configparser
import logging
import time
import socket
import subprocess
from sock_ops import udp_sender as sender
from sock_ops import udp_capturer as capturer
from random import randrange
from threading import Timer



class NodeSockManager():
    def __init__(self, config_file):

        config = configparser.ConfigParser()
        config.read(config_file)

        self._timer = None
        self.interval = int(config['GENERAL']['LinkCheckInterval'])
        self.is_running = False

        self.host_ipv4s = self._find_IPs()
        print(self.host_ipv4s)

        self.service_request = config['GENERAL']['ServiceRequestFile']   
        self.udp_port = int(config['GENERAL']['UdpPort'])
        self.pcap_interval = int(config['receiver']['PcapInterval'])
        self.send_interval = float(config['sender']['SendInterval'])
        self.output_dir = config['receiver']['OutputDir']


        logging.basicConfig(filename=f'{self.output_dir}/owl.log',
                        level=logging.DEBUG, 
                        format='%(created)f %(message)s')
        self.logger = logging.getLogger('owl-log')

        self.sender_instances = {}
        self.listen_instance = None

        self.start()


    def _run(self):
        self.is_running = False
        self.start()

        _status, _dests = self._read_service_request()
        self._update_capturer(_status)
        self._update_sender(_dests)


    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True


    def stop(self):
        self._timer.cancel()
        self.is_running = False

        # Clean up!
        if self.listen_instance:
            self.logger.info("stopping tcpdump")
            self.listen_instance.stop()
            time.sleep(1)
            self.listen_instance = None

        if len(self.sender_instances) > 0:
            for ip, instance in self.sender_instances.items():
                self.logger.info("stopping send to: ", ip)
                instance.stop()
                time.sleep(1)
                self.sender_instances[ip] = None

            # Clean up None values
            new_d = {k:v for k, v in self.sender_instances.items() if v is not None}
            self.sender_instances = new_d
    
        assert self.listen_instance is None
        assert len(self.sender_instances) == 0


    def _find_IPs(self):
        s = subprocess.check_output(["hostname", "-I"])
        return s.decode('UTF-8').split()


    def _read_service_request(self):
        
        listener = "DOWN" # Default is down
        dests = []

        try:
            f = open(self.service_request)
            data = json.load(f)
    
            for link in data["links"]:
                if link["src"] in self.host_ipv4s:
                    dests.append(link["dst"])
    
                if link["dst"] in self.host_ipv4s:
                    listener = "UP"

        except FileNotFoundError:
            self.logger.error(f"No service request file {self.service_request} found.")
            # Will return DOWN for receiver status, an empty list for dests

        finally:
            self.logger.info(f"read_service_request: {listener}, {dests}")

        return listener, dests
    

    def _update_capturer(self, status):
    
        if status == "DOWN":
            if self.listen_instance: # there is an instance
                self.logger.info("shutting down tcpdump")
                self.listen_instance.stop()
                time.sleep(1)
                self.listen_instance = None
        else:
            if self.listen_instance is None: # need to start 
                self.logger.info("starting tcpdump")
                self.listen_instance = capturer.TcpdumpOps(
                                            self.udp_port, self.pcap_interval, self.output_dir)
                self.listen_instance.start()
            else:
                # let the current tcpdump instance keep going
                pass
    
    def _update_sender(self, dests):
        seq_n = randrange(10000)
    
        # new dest
        for ip in dests:
            if ip not in self.sender_instances.keys():
                self.logger.info(f"new ip dest found: {str(ip)} ")
                self.sender_instances[ip] = sender.UDP_sender(
                                self.send_interval, ip, self.udp_port, seq_n)
    
        # dest to be removed
        for ip in self.sender_instances.keys():
            if ip not in dests:
                self.logger.info(f"dest ip to be removed: {str(ip)}")
                self.sender_instances[ip].stop()
                time.sleep(1)
                self.sender_instances[ip] = None
    
        # Clean up None values
        new_d = {k:v for k, v in self.sender_instances.items() if v is not None}
        self.sender_instances = new_d
    
if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('conf', type=str, help='path to config file')
    parser.add_argument('--duration', type=int, help='number of seconds to run')
    args = parser.parse_args()

    manager = NodeSockManager(args.conf)

    if args.duration:
    # Stop the program at a certain interval only if the arg is given.
        time.sleep(args.duration)
        manager.stop()
        self.logger.info("finished")
        exit(0)

