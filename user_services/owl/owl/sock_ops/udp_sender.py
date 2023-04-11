import os
import sys
import socket
import time
import json
import argparse
from time_ops import ptp

#######
# Timer part:
# https://stackoverflow.com/questions/3393612/run-certain-code-every-n-seconds
# By https://github.com/MestreLion
#######

from threading import Timer

class UDP_sender(object):
    def __init__(self, interval, dst_ip, dst_port, start_num, 
                 ptp_so_file=None, sys_clock=False):
        
        if sys_clock:
            self.ptp_device = None
            print("Using system clock")
        else:
            self.ptp_device = self.find_ptp_device_name()
            self.ptp_so_file = ptp_so_file
            print("Using PTP device")

        self._timer     = None
        self.interval   = interval
        self.is_running = False

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Internet, UDP
        self.dst_ip = dst_ip
        self.dst_port = dst_port
        self.seq_n = start_num
        
        self.start()


    def find_ptp_device_name(self):
        result=os.popen("sudo ps -ef |grep phc2sys").read()
        start="-s"
        end=" -c CLOCK_REALTIME"
        
        if (end in result):
            sindex= result.rfind(start)
            eindex= result.rfind(end)
            device = result[sindex+3:eindex].strip()   
            return (device)

        else:
            sys.exit("Cannot find running ptp device")


    def _run(self):
        self.is_running = False
        self.start()

        if not self.ptp_device:
            # Use Python system library
            current_timestamp = time.time_ns()/1000000000

        else: 
            # Get it directly from PTP device
            current_timestamp = ptp.get_ptp_timestamp(
                                device_name = self.ptp_device,
                                so_file=self.ptp_so_file)

        MESSAGE = f"{current_timestamp},{str(self.seq_n)}"
        self.sock.sendto(MESSAGE.encode(), (self.dst_ip, self.dst_port))
        self.seq_n = self.seq_n + 1


    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True


    def stop(self):
        self._timer.cancel()
        self.is_running = False
        self.sock.close()



if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("--dest-ip", type=str, default="10.10.1.1", 
                        help='destination IP')
    parser.add_argument("--dest-port", type=int, default=5005, 
                        help='destination port')
    parser.add_argument("--frequency", type=float, default=0.5,
                        help="second interval at which probe packet will be sent")
    parser.add_argument("--seq-n", type=int, default=1234,
                        help="initial sequence number")
    parser.add_argument("--duration", type=int, default=60,
                        help="number of seconds to run")
    parser.add_argument("--ptp-so-file", type=str, default="./time_ops/ptp_time.so", 
                        help='path to ptp_time.so file.')
    parser.add_argument("--sys-clock", action=argparse.BooleanOptionalAction,
                        help='uses Python time module (mostly for debugging)')

    args = parser.parse_args()
    
    send_interval = args.frequency
    dest_ip = args.dest_ip
    dest_port = args.dest_port
    seq_n = args.seq_n
    duration = args.duration
    ptp_so_file = args.ptp_so_file
    sys_clock = args.sys_clock

    owl_sender = UDP_sender(send_interval, dest_ip, dest_port, seq_n, 
                            ptp_so_file, sys_clock)
    try:
        time.sleep(duration) # function should run during this time
    finally:
        owl_sender.stop()



