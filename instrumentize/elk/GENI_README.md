# Orchestrating Measurement Framework (ELK/Beats) using Ansible for GENI

This document shows how to start `ELK` (`Elasticsearch`, `Logstash`, `Kibana`) and multiple beats (`Filebeat`, `Metricbeat`, `Packetbeat`) using Ansible and Python scripts on **`GENI`**.

If user wants to deploy `ELK` and `Beats` only using `Ansible` script, then check [readme file for using ansible only](./README_AnsibleOnly.md).

## 0. Requirements

You must have following packages are installed on the machine that you are running this code:

- `omni`
- `ansible`
- `paramiko`

## 1. Create slice and reserve resources on GENI

First, you have to create a slice using your own `rspec` or using one of `rspec_GENI_w*.rspec` files and reserve resources. Make it sure your machine that is orchestraing have proper SSH key to access all the GENI slice's VMs.

## 2. Orchestrating ELK/Beats on slice

Once all the resources are reserved successfully and you can access to all the VMs properly, you can simply run single Python command like below.

```bash
$ cd MeasurementFramework/geni
$ python GENI_Instrumentize_Slice.py --slice your_geni_slice_name_here
```

Note you may also call the GENI_Instrumentize_Slice.py by giving it the path to the inventory file returned by a previous OMNI call (such as using the OMNI Docker contianer to obtain the slice inventory) This facilitates testing and does not require the installation of the OMNI software. See the MeasurmentFramework/geni/OMNI_docker directory for details.

```
$ docker run --rm -w /root/working --mount type=bind,source=$PWD,target=/root/working -it omni_image /bin/bash
root@33587f830da6:~/working# omni-configure
root@33587f830da6:~/working# readyToLogin <slice-name> --useSliceAggregates --ansible-inventory -o
root@33587f830da6:~/working# exit

$ python GENI_Instrumentize_Slice.py --slice your_geni_slice_name_here --inventory your_omni_created_inventory_file_above
```

## 3. Check Kibana

After previous step is completed, users can access to `Meas_Net` node (port 80) on the slice using randomly generated Nginx password during the privous step. User should be able to find out the FQDN of `Meas_Net` node in the `rspec` or `FIM` file. The Nginx password is saved under `credentials/nginx_passwd` file and default user name is `fabric`.

If everything worked correctly, users should be able to see the `Kibana` is up and running and `Filebeat, Metricbeat, Packetbeat` are sending data from worker nodes. All the pre-build dashboards are under dashboard menu in the `Kibana`.
