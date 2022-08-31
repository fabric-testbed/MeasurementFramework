import socket
import time
import json

#######
# Timer part:
# https://stackoverflow.com/questions/3393612/run-certain-code-every-n-seconds
# By https://github.com/MestreLion
#######

from threading import Timer

class UDP_sender(object):
    def __init__(self, interval, dst_ip, dst_port, start_num):
        self._timer     = None
        self.interval   = interval
        self.is_running = False

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Internet, UDP
        self.dst_ip = dst_ip
        self.dst_port = dst_port
        self.seq_n = start_num
        
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        
        MESSAGE = f"{(time.time()):.9f},{str(self.seq_n)}"
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
    
    DEST_IP = "10.10.2.1"
    DEST_PORT = 5005
    SEND_INTERVAL = 0.5
    Seq_n = 1000
    Run_time = 10

    rt = UDP_sender(SEND_INTERVAL, DEST_IP, DEST_PORT, Seq_n)
    try:
        time.sleep(Run_time) # function should run during this time
    finally:
        rt.stop()



