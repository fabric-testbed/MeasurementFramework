from scapy.all import *
import os
import csv
import sys
from decimal import Decimal
import datetime
import argparse


def convert_pcap_to_csv(pcapfile, outfile="owl_output.csv", verbose=Fales):

    pkts=rdpcap(pcapfile)
    print(f"reading... {pcapfile}")

    for pkt in pkts:
        # Fields are <linkid, src-ip, send-t, send-t-ISO, 
        #             dst-ip, dst-t, dst-t-ISO, seq-n, latency_nano>
        # latency_nano is in nano-seconds
    
        fields=[]
    
        # Field: linkid
        linkid = 0 # for now
        fields.append(str(linkid))
    
        # Field: src-ip
        fields.append(str(pkt[IP].src))
    
        # Field: send-t
        send_t, seq_n = pkt[Raw].load.decode().split(",")
        send_t = Decimal(send_t)  # To prevent floating point issues
        fields.append(str(send_t))
    
        # Field: dst-ip
        fields.append(str(pkt[IP].dst))
    
        # Field: dst-t
        fields.append(str(pkt.time))  # pkt.time is type Decimal
    
        # Field: seq-n
        fields.append(seq_n)
    
        # Field: latency
        latency_nano = (pkt.time-send_t)*1000000000
        fields.append(str(int(latency_nano)))
    
        if verbose:
            print(fields)
    
        with open(outfile, 'a') as f:
            writer = csv.writer(f)
            writer.writerow(fields)
    

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("--pcapfile", type=str, help="path/to/a/pcap/file")
    parser.add_argument("--outfile", type=str, default="owl_output.csv")
    parser.add_argument("--verbose", "-v", action='store_true', default=False)

    args = parser.parse_args()
    
    convert_pcap_to_csv(args.pcapfile, outfile=args.outfile, verbose=args.verbose)


