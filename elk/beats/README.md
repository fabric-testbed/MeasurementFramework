**This document shows how to deploy, start, stop and remove beats (`Filebeat`, `Packetbeat`) containers on the Fabric racks.**

# 1. Setting up

The user needs to create two files (`hosts` and `.vault_key_beats`) under `beats` folder.

## 1.1. `hosts` file

`hosts` file under `beats` folder lists all the target nodes. The example of `hosts` file is shown below. To deploy `Filebeat` on a node, list the target node under `[filebeat]` group in the `hosts` file. Same for the `packetbeat`.

```yml
[filebeats]
fabric-hn ansible_ssh_host=192.168.1.10 ansible_port=22
fabric-w1 ansible_ssh_host=192.168.1.10 ansible_port=22

[packetbeats]
fabric-hn ansible_ssh_host=192.168.1.10 ansible_port=22
fabric-w1 ansible_ssh_host=192.168.1.10 ansible_port=22
```

## 1.2. `.vault_key_beats` file

`.vault_key_beats` file contains ansible vault secret to decrypt `group_vars/all/settings.yml` file. You can find password on the `Software Systems` on `1Password`. Create the `.vault_key_beats` file anywhere but make it sure give the correct path when you run ansible-playbook later.

# 2. Deploy Beats

> Deploying beats should be only done once. After successful deployment, use start, stop, and remove playbooks to manage containers.

## 2.1. Depoly Filebeat

The following command deploys `Filebeat` on the nodes in the `hosts` file.

> Change path to `vault_key_beats` based on your file location.

```shell
ansible-playbook --vault-password-file .vault_key_beats deploy_beats.yml --tags "filebeat"
```

## 2.2. Deploy Packetbeat

The following command deploys `Packetbeat` on the nodes in the `hosts` file.

```shell
ansible-playbook --vault-password-file .vault_key_beats deploy_beats.yml --tags "packetbeat"
```

# 3. Start, Stop, Remove Beats containers

## 3.1. Start Beats

Start Filebeat

```shell
ansible-playbook --vault-password-file .vault_key_beats start_beats.yml --tags "filebeat"
```

Start Packetbeat

```shell
ansible-playbook --vault-password-file .vault_key_beats start_beats.yml --tags "packetbeat"
```

## 3.2. Stop Beats

Stop Filebeat

```shell
ansible-playbook --vault-password-file .vault_key_beats stop_beats.yml --tags "filebeat"
```

Stop Packetbeat

```shell
ansible-playbook --vault-password-file .vault_key_beats stop_beats.yml --tags "packetbeat"
```

## 3.3. Remove Beats

Remove Filebeat

```shell
ansible-playbook --vault-password-file .vault_key_beats remove_beats.yml --tags "filebeat"
```

Remove Packetbeat

```shell
ansible-playbook --vault-password-file .vault_key_beats remove_beats.yml --tags "packetbeat"
```
