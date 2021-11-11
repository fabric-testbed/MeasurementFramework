import os
import time
import argparse
import subprocess
import sys
import paramiko

HostDestinations = ["../ansible/hosts/", "../elk/bootstrap/"]
# Default: ["../ansible/hosts/hosts.ini", "../elk/bootstrap/hosts"]

def parseArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("-slice", "--slicename", help="Geni slice name")
    args = parser.parse_args()
    if args.slicename is not None:
        return args.slicename
    else:
        slicename = input("Please enter your GENI slice name.\n\t")
        return slicename


def getInventory(sliceName):
        print("Pulling inventory file from " + sliceName)
        output = subprocess.check_output(["/usr/local/bin/gcf/examples/readyToLogin.py", sliceName, "--useSliceAggregates", "--ansible-inventory", "-o"])
        print("Success.")


def createHostFile():
        print("Generating hosts file from inventory file.")
        # Open inventory file to convert
        with open('inventory') as f:
                lines = f.readlines()


        # Save inventory variables in the form: nodename['node name'] = [hostname, port]
        nodes = {}
        nodeName = ""
        hostName = ""
        port = ""
        for node in lines:
                nodeName = node[0 : node.find(' ')]
                hostName = node[node.find('ansible_ssh_host=')+17 : node.find('  ansible_ssh_port=')]
                port = node[node.find('ansible_ssh_port=')+17 : node.find('\n')]
                if (node.find('ansible_ssh_port=') == -1):
                        port = "22"
                nodes[nodeName] = [hostName, port]

        outputFile = ""
        outputFileForELK = ""

        # Confirm all required nodes are present.
        if "Meas_Node" not in nodes:
                print("ERROR: Meas_Node was not found in inventory. Please check topography.")
                return
        if "Meas_Net" not in nodes:
                print("ERROR: Meas_Net was not found in inventory. Please check topography.")
                return
        if "Meas_NGINX" not in nodes:
                print("ERROR: Meas_NGINX was not found in inventory. Please check topography.")
                return

        # Print required nodes
        outputFile += "[Measurement_Node]\n"
        outputFile += "Meas_Node ansible_ssh_host=%s ansible_ssh_port=%s"%(nodes["Meas_Node"][0], nodes["Meas_Node"][1])
        outputFile += " hostname=meas_node_link_net_node self_signed_key_path=meas_node_link_net_node\n"
        outputFile += "[Measurement_Net]\n"
        outputFile += "Meas_Net ansible_ssh_host=%s ansible_ssh_port=%s\n"%(nodes["Meas_Net"][0], nodes["Meas_Net"][1])
        outputFile += "[Measurement_NGINX]\n"
        outputFile += "Meas_NGINX ansible_ssh_host=%s ansible_ssh_port=%s\n"%(nodes["Meas_NGINX"][0], nodes["Meas_NGINX"][1])

        # Print required nodes for ELK (using hostnames)
        outputFileForELK += "[elk]\n"
        outputFileForELK += "Meas_Node\n\n"
        outputFileForELK += "[nginx]\n"
        outputFileForELK += "Meas_NGINX\n\n"

        # Print all other nodes
        outputFile += "\n[Experiment_Nodes]\n"
        for name,value in nodes.items():
                if ((name != "Meas_Node") and (name != "Meas_Net") and (name != "Meas_NGINX")):
                        outputFile += "%s ansible_ssh_host=%s ansible_ssh_port=%s hostname=%s_link%sm node_exporter_listen_ip=%s_link%sm\n"%(name, value[0], value[1], name, name[-1], name, name[-1])

        # Print all other nodes for ELK
        outputFileForELK += "[workers]\n"
        for name,value in nodes.items():
                if ((name != "Meas_Node") and (name != "Meas_Net") and (name != "Meas_NGINX")):
                        outputFileForELK += "%s\n" % name

        for directory in HostDestinations:
                hostFile = open(directory + "hosts", "w")
                attempt = hostFile.write(outputFile)
                hostFile.close
                print("\tSuccess. hosts file placed inside " + directory + " directory.")

        hostFileForELK = open("../elk/hosts", "w")
        writeAttempt = hostFileForELK.write(outputFileForELK)
        hostFileForELK.close
        print("\tSuccess. hosts file placed inside ../elk/ directory.")

        
        # This is done for the time being to install
        # Paramiko seems to have issues with public IP's.
        # It is understood that this will not work in Fabric.
        return [nodes["Meas_Net"][0], nodes["Meas_Net"][1]]

#======================================================================

def ansible_call():
        time.sleep(1)   # Delays for 1 seconds
                        # to help with all subprocess writes
        bootstrap_folder = os.path.dirname(os.getcwd())+"/elk/bootstrap/"
        output_ansible = subprocess.call("ansible-playbook bootstrap.yml", shell=True ,cwd=bootstrap_folder)

#======================================================================

def remote_ansible_call(host_ip, host_port):
        username = "ansible"
        command = "cd mf_git/elk/; ansible-playbook site.yml"
        host_ip = host_ip.split(' ', 1)[0];

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host_ip, host_port, username, key_filename=os.path.expanduser("~/.ssh/ansible"))

        stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)
        stdin.close()
        for line in iter(lambda: stdout.readline(2048), ""):
                sys.stdout.write(line)

#======================================================================

def main():
        sliceName = parseArgs()
        getInventory(sliceName)
        [meas_node_ip, meas_node_port] = createHostFile()
        ansible_call()
        remote_ansible_call(meas_node_ip, meas_node_port.split()[0])


if __name__ == "__main__":
    main()
