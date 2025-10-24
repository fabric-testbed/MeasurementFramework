This directory contains SNMP Exporter yaml config files. Each file contains one (maybe more) modules that will be combined into the snmp.yml file.
The only jinja var is the snmp_community_string that will be set per rack. 


Possible files include:
* if_mib for switches
* if_mib might be usefull for every thing (try it for the storage)
* pdu for the Power distribution unit
* isis for network to network connections for swithches
* tmi_ptu for the GPS PTP time unit
* data storage ?