# Fabric Prometheus Releases

Fabric Prometheus has releases to ensure that the deployed versions are consistent.  

There are several roles:
* Rack
* Central
* Experimentor - geni




## Release Changes


### ?
* Updated Alerts with new labels for response groups. See https://fabric-testbed.atlassian.net/wiki/spaces/FP/pages/1693941761/Operational+Alerts
* Added Alertmanager configurations and templates for central alertmanager.
    * Updated alerts to slack formating. 

### v0.1-beta.1
* Removed htaccess for prometheus UI on port 9090. Moved it to localhost only.

### v0.1-beta.0
Initial version that can be deployed to racks.
