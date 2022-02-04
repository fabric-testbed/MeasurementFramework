# ELK (Elasticsearch, Logstash, Kibana) and Beats deployment using Ansible and Python scripts

This folder (`./elk`) contains all Ansible and Python scripts to deploy ELK and Beats on different project enviroments. Read more details for each project from link below.

- [Fabric](./FABRIC_README.md)
- [GENI](./GENI_README.md)

## Structure of folder and descriptions

```
elk
│   README.md
│   FABRIC_README.md
│   GENI_README.md
│   hosts
│
└─── bootstrap
│    │   ansible.cfg
│    │   bootstrap.yml
│    │
│    └─── files
│         └─── sudoer_ansible
│
└─── docker-images
│
└─── roles
│
└─── Service Management
```
