'''
file: temp.py
author: Carson Berry <carsonberry@hotmail.ca>
Date: January 30th, 2021

Purpose: To read data from the one-wire interface of the DS18B20 temperature sensor on teh raspberry pi. 
This file is designed to be used in a obj oriented way, such as temp.read()

inputs: null
outputs: float temp

Usage:
import temp
python temp.read()
'''

import os 
import glob
import time



#name of specific temperature sensor in given system. Should try and automate this process. 
#temp_sensor = '/sys/bus/w1/devices/28-3c01b556d3de/w1_slave'

#Read from the file where the temperature information is stored for this device.
def temp_raw():
    try: 
        os.system('modprobe w1-gpio')
        os.system('modprobe w1-therm')
        temp_dir = '/sys/bus/w1/devices/28-*/w1_slave'
        temp_sensor = glob.glob(temp_dir)
    except:
        print('Wrong Temperature Device ID')
    f = open(temp_sensor[0], 'r')
    lines = f.readlines()
    f.close()
    return lines


def read():
    try:
        lines = temp_raw()
        #Wait for successful read from temperature sensor (denoted by YES) at the end of this file.
        while lines[0].strip()[-3:] != 'YES': 
            time.sleep(0.2) #try again in 200 ms if not successful
            lines = temp_raw()
        temp_output = lines[1].find('t=')
        if temp_output != -1:
            temp_string = lines[1].strip()[temp_output+2:]
            temp_c = float(temp_string)/1000.0
            temp_f = temp_c*9.0/5.0+32.0
            return temp_c #, temp_f
    except:
        print('Temperature sensor error! Check Wiring or device ID is correct')
        return -1


