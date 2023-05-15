#!/usr/bin/python3
import argparse
import os
import re
import sys
import time
import json
import subprocess
import logging
import configparser


class data_transfer_tool():
    # init
    def __init__(self):
        self.config_file_path="/root/services/data_transfer/config_file/data_transfer.conf"
        self.args=None
        self.logger=None
        self.servicename="data_transfer"
        self.read_config()
    
    # read file paths from config file    
    def read_config(self):
        config = configparser.ConfigParser()
        c= config.read(self.config_file_path)
        self.prometheus_mapping_path = config['PROMETHEUS_MAPPING']['Dir'] 
        self.elk_mapping_path = config['ELK_MAPPING']['Dir']
        self.prometheus_rclone_download_path=config['PROMETHEUS_DOWNLOAD']['Dir']
        self.elk_rclone_download_path=config['ELK_DOWNLOAD']['Dir']
        self.prometheus_tar_path=config['PROMETHEUS_TAR']['Dir']
        self.elk_tar_path=config['ELK_TAR']['Dir']

    # Set args    
    def set_args(self, args):
        self.args=args
        self.set_up_logger(args=args)

    # Set up logger    
    def set_up_logger(self, args):
        self.logger = logging.getLogger(self.servicename)
        self.logger.setLevel(logging.DEBUG)
        filehandler = logging.FileHandler(self.servicename + ".log")
        filehandler.setLevel(logging.DEBUG)
        streamhandler= logging.StreamHandler(sys.stdout)
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
                   
    
    ##############################################################
    ## For prometheus, generate a snapshot using the curl command.
    ## For elastic, generate a json file
    ##############################################################
    
    # Prometheus
    def generate_prometheus_snapshot(self, ht_user, ht_password):
        self.logger.debug(f"Generating snapshot to in prometheus on meas node")
        prometheus_snapshot_url = "https://localhost:9090/api/v1/admin/tsdb/snapshot"
        cmd = f"sudo curl -k -u {ht_user}:{ht_password} -XPOST {prometheus_snapshot_url}"
        self.logger.debug(f"Running command: {cmd}")
        self.logger.debug(f"If successful, you should see a snapshot created in {self.prometheus_mapping_path}")
        p = subprocess.Popen(cmd, shell=True, stdout=sys.stdout, stderr=sys.stderr)
        res = p.wait()
        
        
    
    # Elasticsearch 
    # Step1 create snapshot repo    
    def create_snapshot_repo(self, repo_name):
        """
        registers a snapshot repo using elk rest api
        Args:
            repo_name(str): name of the repo to be created 
        """
        self.logger.debug(f"Creating snapshot repo on meas node")
        default_dir = "/var/lib/docker/volumes/elk_snapshotbackup/_data"
        cmd = f'curl -X PUT "http://localhost:9200/_snapshot/{repo_name}?pretty" -H "Content-Type: application/json" -d \'{{ "type": "fs", "settings": {{ "location": "{default_dir}" }} }}\''
        self.logger.debug(f"Running command: {cmd}")
        p = subprocess.Popen(cmd, shell=True, stdout=sys.stdout, stderr=sys.stderr)
        res = p.wait()
        
    #Step2: create a snapshot in the repo
    def create_elk_snapshot(repo_name, snapshot_name, indice=None):
        # indice default to None which includes all indices
        # snapshot will be available at /var/lib/docker/volumes/elk_snapshotbackup/_data
        
        """
        creates a snapshot repo using elk rest api
        Args:
            repo_name(str): name of the repo to be created 
            snapshot_name(str): name of the snapshot to be created
            indice(optional, list): list of indices to use
        """
        self.logger.debug(f"Creating snapshot on meas node")
        json_str = '"ignore_unavailable": true, "include_global_state": false'
        if indice:
            indice_str=",".join(indice)
            indice_str_final = f'"indices": "{indice_str}",'
            json_str_new = f'{indice_str_final} {json_str}'
            json_str_final = f"{{{json_str_new}}}"
        else:
            json_str_final = f"{{{json_str}}}"
        cmd = f'curl -X PUT "http://localhost:9200/_snapshot/{repo_name}/{snapshot_name}?wait_for_completion=true&pretty" -H "Content-Type: application/json" -d \'{json_str_final}\''
        self.logger.debug(f"Running command: {cmd}")
        p = subprocess.Popen(cmd, shell=True, stdout=sys.stdout, stderr=sys.stderr)
        res = p.wait()
    
    def tar_prometheus_file(self, file_name, snapshot_name):
        self.logger.debug(f"Creating prometheus snapshot tar file in container")
        local_file_path = self.prometheus_tar_path
        cmd = cmd = f'sudo tar -C {self.prometheus_mapping_path}/snapshots -cvf {self.prometheus_tar_path}/{file_name} {snapshot_name}'
        self.logger.debug(f"Running command: {cmd}")
        p = subprocess.Popen(cmd, shell=True, stdout=sys.stdout, stderr=sys.stderr)
        res = p.wait()
        
    def tar_elk_file(self, file_name):
        self.logger.debug(f"Creating elk snapshot tar file in container")
        local_file_path = self.elk_tar_path
        cmd = f'sudo tar -C {self.elk_mapping_path} -cvf {self.elk_tar_path}/{file_name} _data'
        self.logger.debug(f"Running command: {cmd}")
        p = subprocess.Popen(cmd, shell=True, stdout=sys.stdout, stderr=sys.stderr)
        res = p.wait()
        
    
    
    # One function to include all
    def generate_elk_snapshot(self, repo_name, snapshot_name):
        # to be store in self.elk_mapping_path (/root/services/data_transfer/elk) in the container
        # which maps /home/ubuntu/elk on the host
        # as defined in the start_data_transfer.yaml playbook
        self.create_snapshot_repo(repo_name=repo_name)
        self.create_elk_snapshot(repo_name=repo_name, snapshot_name=snapshot_name)
        
    # Check whether rclone is installed in the container or not 
    def check_rclone_status(self):
        self.logger.debug(f"Checking whether rclone is installed...")
        cmd = f"sudo rclone -V"
        pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
        res = pipe.communicate()
        if (pipe.returncode!=0):
            sys.exit(f"Failed to get the status of rclone. Exit program..")
        else:
            self.logger.debug(f"rclone is installed")
    
    # Use rclone to create remote dirs     
    def create_remote_dir_using_rclone(self, storage, remote_dir):
        self.logger.debug(f"using rclone to create remote dir {storage}:{remote_dir}")
        cmd = f"sudo rclone mkdir {storage}:{remote_dir}"
        self.logger.debug(f"The command is: {cmd}")
        pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
        res = pipe.communicate()
    
    # Use rclone to delete remote dirs    
    def delete_remote_dir_using_rclone(self, storage, remote_dir):
        self.logger.debug(f"using rclone to delete remote dir {storage}:{remote_dir}")
        cmd = f"sudo rclone purge {storage}:{remote_dir}"
        self.logger.debug(f"The command is: {cmd}")
        pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
        res = pipe.communicate()
    
    
    # Prepare to upload
    def upload_data_to_storage(self, data_type, local_file_name, storage, remote_dir):
        self.logger.debug(f"using rclone to upload {local_file_name} to {storage}:{remote_dir}")
        if (data_type=="prometheus"):
            local_file_path = self.prometheus_tar_path
        elif (data_type == "elk"):
            local_file_path = self.elk_tar_path
        else:
            sys.exit(f"data type has to be prometheus or elk. Exit program..")
        cmd = f"sudo rclone copy -P {local_file_path}/{local_file_name} {storage}:{remote_dir}"
        self.logger.debug(f"The command is: {cmd}")
        pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
        res = pipe.communicate()
        #self.logger.debug(f"You should see {local_file_name} in {storage}:{remote_dir}")
        
    # prepare to download
    def download_data_from_storage(self,data_type, storage, remote_dir, file_name):
        self.logger.debug(f"using rclone to download {file_name} from {storage}:{remote_dir}")
        if (data_type=="prometheus"):
            local_file_path = self.prometheus_rclone_download_path
        elif (data_type == "elk"):
            local_file_path = self.elk_rclone_download_path
        else:
            sys.exit(f"data type has to be prometheus or elk. Exit program..")
        cmd = f"sudo rclone copy -P {storage}:{remote_dir}/{file_name} {local_file_path}"
        self.logger.debug(f"The command is: {cmd}")
        pipe = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
        res = pipe.communicate()
        self.logger.debug(f"You should see {file_name} in {local_file_path}")
        
    # Call different funcs based on the arguments     
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
            self.logger.debug(f"Type not found Exit..")
            return
        
        if (args_json['action']=='process_remote_dir'):
            self.check_rclone_status()
            if (args_json['type']=='create'):
                self.create_remote_dir_using_rclone(storage=self.args.storage, remote_dir=self.args.dir)
            elif (args_json['type']=='delete'):
                self.delete_remote_dir_using_rclone(storage=self.args.storage, remote_dir=self.args.dir)
            else:
                sys.exit(f"type has to be create or delete. Exit program..")
        elif (args_json['action']=='generate_backup'):
            if (args_json['type']=='prometheus'):
                self.generate_prometheus_snapshot(ht_user=self.args.user, ht_password=self.args.password)
            elif (args_json['type']=='elk'):
                self.generate_elk_snapshot(repo_name=self.args.repo, snapshot_name= self.args.snapshot)
        elif (args_json['action']=='upload_backup'):
            self.check_rclone_status()
            if (args_json['type']=='prometheus'):
                self.upload_data_to_storage(data_type="prometheus", local_file_name=self.args.file, storage=self.args.storage, remote_dir=self.args.dir)
            elif (args_json['type']=='elk'):
                self.upload_data_to_storage(data_type="elk", local_file_name=self.args.file, storage=self.args.storage, remote_dir=self.args.dir)
        elif (args_json['action']=='download_backup'):
            self.check_rclone_status()
            if (args_json['type']=='prometheus'):
                self.download_data_from_storage(data_type="prometheus", storage=self.args.storage, remote_dir=self.args.dir, file_name=self.args.file)
            elif (args_json['type']=='elk'):
                self.download_data_from_storage(data_type="elk", storage=self.args.storage, remote_dir=self.args.dir, file_name=self.args.file)
        elif (args_json['action']=='tar_snapshot'):
            if (args_json['type']=='prometheus'):
                self.tar_prometheus_file(file_name=self.args.file, snapshot_name=self.args.snapshot)
            elif (args_json['type']=='elk'):
                self.tar_elk_file(file_name=self.args.file)
            
        else:
            sys.exit(f"action has to be process_remote_dir or generate_backup or upload_backup or download_backup or tar_snapshot. Exit program..")
        
        
if __name__ == "__main__":
    d= data_transfer_tool()
    parser = argparse.ArgumentParser(prog="data_transfer_tool",description="options for the data_transfer_tool executable")
    action_subparsers = parser.add_subparsers(help='Choose an action', dest='action')
    generate_parser = action_subparsers.add_parser('generate_backup', help='generate_backup -h')
    upload_parser= action_subparsers.add_parser('upload_backup', help='upload_backup -h')
    download_parser=action_subparsers.add_parser('download_backup', help='download_backup -h')
    rclone_parser = action_subparsers.add_parser('process_remote_dir', help='process_remote_dir -h')
    tar_parser = action_subparsers.add_parser('tar_snapshot', help='tar_snapshot -h')
    
    
    # Generate_backup parser(to generate backup data file)
    type_in_generate_parser = generate_parser.add_subparsers(help='Choose a type', dest='type')
    prometheus_generate_parser= type_in_generate_parser.add_parser('prometheus', help='prometheus -h')
    required_args_prometheus_generate = prometheus_generate_parser.add_argument_group('Required named arguments')
    required_args_prometheus_generate.add_argument("-u", "--user", required=True, help="set ht user name")
    required_args_prometheus_generate.add_argument("-p", "--password", required=True, help="set ht password")
    prometheus_generate_parser.add_argument('-v', '--verbose', action='store_true', default=False, help='verbose output')
    prometheus_generate_parser.set_defaults(type='prometheus')
    
    elk_generate_parser = type_in_generate_parser.add_parser('elk', help='elk -h')
    required_args_elk_generate = elk_generate_parser.add_argument_group('Required named arguments')
    required_args_elk_generate.add_argument("-r", "--repo", required=True, help="set repo name")
    required_args_elk_generate.add_argument("-s", "--snapshot", required=True, help="set snapshot password")
    elk_generate_parser.add_argument('-v', '--verbose', action='store_true', default=False, help='verbose output')
    elk_generate_parser.set_defaults(type='elk')
    
    
    
    # upload_backup parser (to upload data to cloud storage)
    type_in_upload_parser = upload_parser.add_subparsers(help='Choose a type', dest='type')
    prometheus_upload_parser= type_in_upload_parser.add_parser('prometheus', help='prometheus -h')
    required_args_prometheus_upload = prometheus_upload_parser.add_argument_group('Required named arguments')
    required_args_prometheus_upload.add_argument("-file", "--file", required=True, help="set file name")
    required_args_prometheus_upload.add_argument("-s", "--storage", required=True, help="set storage")
    required_args_prometheus_upload.add_argument("-d", "--dir", required=True, help="set remote dir")
    prometheus_upload_parser.add_argument('-v', '--verbose', action='store_true', default=False, help='verbose output')
    prometheus_upload_parser.set_defaults(type='prometheus')
    
    elk_upload_parser = type_in_upload_parser.add_parser('elk', help='elk -h')
    required_args_elk_upload = prometheus_upload_parser.add_argument_group('Required named arguments')
    required_args_elk_upload.add_argument("-file", "--file", required=True, help="set file name")
    required_args_elk_upload.add_argument("-s", "--storage", required=True, help="set storage")
    required_args_elk_upload.add_argument("-d", "--dir", required=True, help="set remote dir")
    elk_upload_parser.add_argument('-v', '--verbose', action='store_true', default=False, help='verbose output')
    elk_upload_parser.set_defaults(type='elk')
    
    
    
    # download_backup parser (to download data from cloud storage)
    type_in_download_parser = download_parser.add_subparsers(help='Choose a type', dest='type')
    prometheus_download_parser= type_in_download_parser.add_parser('prometheus', help='prometheus -h')
    required_args_prometheus_download = prometheus_download_parser.add_argument_group('Required named arguments')
    required_args_prometheus_download.add_argument("-file", "--file", required=True, help="set file name")
    required_args_prometheus_download.add_argument("-s", "--storage", required=True, help="set storage")
    required_args_prometheus_download.add_argument("-d", "--dir", required=True, help="set remote dir")
    prometheus_download_parser.add_argument('-v', '--verbose', action='store_true', default=False, help='verbose output')
    prometheus_upload_parser.set_defaults(type='prometheus')
    
    
    elk_download_parser = type_in_upload_parser.add_parser('elk', help='elk -h')
    required_args_elk_download = prometheus_download_parser.add_argument_group('Required named arguments')
    required_args_elk_download.add_argument("-file", "--file", required=True, help="set file name")
    required_args_elk_download.add_argument("-s", "--storage", required=True, help="set storage")
    required_args_elk_download.add_argument("-d", "--dir", required=True, help="set remote dir")
    elk_download_parser.add_argument('-v', '--verbose', action='store_true', default=False, help='verbose output')
    elk_download_parser.set_defaults(type='elk')
    
    
    
    
    # rclone parser
    type_in_rclone_parser = rclone_parser.add_subparsers(help='Choose a type', dest='type')
    rclone_create_parser = type_in_rclone_parser.add_parser('create', help='create -h')
    required_args_rclone_create = rclone_create_parser.add_argument_group('Required named arguments')
    required_args_rclone_create.add_argument("-s", "--storage", required=True, help="set storage")
    required_args_rclone_create.add_argument("-d", "--dir", required=True, help="set remote dir")
    rclone_create_parser.add_argument('-v', '--verbose', action='store_true', default=False, help='verbose output')
    rclone_create_parser.set_defaults(type='create')
    
    rclone_delete_parser = type_in_rclone_parser.add_parser('delete', help='delete -h')
    required_args_rclone_delete = rclone_delete_parser.add_argument_group('Required named arguments')
    required_args_rclone_delete.add_argument("-s", "--storage", required=True, help="set storage")
    required_args_rclone_delete.add_argument("-d", "--dir", required=True, help="set remote dir")
    rclone_delete_parser.add_argument('-v', '--verbose', action='store_true', default=False, help='verbose output')
    rclone_delete_parser.set_defaults(type='delete')
    
    
    # tar parser
    type_in_tar_parser = tar_parser.add_subparsers(help='Choose a type', dest='type')
    prometheus_tar_parser= type_in_tar_parser.add_parser('prometheus', help='prometheus -h')
    required_args_prometheus_tar = prometheus_generate_parser.add_argument_group('Required named arguments')
    required_args_prometheus_tar.add_argument("-file", "--file", required=True, help="set tar file name")
    required_args_prometheus_tar.add_argument("-s", "--snapshot", required=True, help="set snapshot name")
    prometheus_tar_parser.add_argument('-v', '--verbose', action='store_true', default=False, help='verbose output')
    prometheus_tar_parser.set_defaults(type='prometheus')
    
    elk_tar_parser = type_in_generate_parser.add_parser('elk', help='elk -h')
    required_args_elk_tar = elk_generate_parser.add_argument_group('Required named arguments')
    required_args_elk_tar.add_argument("-file", "--file", required=True, help="set tar file name")
    elk_tar_parser.add_argument('-v', '--verbose', action='store_true', default=False, help='verbose output')
    elk_tar_parser.set_defaults(type='elk')
    

    
    # General parser
    parser.add_argument("-conf_path", "--config_file_path", action='store_const', const="/root/services/data_transfer/config_file/data_transfer.conf", default="/root/services/data_transfer/config_file/data_transfer.conf", help="show config file path")
    args = parser.parse_args()
    d.set_args(args=args)
    d.process()