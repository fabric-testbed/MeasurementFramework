# ELK and Beats Service

ELK (Elastichsearch, Logstash, Kibana) and Beats (Filebeat, Metricbeat, Packetbeat) provides the monitoring Fabric slice VMs using logs.

To access the ELK data go to the Kibana interface.
From your local machine, tunnel into the measure node using ssh -L 10020:localhost:80 -F <fabric-ssh-config-file> -i <your portal_slice_id_rsa-file> <slice-username>@<meas_node-ip>
Browse to https://localhost:10020

Use mflib to get the username and password needed to access Kibana.

data = {}
# Set the info you want to get.
data["get"] = ["nginx_id", "nginx_password"]
# Call info using service name and data dictionary.
info_results = mf.info("elk", data)
print(info_results)
Output:
{'success': True, 'msg': '', 'nginx_password': 'sZ_1T:fJum83J9W8ofre\n', 'nginx_id': 'fabric'}