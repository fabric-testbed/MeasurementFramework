#!/usr/bin/python3
import time
import datetime
import os
import json
import configparser
import pwd
from multiprocessing import Process
from os.path import exists



class timestampservice():
    
    def __init__(self):
        self.config_file_path="/root/services/timestamp/config_file/timestamp.conf"
        self.read_config()
        self.hostname= self.get_hostname_new()
        self.meas_node_ip=self.get_meas_node_ip_new()
        self.event_index_name= self.get_event_index_name()
        self.packet_index_name= self.get_packet_index_name()
    

    def read_config(self):
        config = configparser.ConfigParser()
        c= config.read(self.config_file_path)
        self.tcpdump_output_path = config['TCPDUMP']['Out_dir'] 
        self.tshark_output_path = config['TSHARK']['Out_dir']
        self.event_output_path=config['EVENT']['Out_dir']
        self.name_path=config['PACKETNAME']['Out_dir']
        self.packet_output_influx_path = config['PACKET_INFLUX']['Out_dir']
        self.event_output_influx_path = config['EVENT_INFLUX']['Out_dir']
        self.packet_elastic_index_path = config['PACKET_ELASTIC_INDEX']['Dir']
        self.event_elastic_index_path = config['EVENT_ELASTIC_INDEX']['Dir']
        self.packet_influx_download_path = config['PACKET_INFLUX_DOWNLOAD']['Out_dir']
        self.event_influx_download_path= config['EVENT_INFLUX_DOWNLOAD']['Out_dir']
        self.ptp_routine = config['PTP_ROUTINE']['Dir']
        self.ptp_clock_name_path= config['PTP_CLOCK_NAME']['Out_dir']
    
    def get_hostname(self):
        file="/etc/hostname"
        with open(file, "r") as h:
            for line in h:
                line_no_space= line.strip()
                host_name= line_no_space.rsplit("-",1)[1]
                return (host_name) 
    
    # function to adapt to the new format of hostname(Node1)
    def get_hostname_new(self):
        file="/etc/hostname"
        with open(file, "r") as h:
            for line in h:
                host_name= line.strip()
                return (host_name) 
        
            
    def get_meas_node_ip(self):
        # Find the line with _meas_node
        meas_ip=""
        with open("/etc/hosts", "r") as f:
            lines = f.readlines()
            for line in lines:
                if ("_meas_node" in line):
                    meas_ip = line.split()[0]
        return (meas_ip)
    
    # function to adpat to mflib meas node hostname change
    def get_meas_node_ip_new(self):
        # Find the line with meas-node
        meas_ip=""
        with open("/etc/hosts", "r") as f:
            lines = f.readlines()
            for line in lines:
                if ("meas-node" in line):
                    meas_ip = line.split()[0]
        return (meas_ip)
    
    
    def get_event_index_name(self):
        name= self.hostname
        index_name=name+"-event-timestamp"
        return (index_name)
    

    def get_packet_index_name(self):
        name= self.hostname
        index_name=name+"-packet-timestamp"
        return (index_name)
    
    
    def create_elastic_indexes(self):
        command = f"sudo curl http://{self.meas_node_ip}:9200/_aliases "
        result=os.popen(command).read()
        result_json= json.loads(result)
        if (self.event_index_name in result_json.keys()):
            print ("event index already exists. pass")
            pass
        else:
            self.create_event_elastic_index()
        if (self.packet_index_name in result_json.keys()):
            print ("packet index already exists. pass")
            pass
        else:
            self.create_packet_elastic_index()
            
        
    
    def create_event_elastic_index(self):
        basic_cmd = f"curl -XPUT 'http://{self.meas_node_ip}:9200/{self.event_index_name}?include_type_name=true' -H 'Content-Type: application/json' -d'@{self.event_elastic_index_path}'"
        result=os.popen(basic_cmd).read()
        if ("false" in result):
            print ("create event index fail")
            return
        else:
            print ("create event index succeed")
        
        
    def create_packet_elastic_index(self):
        basic_cmd = f"curl -XPUT 'http://{self.meas_node_ip}:9200/{self.packet_index_name}?include_type_name=true' -H 'Content-Type: application/json' -d'@{self.packet_elastic_index_path}'"
        result=os.popen(basic_cmd).read()
        if ("false" in result):
            print ("create packet index fail")
            return
        else:
            print ("create packet index succeed")
            
            
    def initialize_files(self):
        if (os.path.exists(self.tshark_output_path)== False):
            with open(self.tshark_output_path, "w+") as ts:
                pass
        
        
        if (os.path.exists(self.event_output_path)== False):
            with open(self.event_output_path, "w+") as ev:
                pass
        

if __name__ == "__main__":
    ts=timestampservice()
    ts.initialize_files()