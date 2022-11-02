import subprocess
import time
import os
import signal
import re
from decimal import *
import argparse
import psutil

# This script must be run as root


class TcpdumpOps:
    def __init__(self, ip_addr, port):
        '''
        ip_addr(str):
        port(int):
        '''
        
        self.interface = self.find_interface(ip_addr)
        self.port = port

    def start_capture(self, output_dir, pcap_interval):
        cmd = f"tcpdump -vfn -XX -tt  \
                -i {self.interface}  --direction in \
                -j adapter_unsynced \
                --time-stamp-precision nano \
                port {str(self.port)} \
                -w {output_dir}/%s.pcap \
                -G {str(pcap_interval)}"

        print("Starting tcpdump session: ", cmd)
        print("pcap files will be saved in: ", output_dir)

        self.p = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
        print("Pid: ", self.p.pid)

    def start_live_capture(self):
        cmd = f'tcpdump -U  -q -n  -A -tt \
                -i {self.interface} --direction in \
                -j adapter_unsynced \
                port {str(self.port)} \
                --time-stamp-precision nano'
        
        print(f"Starting tcpdump session: ", cmd)

        self.p = subprocess.Popen(cmd.split(),stdout=subprocess.PIPE)

        # Set decimal to 9 sub-decimal digits
        getcontext().prec=9
        print(getcontext())

        while True:
            line = self.p.stdout.readline()
            if not line:
                break
        
            newline = line.rstrip().decode()
            IP_pos = newline.find("IP")
        
            # Find a line that looks like
            # "1661899028.527932821 IP 10.10.2.1.40634 > 10.10.1.1.5005: UDP, length 23"
            if IP_pos != -1:
                packet_data = {}
        
                time_dst = newline[:(IP_pos-1)]
                IPs = re.findall(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', newline)
        
                packet_data["sender"] = IPs[0]
                packet_data["receiver"] = IPs[1]
                packet_data["received"] = time_dst
        
        
            # Find a line that looks like ".........F1661899028.5274663,1877"
            elif re.search(r'\d{10}.\d{,9},\d{1,4}$', newline):
                parts = re.split(",", newline)
                timestamp = re.findall('\d{10}\.\d{,9}', parts[0])
                seq_n = parts[1]
        
                t_delta = Decimal(time_dst) - Decimal(timestamp[0])
        
                packet_data["sent"] = timestamp[0]
                packet_data["latency"] = t_delta
                packet_data["seq"] = seq_n
        
                # For debugging
                print(packet_data)

                # TODO: Push this to InfluxDB

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
    parser.add_argument("--pcap-sec", type=int, default=45, 
                        help="number of capture seconds for each pcap file")
    parser.add_argument("--outdir", type=str, default="/owl_output",
                        help="output dir where pcap files will be saved")
    parser.add_argument("--duration", type=int, default=60, 
                        help="number of seconds to run each capture")


    args = parser.parse_args()
    ip_addr = args.ip
    port = args.port
    interval_pcap = args.pcap_sec
    output_dir = args.outdir 
    sec = args.duration 

    session1 = TcpdumpOps(ip_addr, port)
    session1.start_capture(output_dir, interval_pcap)
    time.sleep(sec)
    session1.stop()

    time.sleep(5)

    session2 = TcpdumpOps(ip_addr, port)
    session2.start_live_capture()
    time.sleep(sec)
    session2.stop()


