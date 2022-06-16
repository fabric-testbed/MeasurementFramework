from data_ops import read_pcap as pcap_reader
import glob
import sys
import os

class DataProcessManager:
    def __init__(self, dir_path, outfile, delete_pcap=False, verbose=True):

        files = glob.glob(f'{dir_path}/*.pcap')
        # Remove zero-bye pcap files
        self.pcapfiles = [f for f in files if os.stat(f).st_size > 0] 
        
        print("pcapfiles: ", self.pcapfiles)

        self.outfile = f'{dir_path}/{outfile}'
        self.delete_pcap = delete_pcap
        self.verbose = verbose


    def process(self):
        processor = pcap_reader.PcapProcessor(
                            self.pcapfiles, 
                            self.outfile, 
                            self.delete_pcap, 
                            self.verbose)
        processor.process()

if __name__ == "__main__":
    

        if len(sys.argv) < 2:
            print("Error: needs 1 directory path")
            exit(1)

        elif len(sys.argv) == 2:
            data_processor = DataProcessManager(sys.argv[1], 'out.csv')

        else:
            data_processor = DataProcessManager(sys.argv[1], sys.argv[2])

        data_processor.process()

