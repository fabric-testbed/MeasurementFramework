#!/usr/bin/python3
import argparse
import os
import re
import sys
import time
import json
import subprocess
import datetime
import json
import configparser
from timestampservice import timestampservice
from ctypes import *
import logging


class timestamptool():
    
    def __init__(self):
        self.args=None
        self.logger=None
        self.timestampservice= timestampservice()
        self.servicename="timestamp"
        self.read_service_info()
        self.check_elastic_status(meas_node_ip=self.meas_node_ip)
        self.check_timestamp_service_status()
   

    # Set args    
    def set_args(self, args):
        self.args=args
        self.set_up_logger(args=args)

        
        
    def set_up_logger(self, args):
        self.logger = logging.getLogger(self.servicename)
        self.logger.setLevel(logging.DEBUG)
        filehandler = logging.FileHandler(self.servicename + ".log")
        filehandler.setLevel(logging.DEBUG)
        streamhandler= logging.StreamHandler()
        if args.verbose:
            streamhandler.setLevel(logging.DEBUG)
        else:
            streamhandler.setLevel(logging.INFO)
        filehandler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        streamhandler.setFormatter(logging.Formatter(
            '%(message)s'
        ))
        self.logger.addHandler(filehandler)
        self.logger.addHandler(streamhandler)
        
        
    def read_service_info(self):
        self.config_file_path=self.timestampservice.config_file_path 
        self.hostname= self.timestampservice.hostname
        self.meas_node_ip = self.timestampservice.meas_node_ip
        self.ptp_device_name=self.get_ptp_device_name()
        self.event_index_name= self.timestampservice.event_index_name
        self.packet_index_name= self.timestampservice.packet_index_name
        self.tcpdump_output_path = self.timestampservice.tcpdump_output_path
        self.tshark_output_path = self.timestampservice.tshark_output_path
        self.event_output_path= self.timestampservice.event_output_path
        self.name_path= self.timestampservice.name_path
        self.packet_output_elastic_path = self.timestampservice.packet_output_elastic_path
        self.event_output_elastic_path = self.timestampservice.event_output_elastic_path
        self.packet_elastic_index_path = self.timestampservice.packet_elastic_index_path
        self.event_elastic_index_path = self.timestampservice.event_elastic_index_path
        self.ptp_routine = self.timestampservice.ptp_routine
        self.executable_alias_path = self.timestampservice.executable_alias_path

        
        
    ##############################################################
    ## This code section is a list of helper methods that gather 
    ## information about the experiment node
    ##############################################################
        
    # Gets the system ptp device    
    def get_ptp_device_name(self):
        result=os.popen("ps -ef |grep phc2sys").read()
        start="-s"
        end=" -c CLOCK_REALTIME"
        if (end in result):
            sindex= result.rfind(start)
            eindex= result.rfind(end)
            device = result[sindex+3:eindex].strip()   
            return (device)
        else:
            return ("Cannot find running ptp device")
        
    
    def check_elastic_status(self, meas_node_ip):
        cmd=f"sudo curl -XGET http://{meas_node_ip}:9200/"
        pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
        res = pipe.communicate()
        if (pipe.returncode!=0):
            sys.exit(f"Failed to get the status of Elasticsearch. Exit program..")
        else:
            pass
        
    def check_timestamp_service_status(self):
        cmd= f"sudo systemctl is-active --quiet timestamp.service"
        pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
        res = pipe.communicate()
        if (pipe.returncode!=0):
            sys.exit(f"Timestamp.service is not running. Start by 'sudo systemctl start timestamp.service'")
            
        else:
            pass
           
        
    ##############################################################
    
    ##############################################################
    ## This code section is a list of methods that generate files based 
    ## on the cmd input arguments
    ## packet results are written to tcpdump.pcap first and then 
    ## filtered by the tshark command and finally written to packet.json
    ## event results are written to event.json
    ##############################################################
    
    ## Event related methods..
    
    # Gets the system ptp time by calling the C routine
    def get_ptp_timestamp(self, device_name):
        self.logger.debug(f"Calling C routine to get ptp time from device {device_name}")
        func = CDLL(self.ptp_routine)
        func.get_ptp_time.restype = type(self.TIMESPEC())
        test=func.get_ptp_time(bytes(device_name, encoding='utf-8'))
        timestamp_str= str(test.tv_sec)+"."+str(test.tv_nsec)    
        return (timestamp_str)
    
    
    # Writes the event data along with the ptp time to a file
    def write_event_data_to_file(self, device_name, output_file, elastic_file):
        self.logger.debug(f"Writing event data to {output_file}")
        data_json={}
        time= self.get_ptp_timestamp(device_name)
        data_json['timestamp']=time
        data_json['name']=self.args.name
        data_json['command']=self.args.command
        if (self.args.description):
            data_json['description']=self.args.description
        else:
            data_json['description']='none'
        self.reset_file_content(record_file=output_file, elastic_file=elastic_file):
        with open(output_file, "a") as f:
            f.write('{"index":{}}'+"\n")
            f.write(str(json.dumps(data_json)) + "\n")
            
            
    ## Packet related methods
    
    # Get the tcpdump command based on the arguments
    def generate_tcpdump_command(self):
        command= f"sudo tcpdump -v -l -j adapter_unsynced --time-stamp-precision nano "
        name=self.args.name
        interface = self.args.interface
        interface_cmd = f"-i {interface} "
        command+=interface_cmd
        duration = self.args.duration
        duration_cmd= f"-G {duration} -W 1 "
        command+= duration_cmd
        write_to_file_cmd = f"-w {self.tcpdump_output_path} "
        command+= write_to_file_cmd
        protocol = self.args.protocol
        protocol_cmd = f"{protocol} "
        command+=protocol_cmd
        if (self.args.port):
            port_cmd = f"port {self.args.port} "
            command+= port_cmd
        if (self.args.host):
            host_cmd=f"and host {self.args.host}"
            command+=host_cmd
        #print (f"\n tcpdump command is: {command}")
        return (command)
       
        
    # record the name of the packet traces in the file    
    def write_packet_name_to_file(self):
        name=self.args.name
        name_file_path=self.name_path
        with open(name_file_path, "w") as f:
            f.write(name)
                   
    # generate tshark command to read the pcap file
    def generate_tshark_command(self):
        command = f"sudo -u mfuser tshark -T ek "
        pcap_file_path= self.tcpdump_output_path
        read_pcap_file_cmd= f"-r {pcap_file_path} "
        tshark_output_path= self.tshark_output_path
        tshark_output_cmd = f"> {tshark_output_path}"
        default_filters=[]
        if (self.args.protocol):
            if (self.args.protocol=="tcp"):
                default_filters = ["ip.src", "ip.dst", "frame.protocols", "tcp.srcport", "tcp.dstport", "frame.time_epoch"]
                filter_protocol_cmd = "-Y 'tcp' "
                base=""
                for f in default_filters:
                    base+=f"-e {f} "
                filter_cmd = command+read_pcap_file_cmd+filter_protocol_cmd+base+tshark_output_cmd 
                #print ("\n tshark command is: "+filter_cmd)
                return (filter_cmd)
            elif (self.args.protocol=="udp"):
                default_filters = ["ip.src", "ip.dst", "frame.protocols", "udp.srcport", "udp.dstport", "frame.time_epoch"]
                filter_protocol_cmd = "-Y '{udp}' "
                base=""
                for f in default_filters:
                    base+=f"-e {f} "
                filter_cmd = command+read_pcap_file_cmd+filter_protocol_cmd+base+tshark_output_cmd
                #print ("\n tshark command is: "+filter_cmd)
                return (filter_cmd)
        else:
            return (f"Protocol is not specified")
        
    # Run the tcpdump command to record packet traces    
    def run_tcpdump_cmd(self, cmd):
        self.logger.debug(f"Starting Tcpdump......\n")
        self.logger.debug(f"The tcpdump command is: {cmd} \n")
        p = subprocess.Popen(cmd, shell=True, stdout=sys.stdout, stderr=sys.stderr)
        res = p.communicate()
        if (p.returncode==0):
            self.logger.debug(f"Tcpdump process finished")
            return 0
        else:
            #self.logger.debug(f"Problem running tcpdump")
            return 1
            
    
    def write_packet_data_to_file(self, cmd):
        self.logger.debug(f"Running Tshark to read to pcap file......\n")
        self.logger.debug(f"The tshark command is: {cmd} \n")
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        res = p.wait()
        
    # Before each time timestamptool is run, files that record previous results should be cleared    
    def reset_file_content(self, record_file, elastic_file):
        with open (record_file, "w+"):
            pass
        time.sleep(0.5)
        p = subprocess.Popen(f"sudo rm {elastic_file}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        res = p.communicate()
        
        
        
    def upload_to_elastic(self, meas_node_ip, index_name, file):
        self.logger.debug(f"Uploading {file} to elastic...")
        cmd= f"sudo curl -XPUT 'http://{meas_node_ip}:9200/{index_name}/_bulk?refresh' -H 'Content-Type: application/json' --data-binary '@{file}'"
        self.logger.debug(f"Running command: {cmd}")
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        res = p.communicate()
        
    def download_from_elastic(self, meas_node_ip, index_name, name):
        self.logger.debug(f"Downloading from elastic...")
        elk_query='{"query": {"match": {"name": "'+name+'"}}}'
        cmd= f"sudo curl -XGET 'http://{meas_node_ip}:9200/{index_name}/_search?pretty' -H 'Content-Type: application/json' -d'{elk_query}'"
        self.logger.debug(f"Running command: {cmd}")
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        data, err = p.communicate()
        if (p.returncode==0):
            json_result = json.loads(data)
            pretty_json = json.dumps(json_result["hits"], indent=2)
            print (pretty_json)
            return json_result["hits"]
        
    # Read from local file
    def read_from_local_file(self, file):
        result = {}
        result["hits"]=[]
        with open(file, 'r') as f:
            for line in f:
                if ('"index":{}' in line):
                    continue
                else:
                    try:
                        json_obj = json.loads(line)
                        result["hits"].append(json_obj)
                    except ValueError:
                        self.logger.debug('Json cannot load %s', line)
        print (result)
        return result    
    
    
    # Wrapper method for all the method
    def process(self):
        args_json={}
        if (self.args is None):
            self.logger.debug(f"Error, no arguments detected")
            return
        else:
            for arg in vars(self.args):
                args_json[arg]=getattr(self.args, arg)
            self.logger.debug(args_json)         
        if ('type' not in args_json.keys()):
            self.logger.debug(f"Type packet or event not detected. Exit..")
            return
        
        if (args_json['type']=='packet'):
            #self.read_config_file()
            if (args_json['action']=='record'):
                self.logger.debug(f"Recording packet...")
                self.reset_file_content(record_file=self.tshark_output_path, elastic_file=self.packet_output_elastic_path)
                self.write_packet_name_to_file()
                tcpdump_cmd=self.generate_tcpdump_command()
                tshark_cmd=self.generate_tshark_command()
                t= self.run_tcpdump_cmd(cmd=tcpdump_cmd)
                if (t==0):
                    while True:
                        if (os.stat(self.tshark_output_path).st_size == 0):
                            self.write_packet_data_to_file(cmd=tshark_cmd)
                            break
                        else:
                            time.sleep(0.1)
                else:
                    self.logger.debug("Tcpdump command failed..")
                    sys.exit(f"Exit")
                if (self.args.storage=='elasticsearch'):
                    self.upload_to_elastic(meas_node_ip=self.meas_node_ip, index_name=self.packet_index_name, file=self.packet_output_elastic_path)
                
            elif (args_json['action']=='get'):
                self.logger.debug(f"Getting packet...")
                query_name=self.args.name
                if (self.args.storage=='elasticsearch'):
                    r=self.download_from_elastic(meas_node_ip=self.meas_node_ip, index_name=self.packet_index_name,name=query_name)
                    #self.get_packet_timestamp(name)
                    return r
                elif (self.args.storage=='local'):
                    r = self.read_from_local_file(file=self.packet_output_elastic_path)
                    return r
                    
            
        elif (args_json['type']=='event'):
            output_file= self.event_output_path
            output_file_elastic=self.event_output_elastic_path
            if (args_json['action']=='record'):
                self.logger.debug(f"Recording event...")
                self.write_event_data_to_file(device_name=self.ptp_device_name, output_file=self.event_output_path, elastic_file=self.event_output_elastic_path)
                if (self.args.storage=='elasticsearch'):
                    self.upload_to_elastic(meas_node_ip=self.meas_node_ip, index_name=self.event_index_name, file=self.event_output_elastic_path)
            
            elif (args_json['action']=='get'):
                self.logger.debug(f"Getting event...")
                query_name=self.args.name
                if (self.args.storage=='elasticsearch'):
                    r=self.download_from_elastic(meas_node_ip=self.meas_node_ip, index_name=self.event_index_name,name=query_name)
                    return r
                elif (self.args.storage=='local'):
                    r = self.read_from_local_file(file=self.event_output_elastic_path)
                    return r
        else:
            self.logger.debug(f"The type is not event nor packet. Stop")
            return
        
        
        
    # Structure to match the return value of the C routine: struct timespec
    class TIMESPEC(Structure):
        _fields_ = [
            ('tv_sec', c_long),
            ('tv_nsec', c_long)
    ]

            

            

if __name__ == "__main__":
    t= timestamptool()
    parser = argparse.ArgumentParser(prog="timestamptool",description="options for the timestamptool executable")
    action_subparsers = parser.add_subparsers(help='Choose an action', dest='action')
    get_parser = action_subparsers.add_parser('get', help='get -h')
    record_parser= action_subparsers.add_parser('record', help='record -h')
    
    
    # Record parser
    type_in_record_parser = record_parser.add_subparsers(help='Choose a type', dest='type')
    event_record_parser= type_in_record_parser.add_parser('event', help='event -h')
    required_args_event_record = event_record_parser.add_argument_group('Required named arguments')
    required_args_event_record.add_argument("-n", "--name", required=True, help="set name for the event")
    required_args_event_record.add_argument("-cmd", "--command",required=True, help="User input command for the event")
    required_args_event_record.add_argument("-stg", "--storage", required= True, choices=['local', 'elasticsearch'], help="Choose whether to upload the results to elasticsearch or save locally")
    event_record_parser.add_argument("-desc", "--description", help="Text description")
    event_record_parser.add_argument('-v', '--verbose', action='store_true', default=False, help='verbose output')
    event_record_parser.set_defaults(type='event')
    
    packet_record_parser= type_in_record_parser.add_parser('packet', help='packet -h')
    required_args_packet_record = packet_record_parser.add_argument_group('Required named arguments')
    required_args_packet_record.add_argument("-n", "--name", required=True, help="set name for the packet dump")
    required_args_packet_record.add_argument("-i", "--interface", required=True, help="specify the interface name for tcpdump")
    required_args_packet_record.add_argument("-proto", "--protocol", required=True, choices=['tcp','udp'], help="protocol of the packets, select from tcp or udp")
    required_args_packet_record.add_argument("-durn", "--duration", required=True, type=int, help="set duration in seconds to run tcpdump")
    required_args_packet_record.add_argument("-stg", "--storage", required= True, choices=['local', 'elasticsearch'], help="Choose whether to upload the results to elasticsearch or save locally")
    packet_record_parser.add_argument("-port", "--port", help="port of the packets")
    packet_record_parser.add_argument("-host", "--host", help="ip of the host packets are sent to or come from")
    packet_record_parser.add_argument('-v', '--verbose', action='store_true', default=False, help='verbose output')
    packet_record_parser.set_defaults(type='packet')
    

    # Get parser    
    type_in_get_parser = get_parser.add_subparsers(help='Choose a type', dest='type')
    event_get_parser = type_in_get_parser.add_parser('event', help='event -h')
    event_get_parser.add_argument('-v', '--verbose', action='store_true', default=False, help='verbose output')
    required_args_event_get = event_get_parser.add_argument_group('Required named arguments')
    required_args_event_get.add_argument("-n", "--name", required=True, help="name for the event to query")
    required_args_event_get.add_argument("-stg", "--storage", required= True, choices=['local', 'elasticsearch'], help="Choose whether to download from elasticsearch or read results from local file")
    event_get_parser.set_defaults(type='event')
    
    packet_get_parser= type_in_get_parser.add_parser('packet', help='packet -h')
    packet_get_parser.add_argument('-v', '--verbose', action='store_true', default=False, help='verbose output')
    required_args_packet_get = packet_get_parser.add_argument_group('Required named arguments')
    required_args_packet_get.add_argument("-n", "--name", required=True, help="name for the packet to query")
    required_args_packet_get.add_argument("-stg", "--storage", required= True, choices=['local', 'elasticsearch'], help="Choose whether to download from elasticsearch or read results from local file")
    packet_get_parser.set_defaults(type='packet')
    
    # General parser
    parser.add_argument("-conf_path", "--config_file_path", action='store_const', const="/home/mfuser/services/timestamp/config_file/timestamp.conf", default="/home/mfuser/services/timestamp/config_file/timestamp.conf", help="show config file path")
    args = parser.parse_args()
    #if (args.config_file_path):
        #print (f"The default config file is at  {args.config_file_path}")
    t.set_args(args=args)
    t.process()

    

    

    

 
