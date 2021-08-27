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
