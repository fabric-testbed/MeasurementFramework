#!/usr/bin/python3
from influxdb_client import Point, InfluxDBClient
from influxdb_client.client.util.date_utils_pandas import PandasDateTimeHelper
from influxdb_client.client.write_api import SYNCHRONOUS
from timestampservice import timestampservice
from ipaddress import ip_address, IPv4Address
import json
import time
import datetime
import sys
import argparse

"""
Set PandasDate helper which supports nanoseconds.
"""
import influxdb_client.client.util.date_utils as date_utils
date_utils.date_helper = PandasDateTimeHelper()

class influxdb_manager():
    def __init__(self):
        self.args=None
        self.timestampservice= timestampservice()
        self.meas_ip = self.timestampservice.get_meas_node_ip_new()
        self.host_name= self.timestampservice.get_hostname_new()
        self.packet_output_influx_path= self.timestampservice.packet_output_influx_path
        self.event_output_influx_path= self.timestampservice.event_output_influx_path
        self.packet_influx_download_path = self.timestampservice.packet_influx_download_path 
        self.event_influx_download_path = self.timestampservice.event_influx_download_path
    
    # Set args    
    def set_args(self, args):
        self.args=args
    
    # Returns a list of json objects to be uploaded to Influxdb     
    def process_packet_data(self):
        records=[]
        with open(self.packet_output_influx_path, "r") as f:
            for line in f:
                if ('"index":{}' in line):
                    continue
                else:
                    try:
                        json_obj = json.loads(line)
                        point = Point(f"{self.host_name}-packet-timestamp") \
                            .tag("name", json_obj["name"]) \
                            .tag("src_ip", json_obj["src_ip"]) \
                            .tag("dst_ip", json_obj["dst_ip"]) \
                            .tag("protocol", json_obj["protocol"]) \
                            .tag("src_port", json_obj["src_port"]) \
                            .tag("dst_port", json_obj["dst_port"]) \
                            .field("count", 1) \
                            .time(json_obj["timestamp"])
                        records.append(point)
                    except ValueError:
                        sys.exit(f"failed to load {line}")
        return (records)
        
    def process_event_data(self):
        records=[]
        with open(self.event_output_influx_path, "r") as f:
            for line in f:
                if ('"index":{}' in line):
                    continue
                else:
                    try:
                        json_obj = json.loads(line)
                        point = Point(f"{self.host_name}-event-timestamp") \
                            .tag("name", json_obj["name"]) \
                            .tag("event", json_obj["event"]) \
                            .tag("description", json_obj["description"]) \
                            .field("count", 1) \
                            .time(json_obj["timestamp"])
                        records.append(point)
                    except ValueError:
                        sys.exit(f"failed to load {line}")
        return (records)
    
    def validIPAddress(self, IP):
        try:
            return "IPv4" if type(ip_address(IP)) is IPv4Address else "IPv6"
        except ValueError:
            return "Invalid"
            
                    
    def process(self):
        args_json={}
        if (self.args is None):
            sys.exit(f"Error, no arguments detected")
        else:
            for arg in vars(self.args):
                args_json[arg]=getattr(self.args, arg)
    
        if (self.args.influxdb_ip):
            if (self.validIPAddress(IP=self.args.influxdb_ip)=="IPv4"):
                url_final=f"http://{self.args.influxdb_ip}:8086"
            elif (self.validIPAddress(IP=self.args.influxdb_ip)=="IPv6"):
                url_final=f"http://[{self.args.influxdb_ip}]:8086"
        else:
            url_final = f"http://{self.meas_ip}:8086"
        
        bucket_final=self.args.bucket
        client = InfluxDBClient(url=url_final, token=self.args.token, org=self.args.org)
        write_api = client.write_api(write_options=SYNCHRONOUS)
        query_api = client.query_api()
        if (args_json['action']=='upload'):
            if (args_json['type']=='packet_data'):
                records = self.process_packet_data()
                write_api.write(bucket=bucket_final, record=records)
            elif (args_json['type']=='event_data'):
                records = self.process_event_data()
                write_api.write(bucket=bucket_final, record=records)
        elif (args_json['action']=='download'):
            if (args_json['type']=='packet_data'):
                query=f'from(bucket:"{bucket_final}")|> range(start: 0, stop: now())|> filter(fn: (r) => r._measurement == "{self.host_name}-packet-timestamp" and r.name == "{self.args.name}")'
                query_results = query_api.query(query)
                output = query_results.to_json(indent=2)
                #with open(self.packet_influx_download_path, 'w', encoding='utf-8') as f:
                    #json.dump(data, f)
                print (output)
            elif (args_json['type']=='event_data'):
                query=f'from(bucket:"{bucket_final}")|> range(start: 0, stop: now())|> filter(fn: (r) => r._measurement == "{self.host_name}-event-timestamp" and r.name == "{self.args.name}")'
                query_results = query_api.query(query)
                output = query_results.to_json(indent=2)
                #with open(self.event_influx_download_path, 'w', encoding='utf-8') as f:
                    #json.dump(data, f)
                print (output)
        """
        Close client
        """
        client.close()
                  
            
            
        
        
if __name__ == "__main__":
    i=influxdb_manager()
    parser = argparse.ArgumentParser(prog="influxdb_manager",description="options to upload or download timestamp data to influxdb")
    action_subparsers = parser.add_subparsers(help='Choose an action', dest='action')
    upload_parser = action_subparsers.add_parser('upload', help='upload -h')
    download_parser= action_subparsers.add_parser('download', help='download -h')
    
    type_in_upload_parser = upload_parser.add_subparsers(help='Choose a type', dest='type')
    event_upload_parser= type_in_upload_parser.add_parser('event_data')
    required_args_event_upload = event_upload_parser.add_argument_group('Required named arguments')
    required_args_event_upload.add_argument("-b", "--bucket", required=True, help="which influx bucket to write to")
    required_args_event_upload.add_argument("-o", "--org", required=True, help="org name")
    required_args_event_upload.add_argument("-t", "--token", required=True, help="token for authorization")
    event_upload_parser.add_argument("-ip", "--influxdb_ip", help="IP of the node where influxdb is installed")
    event_upload_parser.set_defaults(type='event_data')
    
    packet_upload_parser= type_in_upload_parser.add_parser('packet_data')
    required_args_packet_upload = packet_upload_parser.add_argument_group('Required named arguments')
    required_args_packet_upload.add_argument("-b", "--bucket", required=True, help="which influx bucket to write to")
    required_args_packet_upload.add_argument("-o", "--org", required=True, help="org name")
    required_args_packet_upload.add_argument("-t", "--token", required=True, help="token for authorization")
    packet_upload_parser.add_argument("-ip", "--influxdb_ip", help="IP of the node where influxdb is installed")
    packet_upload_parser.set_defaults(type='packet_data')
    
    type_in_download_parser = download_parser.add_subparsers(help='Choose a type', dest='type')
    event_download_parser= type_in_download_parser.add_parser('event_data')
    required_args_event_download = event_download_parser.add_argument_group('Required named arguments')
    required_args_event_download.add_argument("-b", "--bucket", required=True, help="which influx bucket to query from")
    required_args_event_download.add_argument("-o", "--org", required=True, help="org name")
    required_args_event_download.add_argument("-t", "--token", required=True, help="token for authorization")
    required_args_event_download.add_argument("-n", "--name", required=True, help="name for the data")
    event_download_parser.add_argument("-ip", "--influxdb_ip", help="IP of the node where influxdb is installed")
    event_download_parser.set_defaults(type='event_data')
    
    
    packet_download_parser= type_in_download_parser.add_parser('packet_data')
    required_args_packet_download = packet_download_parser.add_argument_group('Required named arguments')
    required_args_packet_download.add_argument("-b", "--bucket", required=True, help="which influx bucket to query from")
    required_args_packet_download.add_argument("-o", "--org", required=True, help="org name")
    required_args_packet_download.add_argument("-t", "--token", required=True, help="token for authorization")
    required_args_packet_download.add_argument("-n", "--name", required=True, help="name for the data")
    packet_download_parser.add_argument("-ip", "--influxdb_ip", help="IP of the node where influxdb is installed")
    packet_download_parser.set_defaults(type='packet_data')
    
    
    args = parser.parse_args()
    i.set_args(args=args)
    i.process()