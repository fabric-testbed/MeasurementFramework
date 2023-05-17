import subprocess
import time
import os
import signal
import re
from decimal import *
import argparse
import psutil
import influxdb_client 
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS


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
        cmd = f"sudo tcpdump -vfn -XX -tt  \
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
       
        # without this, capturer may exit (when sender is not running)
        self.p.wait()


    def start_live_capture(self, influxdb_token, 
                           influxdb_org, influxdb_url, influxdb_bucket):

        # influxdb set up
        write_client = influxdb_client.InfluxDBClient(url=influxdb_url, 
                                    token=influxdb_token, org=influxdb_org)
        write_api = write_client.write_api(write_options=SYNCHRONOUS)


        cmd = f'sudo tcpdump -U  -q -n  -A -tt \
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
        
                t_delta = int((Decimal(time_dst) - Decimal(timestamp[0]))*1000000000)
        
                packet_data["sent"] = timestamp[0]
                packet_data["latency"] = t_delta
                packet_data["seq"] = seq_n

                # Push the data to InfluxDB

                point = (Point("owl")
                        .tag("sender", packet_data["sender"])
                        .tag("receiver", packet_data["receiver"])
                        .field("received", float(packet_data["received"]))
                        .field("latency", int(packet_data["latency"]))
                        .field("seq_n", int(packet_data["seq"]))
                        .time(int(Decimal(packet_data["sent"])*1000000000), 
                        write_precision=WritePrecision.NS)
                        )        

                write_api.write(bucket=influxdb_bucket, org=org, record=point)

                # For debugging
                print(packet_data)


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
    parser.add_argument("--live", action='store_true',
                        help="add this for live capture")
    parser.add_argument("--token", type=str, help="influxdb token (str)")
    parser.add_argument("--org", type=str, help="influxdb org name (str)")
    parser.add_argument("--url", type=str, help="influxdb url (str)")
    parser.add_argument("--bucket", type=str, help="influxdb bucket name (str)")


    args = parser.parse_args()
    ip_addr = args.ip
    port = args.port
    interval_pcap = args.pcap_sec
    output_dir = args.outdir 
    sec = args.duration 
    live = args.live
    token = args.token
    org = args.org
    url = args.url
    bucket = args.bucket


    session = TcpdumpOps(ip_addr, port)
    if args.live:
        session.start_live_capture(token, org, url, bucket)
    else:
        session.start_capture(output_dir, interval_pcap)

    time.sleep(sec)
    session.stop()

