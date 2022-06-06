# Service Scripts
This directory contains scripts for each service that will be exposed to the user via mflib.  
When a fabric experiment is initially setup the bootstrap/init process will call all the scripts in this directory. The call will pass the argument containing the services directory where the services scripts need to be placed.   
Each service has a python script named after the service.  The script sets up the files that mflib will call to create/update/start/stop/remove and get info from the service running on the meas node.  

See the example.py for a basic service setup. The example just copies a directory containing the needed scripts to the predefined directory where mflib expects to find the scripts.  