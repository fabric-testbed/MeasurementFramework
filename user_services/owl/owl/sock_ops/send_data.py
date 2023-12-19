from subprocess import Popen, PIPE
from shlex import split
import time
import os
import signal
import re
from decimal import *
import argparse

import influxdb_client 
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

import influxdb_client_3

'''
Script for reading/tailing a pcap file, convert the relevant contents to ASCII, 
and send data to InfluxDB. Intended for live-monitoring of OWL data.

For more information on InfluxDB, go to https://www.influxdata.com/
InfluxDB Python client: 
    https://docs.influxdata.com/influxdb/cloud/api-guide/client-libraries/python/
'''


def parse_and_send(pcap_file, verbose=False, influxdb_token=None, 
    influxdb_org=None, influxdb_url=None, influxdb_bucket=None, influxdb_desttype="meas_node"):

    # InfluxDB set up
    if influxdb_desttype == "cloud":
        write_client = influxdb_client_3.InfluxDBClient3(host=influxdb_url, token=influxdb_token, org=influxdb_org)    # For cloud push only.
    elif influxdb_desttype == "meas_node":
        write_client = influxdb_client.InfluxDBClient(url=influxdb_url, 
                                token=influxdb_token, org=influxdb_org)
        write_api = write_client.write_api(write_options=SYNCHRONOUS)

    # Continuously read the end of a pcap file
    cmd = f'tail -c +1 -f {pcap_file} | tcpdump -A -tt -n -l -r -'

    if verbose:
        print(f"Starting tcpdump session: ", cmd)

    p1 = Popen(split(f"tail -c +1 -f {pcap_file}"), stdout=PIPE)
    p2 = Popen(split("tcpdump -A -tt -n -l -r -"), stdin=p1.stdout, stdout=PIPE)


    while True:
        line = p2.stdout.readline()
        if not line:
            break
    
        newline = line.rstrip().decode()
        IP_pos = newline.find(" IP ")
    
        # Find a line that looks like
        # "1661899028.527932821 IP 10.10.2.1.40634 > 10.10.1.1.5005: UDP, length 23"
        if IP_pos != -1:
            packet_data = {}
    
            time_dst = newline[:IP_pos]
            IPs = re.findall(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', newline)

            try:
                packet_data["sender"] = IPs[0]
                packet_data["receiver"] = IPs[1]
                packet_data["received"] = time_dst
    
            except Exception as e:
                print(e)
    
        # Find a line that looks like ".........F1661899028.5274663,1877"
        elif re.search(r'\d{10}.\d{,9},\d{1,4}$', newline):
            parts = re.split(",", newline)
            timestamp = re.findall('\d{10}\.\d{,9}', parts[0])
            
            try:
                seq_n = parts[1]
                t_delta = (Decimal(time_dst) - Decimal(timestamp[0]))*1000000000

                packet_data["sent"] = timestamp[0]
                packet_data["latency"] = t_delta
                packet_data["seq"] = seq_n
                packet_data["sent_ns"] = Decimal(timestamp[0])*1000000000
            
            except Exception as e:
                print(e)


            # Check if all keys have non-empty values
            all_non_empty = all(value is not None and value != '' for value 
                                in packet_data.values())

            if all_non_empty:
                # If all values are there, push the data to InfluxDB

                # Cloud push requires different InfluxDB client module. 
                # The try/except block ensures that any prev failure in forming
                # packet_data causes program to not write out data.
                try:
                    if desttype == "meas_node":
                        point = (Point("owl")
                                .tag("sender", packet_data["sender"])
                                .tag("receiver", packet_data["receiver"])
                                .field("received", float(packet_data["received"]))
                                .field("latency", int(packet_data["latency"]))
                                .field("seq_n", int(packet_data["seq"]))
                                .time(int(packet_data["sent_ns"]), 
                                write_precision=WritePrecision.NS)
                                )        
                        write_api.write(bucket=influxdb_bucket, org=org, record=point)
                    elif desttype == "cloud":
                        point = (influxdb_client_3.Point("owl")
                                .tag("sender", packet_data["sender"])
                                .tag("receiver", packet_data["receiver"])
                                .field("received", float(packet_data["received"]))
                                .field("latency", int(packet_data["latency"]))
                                .field("seq_n", int(packet_data["seq"]))
                                .time(int(packet_data["sent_ns"]) 
                                ))        
                        write_client.write(database=influxdb_bucket, record=point)
                except Exception as e:
                    print(e)

            else:
                # Do not send incomplete entries to InfluxDB
                pass

            if verbose:
                print(packet_data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--pcapfile", type=str, default="/owl_output/owl.pcap",
                        help="path/to/the/pcap/file")
    parser.add_argument("--verbose", "-v", action='store_true', 
                        help="verbose(print packet info)")
    parser.add_argument("--token", type=str, help="InfluxDB token (str)")
    parser.add_argument("--org", type=str, help="InfluxDB organization name (str)")
    parser.add_argument("--url", type=str, help="InfluxDB URL (str)")
    parser.add_argument("--desttype", type=str, help="Destination for InfluxDB data. Either 'cloud' for the Cloud instance, or 'meas_node' for the Measurement Node (str)")
    parser.add_argument("--bucket", type=str, help="InfluxDB bucket name (str)")
    
    args = parser.parse_args()
    
    pcap_file=args.pcapfile
    verbose=args.verbose
    token = args.token
    org = args.org
    url = args.url
    bucket = args.bucket
    desttype = args.desttype

    parse_and_send(pcap_file, verbose=verbose, influxdb_token=token, influxdb_org=org, 
                    influxdb_url=url, influxdb_bucket=bucket, influxdb_desttype=desttype)
