#################
## To use this file, run the following command first
## $ cc -fPIC -shared -o ptp_time.so ptp_time.c
##
## Usage:
##   python3 ptp.py <device path>
##
##(to get the device name with "ps -ef | grep phc2sys")
################

import sys
from ctypes import *

class TIMESPEC(Structure):
    _fields_ = [
        ('tv_sec', c_long),
        ('tv_nsec', c_long)
    ]

def get_ptp_timestamp(device_name="/dev/ptp1", so_file="./ptp_time.so"):
    func = CDLL(so_file)
    func.get_ptp_time.restype = type(TIMESPEC())
    test=func.get_ptp_time(bytes(device_name, encoding='utf-8'))
    timestamp_str=f"{test.tv_sec}.{test.tv_nsec:09}"
    return timestamp_str



if __name__ == "__main__":

    if len(sys.argv) != 3:
        print("Usage: python3 pyp.py '<device path>' '<so_file_path>'")
        exit(1)

    else: 
         print(get_ptp_timestamp(device_name=sys.argv[1], so_file=sys.argv[2]))
