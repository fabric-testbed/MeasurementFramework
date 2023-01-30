#!/usr/bin/python3
import os
from pathlib import Path
def get_ptp_device_name():
    result=os.popen("ps -ef |grep phc2sys").read()
    start="-s"
    end=" -c CLOCK_REALTIME"
    if (end in result):
        sindex= result.rfind(start)
        eindex= result.rfind(end)
        device = result[sindex+3:eindex].strip() 
        output_dir= Path("/home/mfuser/services/timestamp/timestamp_output/")
        output_dir.mkdir(parents=True)
        output_file= os.path.join(output_dir,"ptp_clock_name.txt")
        with open(output_file, "w") as f:
            f.write(device)
    else:
        sys.exit("Cannot find running ptp device")
        
if __name__ == "__main__":
    get_ptp_device_name()
            