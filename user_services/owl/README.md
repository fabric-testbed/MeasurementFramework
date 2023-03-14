# OWL(One Way Latency)

Program for measuring one-way latency between nodes. Though it is written 
specifically for FABRIC Testbed, it should work in a general setting with 
minimal edits, if at all.

As outlined below, it can run natively (not recommended), using Docker containers,
or as part of the Measurement Framework environment.


# Architecture
TODO

# How to Run

## 1. As part of Measurement Framework
TODO


## 2. Using Docker containers

### Prerequisites

- Docker daemon (ipv6 enabled if necessary)
- Directory on the host machine for owl config files (owl.conf, links.json)
- Directory on the host machine for owl output files (\*.pcap)

### Usage

1. Build a container using the Dockerfile. 

```
# Example:
$  sudo docker build -t owl-app MeasurementFramework/user_services/owl/
```

2. Run the container with the following.


#### Using NodeSockManager.py

Requires owl.conf and links.json files

```
$ docker run [--rm] -dp 5005:5005 \
$ sudo docker run --rm -dp 5005:5005 \
--mount type=bind,source=<path/to/local/config/dir>,target=/owl_config \
--mount type=bind,source=<path/to/local/output/dir>,target=/owl_output  \
--network="host"  \
--privileged \
owl-app NodeSockManager.py /owl_config/owl.conf
```

#### Using socket operation scripts

```
$sudo docker run --rm -dp 5005:5005 \
--network="host"  \
--privileged \
owl-app  sock_ops/udp_sender.py [options]
```

## 3. Natively

### Prerequisites

- tcpdump
- gcc
- scapy (`pip install --pre scapy[basic]`)
- psutil (`pip install psutil`)
- `ptp_time.so` file placed in the same directory as `ptp_time.c`

In addition, Python scripts must be run with `sudo` privilege to perform 
necessary socket operations.

### Usage

The simplest experiment can be performed with 

```
# Sender side 
sudo python3 owl/sock_ops/udp_sender.py [options]

# Example
sudo python3 owl/sock_ops/udp_sender.py --ptp-device "/dev/ptp1"  --dest-ip "10.0.0.2" \
--frequency 0.1 --seq-n 123 --duration 60

# Receiver side
sudo python3 owl/sock_ops/udp_capturer.py [options]
```

Alternatively use `NodeSockManager` on multiple nodes with config and links files.

```
sudo python3 owl/NodeSockManager.py <path/to/config/file>
```


# Current Limitations
- IPV4 only
- "static" capture only (capturer side saves tcpdump output to .pcap files)
- Assumes end points are non-routing devices with only 1 experimenter's network interface.


