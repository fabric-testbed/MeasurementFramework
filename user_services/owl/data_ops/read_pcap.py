from scapy.all import *
import os
import csv
import sys
from decimal import Decimal
import datetime

class PcapProcessor:
    def __init__(self, pcapfiles, outfile="out.csv", delete_pcap=False, verbose=True):
        '''
        Args:
            pcapfiles([str,]):
        '''

        self.pcapfiles = pcapfiles
        self.outfile = outfile
        self.delete_pcap = delete_pcap
        self.verbose = verbose


    def process(self):

        for pcapfile in self.pcapfiles:
            print("file name:",  pcapfile)
            pkts = rdpcap(pcapfile)
    
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

                # Field: send-t-ISO
                fields.append(datetime.datetime.utcfromtimestamp(int(send_t)).isoformat() + 'Z')

                # Field: dst-ip
                fields.append(str(pkt[IP].dst))

                # Field: dst-t
                fields.append(str(pkt.time))  # pkt.time is type Decimal

                # Field: dst-t-ISO
                fields.append(datetime.datetime.utcfromtimestamp(int(pkt.time)).isoformat() + 'Z')

                # Field: seq-n
                fields.append(seq_n)

                # Field: latency
                latency_nano = (pkt.time-send_t)*1000000000
                fields.append(str(int(latency_nano)))

                if self.verbose:
                    print(fields)

                with open(self.outfile, 'a') as f:
                    writer = csv.writer(f)
                    writer.writerow(fields)

            if self.delete_pcap:
                os.remove(pcapfile)


if __name__ == "__main__":
   
    n = len(sys.argv)
    pcap_files = []

    for i in range(1,n):
        pcap_files.append(sys.argv[i])

    processor = PcapProcessor(pcap_files)
    processor.process()


