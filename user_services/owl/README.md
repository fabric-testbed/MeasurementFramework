# OWL(One Way Latency)

Program for measuring one-way latency between nodes. Though it is written 
specifically for FABRIC Testbed, it should work in a general setting with 
minimal edits, if at all.

As outlined below, it can be used either within the Measurement Framework
environment or as a stand-alone application possibly running inside a Docker
contaier.

Under all circumstances, the sender and receiver nodes must have PTP (Precision
time Protocol) service running. To verify this and to look up the PTP clock path, 
run the following command:

```
px -ef | grep phc2sys
```


# How to Collect OWL data

## 1. As part of Measurement Framework

Refer to the Jupyter Notebook examples.


## 2. Using Docker containers

### Prerequisites

- PTP (Precision Time Protocol) service
- Docker daemon (ipv6 enabled if necessary)
- Directory on the host machine for owl config files (owl.conf, links.json)
- Directory on the host machine for owl output files (\*.pcap)

### Usage

1. clone the repository and navigate to the `owl` directory.

```
git clone -b owl https://github.com/fabric-testbed/MeasurementFramework.git
cd MeasurementFramework/user_services/owl
```

2. Build a container using the Dockerfile. 

```
# Example:
$  sudo docker build -t owl-app .
```

2. Run the container with the following.


#### Using NodeSockManager.py

Requires owl.conf and links.json files

```
$ sudo docker run --rm -dp <port_num>:<port_num> \
--mount type=bind,source=<path/to/local/config/dir>,target=/owl_config \
--mount type=bind,source=<path/to/local/output/dir>,target=/owl_output  \
--network="host"  \
--privileged \
owl-app NodeSockManager.py /owl_config/owl.conf
```

##### Example

```
# On all nodes

$ sudo docker run --rm -dp 5005:5005 \
--mount type=bind,source=~/mydir/owl/config,target=/owl_config \
--mount type=bind,source=~/mydir/owl/output,target=/owl_output  \
--network="host"  \
--privileged \
owl-app NodeSockManager.py /owl_config/owl.conf

```

#### Using socket operation scripts

```
# sender side
$sudo docker run --rm -dp <port_num>:<port_num> \
--network="host"  \
--privileged \
owl-app  sock_ops/udp_sender.py [options]

# receiver 
$sudo docker run --rm -dp <port_num>:<port_num> \
--mount type=bind,source=<path/to/local/output/dir>,target=/owl_output \
--network="host"  \
--privileged \
owl-app  sock_ops/udp_capturer.py [options]
```

##### Examples

```
# On Node 1

    # sender side
    sudo docker run -dp 5005:5005 \
    --network="host"  \
    --privileged \
    owl-app  sock_ops/udp_sender.py --ptp-device "/dev/ptp1" \
    --ptp-so-file "/MeasurementFramework/user_services/owl/owl/sock_ops/time_ops/ptp_time.so" \
    --dest-ip "10.0.0.2" --dest-port 5005 --frequency 0.1 \
    --seq-n 5452 --duration 60

# On Node 2

    # receiver
    sudo docker run -dp 5005:5005 \
    --mount type=bind,source=/tmp/owl/,target=/owl_output \
    --network="host"  \
    --privileged \
    owl-app  sock_ops/udp_capturer.py \
    --ip "10.0.0.2" --port 5005 --pcap-sec 60 \
    --outdir /owl_output --duration 60
```



## 3. Natively (Not recommended)

### Prerequisites
- PTP (Precision Time Protocol) service 
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
# clone the repo and navigate to owl
git clone -b owl https://github.com/fabric-testbed/MeasurementFramework.git
cd MeasurementFramework/user_services/owl

# create a shared object file from ptp_time.c
gcc -fPIC -shared -o owl/sock_ops/time_ops/ptp_time.so owl/sock_ops/time_ops/ptp_time.c

# Run the sender 
sudo python3 owl/sock_ops/udp_sender.py [options]

# Example
sudo python3 owl/sock_ops/udp_sender.py --ptp-device "/dev/ptp1" 
		--ptp-so-file "owl/sock_ops/time_ops/ptp_time.so" \
	 	--dest-ip "10.0.0.2" --dest-port 5005 --frequency 0.1 \
		--seq-n 5452 --duration 60

# Run the receiver
sudo python3 owl/sock_ops/udp_capturer.py [options]

# Example
sudo python3 owl/sock_ops/udp_capturer.py --ip "10.0.0.2" --port 5005 --pcap-sec 60 \
		--outdir /home/username/owl_output --duration 60
```

Alternatively use `NodeSockManager` on multiple nodes with config and links files.

```
sudo python3 owl/NodeSockManager.py <path/to/config/file>
```

# How to Convert Collected data (`.pcap` files) to a CSV file  

(Work in Progress)
Use either `owl/data_ops/read_pcap.py` or `owl/DataProcessManager.py`



# Current Limitations
- IPV4 only
- "static" capture only (capturer side saves tcpdump output to .pcap files)
- Assumes hosts are (non-routing) endpoints.


