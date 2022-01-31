import subprocess
import time
import os
import signal

# This script must be run as root


class TcpdumpOps:
    def __init__(self, port, interval):
        self.cmd = f"tcpdump -vfn -XX -tt  -i any --direction in port {str(port)} \
                    -w data/%s.pcap -G {str(interval)}"

    def start(self):
        self.p = subprocess.Popen(self.cmd.split(), stdout=subprocess.PIPE)
        print("Pid: ", self.p.pid)

    def stop(self):
        self.p.terminate()


if __name__ == "__main__":

    port = 5005
    interval_pcap = 10

    session = TcpdumpOps(port, interval_pcap)
    session.start()
    time.sleep(30)
    session.stop()

