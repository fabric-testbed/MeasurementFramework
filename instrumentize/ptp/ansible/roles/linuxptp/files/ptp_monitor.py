#!/usr/bin/env python3

import sys
import time
import subprocess
import logging
from logging.handlers import RotatingFileHandler

def go_to_sleep(sleep = 0,msg=''):
    logging.info("Polling again in %s seconds %s ..." % (str(sleep),msg))
    time.sleep(sleep)
    return True


def getPTPServerIP(ptp4l_config = '/etc/linuxptp/ptp4l.conf'):
    with open(ptp4l_config, "r") as fp:
        for line in fp:
            if line.startswith('UDPv4'):
                return line.split()[1]

def restartPTP4L():
    logging.info("Trying to restart ptp4l daemon....")
    import dbus
    sysbus = dbus.SystemBus()
    systemd1 = sysbus.get_object('org.freedesktop.systemd1', '/org/freedesktop/systemd1')
    manager = dbus.Interface(systemd1, 'org.freedesktop.systemd1.Manager')
    job = manager.RestartUnit('ptp4l.service', 'fail')
    go_to_sleep(sleep = 60)
 
    return True

def isUp(time_server):
    import os
    response = subprocess.run(['/sbin/ping','-c','1',time_server])

    #and then check the response...
    if response.returncode == 0:
        logging.debug("Success pinging %s" % (time_server))
        return True
    else:
        logging.debug("UnSuccessfull pinging %s . ERROR CODE: %d" % (time_server,response.returncode))
        return False

def getIngressTime():
    # Return states 
    # 0 if ingress time returned is 0 (if no sync messages from PTP server or PTP server may have rebooted)
    # -1 if ptp4l on the local machine is not running . Monitoring should detect this
    # 1 if system is syncing with PTP time 

    p = subprocess.run(['/sbin/pmc','-u','-b','0','GET TIME_STATUS_NP'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        ingress_time = int(p.stdout.decode('utf-8').split('\n')[3].rsplit(" ",1)[1])
        if (ingress_time > 0):
            return 1
        else:
            return 0
    except IndexError as error:
        return -1
    except Exception as exception:
        return -1

def main():

    TIME_SERVER = getPTPServerIP()
    MAX_LOG_SIZE = 20000000
    LOG_FILENAME = '/var/log/ptp4l-monitor.log'

    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S',level=logging.DEBUG,handlers=[RotatingFileHandler(LOG_FILENAME, maxBytes=MAX_LOG_SIZE,backupCount=5,mode='a')])
    logging.info("Starting PTP4L Monitor...") 
    go_to_sleep(sleep = 15,msg='to initiate a slow start') #Slow start due to systemd dependencies
    while True:
        # Check ingressTime every 60 seconds
        ptp4l_status = getIngressTime()
        if (ptp4l_status != 1 ):
            logging.debug("PTP4L Monitor Status = %d" % (ptp4l_status)) 
        if (ptp4l_status == 0 ):
            logging.info("Time Server %s may have just rebooted..." % (TIME_SERVER))
            if(isUp(TIME_SERVER)):
                logging.info("Time Server %s is responsive to ping..." % (TIME_SERVER))
                go_to_sleep(sleep = 120,msg="to let things settle down") # Wait for 2 minutes
                restartPTP4L()
            else:
                logging.info("Time Server %s is still offline..." % (TIME_SERVER))
        elif(ptp4l_status == -1):
                logging.info("PTP4l Daemon Possibly stopped....")
                logging.info("PTP4L Monitor trying to restart PTP4L Daemon....")
                restartPTP4L()
        go_to_sleep(sleep = 60)

if __name__ == "__main__":
    main()
