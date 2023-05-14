**This document shows how to deploy, start, stop and remove beats (`Filebeat`, `Packetbeat`) containers on the Fabric racks.**

# 1. Setting up

The user needs to create two files (`hosts` and `.vault_key_beats`) under `beats` folder.

## 1.1. `hosts` file

`hosts` file under `beats` folder lists all the target nodes. The example of `hosts` file is shown below. To deploy `Filebeat` on a node, list the target node under `[filebeats]` group in the `hosts` file. Same for the `packetbeat`.

### Filebeat options in `hosts` file

- system_enable (true or false): If true, it enables Filebeat's system module that collect syslog and secure logs.

- zeek_enable (true or false): If true, it enables Filebeat's zeek module that collect zeek log data. This supposed to be enabled only for head nodes.

```yml
[filebeats]
fabric-hn ansible_ssh_host=192.168.1.10 ansible_port=22 system_enable=true zeek_enable=true
fabric-w1 ansible_ssh_host=192.168.1.10 ansible_port=22 system_enable=true zeek_enable=true

[packetbeats]
fabric-hn ansible_ssh_host=192.168.1.10 ansible_port=22
fabric-w1 ansible_ssh_host=192.168.1.10 ansible_port=22
```

## 1.2. `.vault_key_beats` file

`.vault_key_beats` file contains ansible vault secret to decrypt the variable `mfkfk_password` in `group_vars/all/settings.yml` file. You can find password on the `Software Systems` on `1Password`. Create the `.vault_key_beats` file anywhere but make it sure give the correct path when you run ansible-playbook later.

# 2. Deploy Beats

> Deploying beats should be only done once. After successful deployment, use start, stop, and remove playbooks to manage containers.

## 2.1. Depoly Filebeat

The following command deploys `Filebeat` on the nodes in the `hosts` file.

> Change path to `vault_key_beats` based on your file location.

```shell
ansible-playbook --vault-password-file .vault_key_beats deploy_beat.yml --extra-vars='op=install'--tags "filebeat"
```

## 2.2. Deploy Packetbeat

The following command deploys `Packetbeat` on the nodes in the `hosts` file.

```shell
ansible-playbook --vault-password-file .vault_key_beats deploy_packetbeat.yml --tags "packetbeat"
```

# 3. Remove Beats containers

## 3.1. Start Beats


## 3.1. Remove Beats

Remove Filebeat

```shell
ansible-playbook --vault-password-file .vault_key_beats deploy_filebeat.yml --extra-vars='op=remove'--tags "filebeat"
```

Remove Packetbeat

```shell
ansible-playbook --vault-password-file .vault_key_beats deploy_packetbeat.yml --tags "packetbeat"
```

# 4. Encrypt and decrypt with ansible vault

Encrypt with ansible vault key.

```shell
ansible-vault encrypt_string --vault-password-file .vault_key_beats <STRING TO ENCRYPT>
```

Decrypt with ansible vault key.

```shell
ansible localhost -e '@group_vars/all/settings.yml' --vault-password-file .vault_key_beats  -m debug -a 'var=ODC.mfkfk_password'
ansible localhost -e '@group_vars/all/settings.yml' --vault-password-file .vault_key_beats  -m debug -a 'var=GMP.mfkfk_password'
```

