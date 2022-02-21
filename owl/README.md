# OWL One Way Latency

## Current owl.conf file format
```
[GENERAL]
LinkCheckInterval = <sec (int)>
UdpPort = <port>
ServiceRequestFile = <service request file>.json

[receiver]
PcapInterval = <sec (int)>

[sender]
SendInterval= <sec (float)>
```

## Current json service request file format
```
{
  "links":[ 
            {
	      "src": "10.10.2.2",
	      "dst": "10.10.2.1"
	    },
            {
	      "src": "10.10.2.1",
	      "dst": "10.10.2.2"
	    },
            {
	      "src": "10.10.3.2",
	      "dst": "10.10.3.1"
	    },
            {
	      "src": "10.10.3.1",
	      "dst": "10.10.3.2"
	    },
            {
	      "src": "10.10.1.1",
	      "dst": "10.10.1.2"
	    },
            {
	      "src": "10.10.1.2",
	      "dst": "10.10.1.1"
	    },
            {
	      "src": "10.10.2.1",
	      "dst": "10.10.3.1"
	    }
  ]
}

```
## How to run quick tests
### 1-node test (preferrably with multiple interfaces)

#### Terminal window 1
1. Run Tcpdump to obvserve outgoing packets
```
sudo tcpdump -i any -Q out dst port 5005
```

#### Terminal window 2
1. While NodeManger is running, edit and save the json file.
```
mv owl_service_requst.json  owl_service_request.json.original
vim owl_service_request.json
# edit and save
```

#### Terminal window 3
1. Run NodeManager alone or inside Python (needs to be root)
```
$ python3
> import NodeManger as manager
> n = manager.NodeManager()
> n.start()
   # Do whatever is needed (observe, change the json file)
> n.stop()
```
2. Check the pcapfile.
```
sudo tcpdump -ttnnr <file>.pcap
```

## Tcpdump command
```
$ sudo tcpdump -vfn -XX -tt  -i eth1 port 5005
tcpdump: listening on eth1, link-type EN10MB (Ethernet), capture size 262144 bytes
1637724059.954885 IP (tos 0x0, ttl 64, id 50479, offset 0, flags [DF], proto UDP (17), length 55)
    10.10.2.1.46829 > 10.10.2.2.5005: UDP, length 27
	0x0000:  02ff cdea 320d 020a ec84 3976 0800 4500  ....2.....9v..E.
	0x0010:  0037 c52f 4000 4011 5d70 0a0a 0201 0a0a  .7./@.@.]p......
	0x0020:  0202 b6ed 138d 0023 184b 3136 3337 3732  .......#.K163772
	0x0030:  3430 3539 2e39 3534 3034 3632 2c32 3032  4059.9540462,202
	0x0040:  3131 3132 33
```
### For reading pcap files using tcpdump (with the payload in HEX and ASCII)
```
sudo tcpdump -qn -tt  -XX -r <file>.pcap
```
## Scapy installation (tentative) 
This is needed only for parsing pcap files. Will likely be changed to `pip`
installation.
```
sudo apt install python3-scapy
```

