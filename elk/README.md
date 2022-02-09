# ELK (Elasticsearch, Logstash, Kibana) and Beats deployment using Ansible and Python scripts

This folder (`./elk`) contains all Ansible and Python scripts to deploy ELK and Beats on different project enviroments. Read more details for each project from link below.

- [Fabric](./FABRIC_README.md)
- [GENI](./GENI_README.md)

## Structure of folder and descriptions

<pre>
<b>elk</b>                      
│  README.md             <span style="color:green">// This document</span>               
│  README_AnsibleOnly.md <span style="color:green">// Deploying ELK and beats using Ansible only</span> 
│  FABRIC_README.md      <span style="color:green">// Readme file for Fabric project</span> 
│  GENI_README.md        <span style="color:green">// Readme file for GENI project</span> 
│  hosts                 <span style="color:green">// host file for Ansible</span> 
│  ansible.cfg           <span style="color:green">// Ansible configuration file</span> 
│
└── <b>bootstrap</b>            
│   │   ansible.cfg      <span style="color:green">// Ansible configuration file for bootstrap</span>
│   └── bootstrap.yml    <span style="color:green">// Ansible bootstrap playbook</span>
│
└── <b>docker-images</b>        <span style="color:green">// Docker files for ELK and beats</span>
│
└── <b>host_vars</b>            <span style="color:green">// host configuration for nodes</span>
│
└── <b>fabric-rack</b>          <span style="color:green">// Ansible script for fabric rack deployment</span>
│
└── <b>roles</b>                <span style="color:green">// Ansible roles for deployment</span>
│   │   <b>elk</b>              <span style="color:green">// deploying elk role</span>
│   └── <b>worker</b>           <span style="color:green">// deploying beats role</span>
│
└── <b>Service Management</b>   <span style="color:green">// Control beats using Ansible</span>
</pre>
