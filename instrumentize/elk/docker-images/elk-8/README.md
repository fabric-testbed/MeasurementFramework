Make sure to set the `vm.max_map_count` to `262144`.

https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html

```
sysctl -w vm.max_map_count=262144
```

The `.env` password may need to contain letters. (not working with only numbers)

To start `Fleet Server`, user has to go through several steps.

https://www.elastic.co/guide/en/fleet/8.4/add-a-fleet-server.html

But the command given by `Elasticsearch` is wrong. You need `ca.crt` and you can get it from `es01` container.

```
sudo docker-compose cp es01:/usr/share/elasticsearch/config/certs/ca/ca.crt .
```

```
sudo ./elastic-agent install   --fleet-server-es=https://localhost:9200   --fleet-server-service-token=AAEAAWVsYXN0aWMvZmxlZXQtc2VydmVyL3Rva2VuLTE2NjI3MzIwMzA0OTI6QjVhQkk3VUpTdmkzVGJKTVBkTkhiUQ  --fleet-server-policy=fleet-server-policy --fleet-server-es-ca=/home/mfuser/elk/elastic-agent-8.4.1-linux-x86_64/ca.crt
```

https://discuss.elastic.co/t/fleet-server-wont-start-certificate-error/274617

To install agent on other hosts, it needs to set up using this command on the other hosts.

Note that user needs to use `--insecure` option to make this work for self-signed cert. [https://www.elastic.co/guide/en/fleet/8.4/install-fleet-managed-elastic-agent.html]

```
sudo ./elastic-agent install --url=https://10.0.0.4:8220 --enrollment-token=WTJPWElvTUJLb0o5MkhuRXh1TVU6alNVUmdsdnJRN3VVQy1wdjFwWHJLZw== --fleet-server-es-ca=/home/mfuser/elastic-agent-8.4.1-linux-x86_64/ca.crt --insecure
```
