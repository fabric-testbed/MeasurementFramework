# Orchestrating Measurement Framework (ELK/Beats) using Ansible

This document shows how to start ELK (Elasticsearch, Logstash, Kibana) and multiple beats (Filebeat, Metricbeat, Packetbeat) using Ansible scripts to orchestrate.

## 0. Manual update

Before running the ansible scripts, you have to update `bootstrap/hosts` file that lists alias name, ssh host name, and ssh port of nodes in the slice. This step will be automatically generated later using `rspec` as input file.

## 1. Bootstrapping

`bootstrap/bootstrap.yml` file creates a random SSH key pair (public and private key) and save it to `~/.ssh/ansible`. Then, it copies the public key to all the remote nodes. It copies the randomly generated private key to `Measurement` node and install required pakages (e.g. ansible) on the `Measurement` node. The `Measurement` node is going to be used to orchestrating the Measurement Framework after bootstraping step.

```bash
$ cd bootstrap
$ ansible-playbook bootstrap.yml -v
```

## 2. Orchestrating ELK/Beats on slice

Once the bootstraping step is completed, users can ssh into the `Measurement` node using the randomly generated SSH key (~/.ssh/ansible) during bootstrapping step.

```bash
$ ssh ansible@pc2.instageni.rnoc.gatech.edu -p 21304 -i ~/.ssh/ansible
```

If SSH works fine, then users can run ansible playbook to orchestrate ELK and Beats on the slice.

> Checking out dev branch will be changed later.

```bash
$ cd mf_git/MeasurementFramework
$ git checkout dev
$ ansible-playbook site.yml -v
```

## 3. Check Kibana

After previous step is completed, users can access to `ELK` node (port 80) on the slice using randomly generated Nginx password during the privous step. User should be able to find out the FQDN of `ELK` node in the `rspec` or `FIM` file. The Nginx password is saved under `credentials/nginx_passwd` file.

If everything worked correctly, users should be able to see the `Kibana` is up and running and `Filebeat, Metricbeat, Packetbeat` are sending data from worker nodes. All the pre-build dashboards are under dashboard menu in the `Kibana`.
