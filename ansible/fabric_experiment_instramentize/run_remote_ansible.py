import os
import time
import argparse
import subprocess
import sys
import paramiko

def remote_ansible_call(host_ip, host_port):
        username = "ansible"
        command = "cd /home/ansible/mf_git/ansible/fabric_experiment_instramentize/; ansible-playbook playbook_fabric_experiment_install_docker.yml"
        
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host_ip, host_port, username, key_filename=os.path.expanduser("~/.ssh/ansible"))

        stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)
        stdin.close()
        for line in iter(lambda: stdout.readline(2048), ""):
                sys.stdout.write(line)

#======================================================================

def main():

        remote_ansible_call("206.196.180.233", 22)


if __name__ == "__main__":
    main()
