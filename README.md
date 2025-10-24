# MeasurementFramework
This is the framework for setting up monitoring to a FABRIC experiment. This repo formerly housed all of the FABRIC measurement framework systems that monitor the entirety of the FABRIC Infrastructure. This repo has been broken up into separate repositories to ease maintenece, security and deployment tasks.
The former MeasurementFramework repository now consists of the following repoositories:
* MeasurementFramework (this repo) - Is responsible for installing monitoring into a FABRIC user's experimental slice.
* mf-rack - installs the monitoring on each FABRIC rack
* mf-central - responsible for the nodes that are central to the infrasturcture monitoring, this includes the operators metrics site and ping-plus
* mf-parsers - a set of parsing routings to create custom private configuration files for the infrastructure monitoring
* mf-public - the sites that gather and make certain infrastructure metrics available to the public and FABRIC users
* mf-dashboards - a collection of premade dashboards users can add to their slice monitoring
* mf-data-import-containers - allows a user to save and import ELK and Prometheus data gathered in their FABRIC slice

Also see the following repositories for monitoring information:  
* **Deprecated** [fabric-prometheus](https://github.com/fabric-testbed/fabric-prometheus) Has been replaced by this repository's fabric_prometheus directory.
* [Kafka Cluster](https://github.com/fabric-testbed/fabric-docker-images/tree/master/kafka): describes how to set up a secure Kafka cluster (3 zookeepers and 3 brokers with SSL/SASL/SCRAM). 
* [Elastic Search Cluster with Nginx](https://github.com/fabric-testbed/fabric-docker-images/tree/master/elk-ssl-xpack): describes how to set up a secure ES cluster (X-Pack security enabled) with Nginx.
* [fabric-docker-images](https://github.com/fabric-testbed/fabric-docker-images) For custom docker images.
* [fabric-deployment](https://github.com/fabric-testbed/fabric-deployment) For ansible scripts & inventory files needed for Rack & Central installs. Private Repo with access limited to system admins.
* [fabrictestbed-extensions](https://github.com/fabric-testbed/fabrictestbed-extensions) For mflib python scripts to instrumentize a users experiments.
* [jupyter-examples](https://github.com/fabric-testbed/jupyter-examples)  For examples of how to instrumentize a slice using Jupyter Notebooks and the mflib python code.
