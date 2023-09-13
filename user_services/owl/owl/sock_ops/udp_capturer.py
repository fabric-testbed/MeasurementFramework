import subprocess
import time
import os
import signal
import re
from decimal import *
import argparse
import psutil


class TcpdumpOps:
    def __init__(self, ip_addr, port):
        '''
        ip_addr(str):
        port(int):
        '''
        
        self.interface = self.find_interface(ip_addr)
        self.port = port


    def start_capture(self, outfile=None, pcap_interval=None):

        if not outfile:
            outfile=f"~/{int(time.time())}.pcap"

        rollover_sec=f"-G {str(pcap_interval)}" if pcap_interval else " "
        
        cmd = f"sudo tcpdump -U -vfn -XX -tt  \
                -i {self.interface}  --direction in \
                -j adapter_unsynced \
                --time-stamp-precision nano \
                port {str(self.port)} \
                -w {outfile} \
                {rollover_sec}"

        print("Starting tcpdump session: ", cmd)
        print("pcap file: ", outfile)

        self.p = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
        print("Pid: ", self.p.pid)
       
        # without this, capturer may exit (when sender is not running)
        self.p.wait()


    def stop(self):
        self.p.terminate()


    def find_interface(self, ip):
        '''
        find the interface for a given ip address
        Returns:
            str: os interface name ('eth0' etc.) 
        '''

        addrs = psutil.net_if_addrs()
        
        for interface in addrs.keys():
            for nic in addrs[interface]:
                if nic.address == ip:
                    return interface

        return 'any'

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("--ip", type=str, default='10.0.0.1', help="destination IP")
    parser.add_argument("--port", type=int, default=5005, 
                        help="listening port number")
    parser.add_argument("--pcap-sec", type=int, default=None, 
                        help="number of capture seconds for each pcap file")
    parser.add_argument("--outfile", type=str, default="/owl_output/owl.pcap",
                        help="path/to/output/file")
    parser.add_argument("--duration", type=int, default=60,
                        help="number of seconds to run capture")


    args = parser.parse_args()
    ip_addr = args.ip
    port = args.port
    interval_pcap = args.pcap_sec
    outfile = args.outfile
    sec = args.duration 


    session = TcpdumpOps(ip_addr, port)
    session.start_capture(outfile, interval_pcap)
    
    time.sleep(sec)
    session.stop()

