#!/usr/bin/python
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
        self.config_file_path="/home/mfuser/services/timestamp/config_file/timestamp.conf"
        self.read_config()
        self.hostname= self.get_hostname()
        self.meas_node_ip=self.get_meas_node_ip()
        self.event_index_name= self.get_event_index_name()
        self.packet_index_name= self.get_packet_index_name()
        #for broken lines
        self.broken_line=[]
        self.complete_line=True 
       

    def convert_epoch(self, time_ns):
        date_time = datetime.datetime.fromtimestamp(float(time_ns))
        s = date_time.strftime("%Y-%m-%dT%H:%M:%S")
        s+= "."+time_ns.split(".")[1]+"Z"
        return s
    

    def read_config(self):
        config = configparser.ConfigParser()
        c= config.read(self.config_file_path)
        self.tcpdump_output_path = config['TCPDUMP']['Out_dir'] 
        self.tshark_output_path = config['TSHARK']['Out_dir']
        self.event_output_path=config['EVENT']['Out_dir']
        self.name_path=config['PACKETNAME']['Out_dir']
        self.packet_output_elastic_path = config['PACKET_ELASTIC']['Out_dir']
        self.event_output_elastic_path = config['EVENT_ELASTIC']['Out_dir']
        self.packet_elastic_index_path = config['PACKET_ELASTIC_INDEX']['Dir']
        self.event_elastic_index_path = config['EVENT_ELASTIC_INDEX']['Dir']
        self.ptp_routine = config['PTP_ROUTINE']['Dir']
        self.executable_alias_path = config['ALIAS']['Dir']
    
    def get_hostname(self):
        file="/etc/hostname"
        with open(file, "r") as h:
            for line in h:
                line_no_space= line.strip()
                name= line_no_space.rsplit("-",1)[1]
                return (name) 
            
    def get_meas_node_ip(self):
        return ("10.0.0.4")
    
    def get_event_index_name(self):
        name= self.hostname
        index_name=name+"-event-timestamp"
        return (index_name)
    
    # Gets the static elastic packet index to push to
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
        


    def read_changing_file(self, file, file_path):
        file.seek(0, 2)
        while True:
            if (os.path.exists(file_path)):
                if (os.stat(file_path).st_size == 0):
                    file.seek(0, 0)
            line = file.readline().rstrip()
            if not line:
                time.sleep(0.2)
                continue
            yield line


    def process_packet_file(self):
        if (os.path.exists(self.tshark_output_path)== False):
            with open(self.tshark_output_path, "w+") as ts:
                pass
        tshark_file = open(self.tshark_output_path, "r+")
        #os.chmod(self.tshark_output_path, 0o777)
        os.chown(self.tshark_output_path, pwd.getpwnam('mfuser').pw_uid, 0)
        tshark_output = self.read_changing_file(file=tshark_file, file_path=self.tshark_output_path)
        for line in tshark_output:
            print ('processing %s', line)
            #print ('\n')
            new_line = ""
            if (self.complete_line):
                try:
                    json_obj = json.loads(line)
                except ValueError:
                    self.broken_line.append(line)
                    self.complete_line=False
                    print ('json cannot load %s', line)
                    return
            else:
                if (len(self.broken_line)>0):
                    try:
                        json_obj = json.loads(''.join(self.broken_line)+line)
                    except ValueError:
                        self.broken_line.append(line)
                        self.complete_line=False
                        print ('json cannot load %s', line)
                        return
                    self.broken_line.clear()
                    self.complete_line=True 
                
            if "index" in json_obj.keys():
                #print("This is index line")
                new_line = '{"index":{}}'
                with open(self.packet_output_elastic_path,"a") as f:
                    f.write(new_line + "\n")
            else:
                new_json_obj = {}
                name = ""
                with open(self.name_path, "r") as n:
                    for line in n:
                        name = line.strip()
                new_json_obj["name"] = name
                ts = json_obj["layers"]["frame_time_epoch"][0]
                final_timestamp = self.convert_epoch(time_ns=ts)
                new_json_obj["timestamp"] = str(final_timestamp)
                new_json_obj["src_ip"] = json_obj["layers"]["ip_src"][0]
                new_json_obj["dst_ip"] = json_obj["layers"]["ip_dst"][0]
                new_json_obj["protocol"] = json_obj["layers"]["frame_protocols"][0]
                if ("tcp_srcport" in json_obj["layers"].keys()):
                    new_json_obj["src_port"]=int(json_obj["layers"]["tcp_srcport"][0])
                    new_json_obj["dst_port"]=int(json_obj["layers"]["tcp_dstport"][0])
                elif ("udp_srcport" in json_obj["layers"].keys()):
                    new_json_obj["src_port"]=int(json_obj["layers"]["udp_srcport"][0])
                    new_json_obj["dst_port"]=int(json_obj["layers"]["udp_dstport"][0])
                with open(self.packet_output_elastic_path, "a") as f:
                    f.write(str(json.dumps(new_json_obj)) + "\n")


    def process_event_file(self):
        if (os.path.exists(self.event_output_path)== False):
            with open(self.event_output_path, "w+") as ev:
                pass
        event_file = open(self.event_output_path, "r+")
        event_output = self.read_changing_file(file=event_file, file_path=self.event_output_path)
        os.chown(self.event_output_path, pwd.getpwnam('mfuser').pw_uid, 0)
        for line in event_output:
            new_line = ""
            json_obj = json.loads(line)
            if "index" in json_obj.keys():
                #print("This is index line")
                new_line = '{"index":{}}'
                with open(self.event_output_elastic_path, "a") as f:
                    f.write(new_line + "\n")
            else:
                new_json_obj = {}
                ts = json_obj['timestamp']
                final_timestamp = self.convert_epoch(time_ns=ts)
                new_json_obj["timestamp"] = str(final_timestamp)
                new_json_obj["name"] = json_obj["name"]
                new_json_obj["command"] = json_obj["command"]
                new_json_obj["description"] = json_obj["description"]
                with open(self.event_output_elastic_path, "a") as f:
                    f.write(str(json.dumps(new_json_obj)) + "\n")

    



if __name__ == "__main__":
    ts=timestampservice()
    ts.create_event_elastic_index()
    ts.create_packet_elastic_index()
    Process(target=ts.process_packet_file).start()
    Process(target=ts.process_event_file).start()
