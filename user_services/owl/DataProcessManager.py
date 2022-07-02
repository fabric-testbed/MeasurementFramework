from data_ops import read_pcap as pcap_reader
import glob
import sys
import os

class DataProcessManager:
    def __init__(self, dir_path, outfile, delete_pcap=False, verbose=True):

        self.data_dir = dir_path
        self.pcapfiles = glob.glob(f'{self.data_dir}/*.pcap')
        self.outfile = f'{self.data_dir}/{outfile}'
        self.delete_pcap = delete_pcap
        self.verbose = verbose


    def process(self):
        # Remove zero-bye pcap files
        pcapfiles_with_data = [f for f in self.pcapfiles if os.stat(f).st_size > 0]
        print("non-zero pcap files to be processed: ", pcapfiles_with_data)

        processor = pcap_reader.PcapProcessor(
                            pcapfiles_with_data, 
                            self.outfile, 
                            self.delete_pcap, 
                            self.verbose)
        processor.process()


    def delete_csv_files(self):
        csv_files = glob.glob(f'{self.data_dir}/*.csv')
        
        for csv_f in csv_files:
            try:
                os.remove(csv_f)
                print("Removed File: ", csv-f)
            except:
                print("Error while deleting file: ", csv_f)


    def delete_pcap_files(self):
        
        for pcap_f in self.pcapfiles:
            try:
                os.remove(pcap_f)
                print("Removed File: ". pcap_f)
            except:
                print("Error while deleting file: ", pcap_f)

if __name__ == "__main__":
    '''
    Args:
        [1] action (required): 'process' | 'delete_csv' | 'delete_pcap'
        [2] directory path (required)
        [3] output ccsv file name (optional)
    '''

    if len(sys.argv) < 3:
        print("Error: needs action +  directory path")
        exit(1)
    
    elif len(sys.argv) == 4:
        outfile = sys.argv[3]

    else:
        outfile = 'out.csv'

    # Create an instance
    data_processor = DataProcessManager(sys.argv[2], outfile)

    # Action!
    if sys.argv[1] == 'process':
        data_processor.process()

    elif sys.argv[1] == 'delete_csv':
        data_processor.delete_csv_files()

    elif sys.argv[1] == 'delete_pcap':
        data_processor.delete_pcap_files()

    else:
        print("Error: no such action")
        exit(1)

    
