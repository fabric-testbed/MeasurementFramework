# Prometheus Service
Prometheus provides the metric monitoring for a Fabric Experiment.

Calling create will install prometheus, grafana and various exporters.

To connect to grafana, use tunnel.

ssh -L 10010:localhost:443 -F <your fabric bastion config path> -i <your slice private key> <vm username>@<vm ip>

Then browse to https://localhost:10010/grafana/login
Use the password ?  
You may need to retype the port number after accepting self signed cert.

