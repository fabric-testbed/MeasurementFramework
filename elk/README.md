# Orchestrating Measurement Framework (ELK/Beats) using Ansible

This document shows how to start ELK (Elasticsearch, Logstash, Kibana) and multiple beats (Filebeat, Metricbeat, Packetbeat) using Ansible scripts to orchestrate on GENI.

## 0. Requirements

You must have following packages are installed on the machine that you are running this code:

- `omni`
- `ansible`

## 1. Create slice and reserve resources on GENI

First, you have to create a slice using your own `rspec` or using one of `rspec_GENI_w*.rspec` files and reserve resources. Make it sure your machine that is orchestraing have proper SSH key to access all the GENI slice's VMs.

## 2. Orchestrating ELK/Beats on slice

Once all the resources are reserved successfully and you can access to all the VMs properly, you can simply run single Python command like below.

```bash
$ cd MeasurementFramework/geni
$ python GENI_Instrumentize_Slice.py -slice your_geni_slice_name_here
```

## 3. Check Kibana

After previous step is completed, users can access to `Meas_Net` node (port 80) on the slice using randomly generated Nginx password during the privous step. User should be able to find out the FQDN of `Meas_Net` node in the `rspec` or `FIM` file. The Nginx password is saved under `credentials/nginx_passwd` file and default user name is `fabric`.

If everything worked correctly, users should be able to see the `Kibana` is up and running and `Filebeat, Metricbeat, Packetbeat` are sending data from worker nodes. All the pre-build dashboards are under dashboard menu in the `Kibana`.
