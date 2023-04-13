from ctypes import *
class TIMESPEC(Structure):
    _fields_ = [
        ('tv_sec', c_long),
        ('tv_nsec', c_long)
    ]

def get_ptp_timestamp(device_name):
    func = CDLL("/home/mfuser/services/timestamp/service_files/get_ptp_time.so")
    func.get_ptp_time.restype = type(TIMESPEC())
    test=func.get_ptp_time(bytes(device_name, encoding='utf-8'))
    #timestamp_str= str(test.tv_sec)+"."+str(test.tv_nsec)
    timestamp_str=f"{test.tv_sec}.{test.tv_nsec:09}"
    return (timestamp_str)



if __name__ == "__main__":
    # Input your ptp device name e.g, "/dev/ptp2"
    print ("clock time is "+get_ptp_timestamp("/dev/ptp2"))

