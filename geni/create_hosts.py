import os
#import glob
import argparse
import subprocess

def parseArgs():
    print("----------")
    parser = argparse.ArgumentParser()
    parser.add_argument("-slice", "--slicename", help="Geni slice name")
    args = parser.parse_args()
    if args.slicename is not None:
        return args.slicename
    else:
        slicename = input("Please enter your GENI slice name.\n")
        print("----------")
        return slicename


def getInventory(sliceName):
        print("Pulling inventory file from " + sliceName)
        # Running readyToLogin.py
        #os.system("/opt/gcf/examples/readyToLogin.py " + sliceName + " --useSliceAggregates --ansible-inventory -o")

        output = subprocess.check_output(["/opt/gcf/examples/readyToLogin.py", sliceName, "--useSliceAggregates", "--ansible-inventory", "-o"])
        # Removes unneeded files generated by omni, currently not in use due to potential bugs.
#        for file in glob.glob(sliceName + "*"):
#            os.remove(file)
#        for file in glob.glob("getversion*"):
#            os.remove(file)
        print("Success.\n----------")


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

        if "meas_node" not in nodes:
                print("ERROR: meas_node was not found in inventory. Please check topography.\n----------")
                return


        # Print out inventory items for non-normal nodes
        for name,value in nodes.items():
                if((name.find("node_") == -1)):
                       outputFile += "%s ansible_ssh_host=%s ansible_ssh_port=%s"%(name, value[0], value[1])

                       if((name.find("meas_node") != -1)):
                        outputFile += " hostname=meas_node_link_net_node self_signed_key_path=meas_node_link_net_node\n"
                       else:
                        outputFile += "\n"


        # Print out inventory items for normal nodes
        outputFile += "[nodes]\n"
        for name,value in nodes.items():
                if((name.find("node_") != -1)):
                       outputFile += "%s ansible_ssh_host=%s ansible_ssh_port=%s hostname=%s_link%sm node_exporter_listen_ip=%s_link%sm\n"%(name, value[0], value[1], name, name[-1], name, name[-1])


        # Save outputFile to hosts.ini
        hostFile = open("../ansible/hosts/hosts.ini", "w")
        attempt = hostFile.write(outputFile)
        hostFile.close
        print("Success. Hosts.ini file placed inside ansible/hosts directory.\n----------")


def main():
        sliceName = parseArgs()
        getInventory(sliceName)
        createHostFile()

if __name__ == "__main__":
    main()