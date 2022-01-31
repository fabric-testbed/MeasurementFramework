from scapy.all import *
import os
import csv
import sys

class PcapProcessor:
    def __init__(self, pcapfiles, outfile="test.csv", delete_pcap=False, verbose=True):
        self.pcapfiles = pcapfiles
        self.outfile = outfile
        self.delete_pcap = delete_pcap
        self.verbose = verbose


    def process(self):

        for pcapfile in self.pcapfiles:
            pkts = rdpcap(pcapfile)
    
            for pkt in pkts:
                # Fields are <linkid, src-ip, send-t, dst-ip, dst-t, seq-n, latency>
                fields=[]
    
                linkid = 0 # for now
                fields.append(str(linkid))
                fields.append(str(pkt[IP].src))
    
                send_t, seq_n = pkt[Raw].load.decode().split(",")
    
                fields.append(send_t)
                fields.append(str(pkt[IP].dst))
                fields.append(str(pkt.time))
                fields.append(seq_n)
                
                latency = pkt.time - float(send_t)
    
                fields.append(str(latency))
    
                if self.verbose:
                    print(fields)
    
                with open(self.outfile, 'a+') as f:
                    writer = csv.writer(f)
                    writer.writerow(fields)
    
            if self.delete_pcap:
                os.remove(pcapfile)

if __name__ == "__main__":
   
    n = len(sys.argv)
    pcap_files = []

    for i in range(1,n):
        pcap_files.append(sys.argv[i])

    test = PcapProcessor(pcap_files)
    test.process()


            
            


