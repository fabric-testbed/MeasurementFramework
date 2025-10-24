# MeasurementFramework
Framework for setting up Fabric Testbed measurement systems.  
This repository contains the needed scripts/code to install the various systems used to monitor the Fabric Testbed.  
Also see the following repositories for monitoring information:  
* **Deprecated** [fabric-prometheus](https://github.com/fabric-testbed/fabric-prometheus) Has been replaced by this repository's fabric_prometheus directory.
* [Kafka Cluster](https://github.com/fabric-testbed/fabric-docker-images/tree/master/kafka): describes how to set up a secure Kafka cluster (3 zookeepers and 3 brokers with SSL/SASL/SCRAM). 
* [Elastic Search Cluster with Nginx](https://github.com/fabric-testbed/fabric-docker-images/tree/master/elk-ssl-xpack): describes how to set up a secure ES cluster (X-Pack security enabled) with Nginx.


#TODO inprogress dir restructure...

## MeasurementFramework Repositories
 
The [MeasurementFramework](https://github.com/fabric-testbed/MeasurementFramework) repository contains the majority of code that is used for setting up the monitoring infrastructure throughout the FABRIC systems. FABRIC systems include the FABRIC Racks, FABRIC Central Services (ODC) and FABRIC user experiments (aka slice). Additionaly some code may be used on GENI slices.  
Other locations for MeasurementFramework code include:
* [fabric-docker-images](https://github.com/fabric-testbed/fabric-docker-images) For custom docker images.
* [fabric-deployment](https://github.com/fabric-testbed/fabric-deployment) For ansible scripts & inventory files needed for Rack & Central installs. Private Repo with access limited to system admins.
* [fabrictestbed-extensions](https://github.com/fabric-testbed/fabrictestbed-extensions) For mflib python scripts to instrumentize a users experiments.
* [jupyter-examples](https://github.com/fabric-testbed/jupyter-examples)  For examples of how to instrumentize a slice using Jupyter Notebooks and the mflib python code.


## MeasurementFramework
Contains the core code for installing monitoring (aka instrumentizing) to FABRIC systems. Most of the repository consists of ansible scripts and configuration files used to install containers that gather metrics and log data and then ship them to a central location.  
The repository is divided in to 2 sections: instrumentize and user_services.
* instrumentize - Code used to install monitoring services to a system.
    * ansible - Common location for ansible playbooks that call Ansible Roles defined in sibiling directories.
    * elk  - Elastic Search & Kibana installation scripts.
    * prometheus - Prometheus & Exporters, Thanos, Grafana and Alertmanager installation scripts. 
    * geni - 
* user_services - Code optionally used on FABRIC Experiments.
    * owl - One Way Latency scripts.
    * ptp - Precision Time Protocol setup for a FABRIC Experiment.

## MeasurementFramework Branches

Merging to branches matching rc* is restricted to our admins. These are release candidate branches that will be merged in to main.   
Merging to the Main branch is restricted to our admins. Anything that is merged into the main branch must be tested and non-breaking. Merges into main brach should always have a version tag.   
There is a dev, dev-elk and a dev-prom branch for merging features developed for those systems. Merging to theses branches is also restricted to admins. The branches should appear similar to this: 

```text
                         | <-- dev-elk  <-- features
main <-- rc* <-- dev <-- |
                         | <-- dev-prom <-- features
```                     
Create a new brach when developing a new feature.


## fabrictestbed-extensions Branches

The current branch is mflib.  

## jupyter-examples Branches

The current branch is mflib.




