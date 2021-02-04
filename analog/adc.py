'''

Python script to read analog voltage values from ADS1115 16bit ADC with PGA
Author: Carson Berry 
Date: February 2nd, 2021


usage: 
    python3 adc.read_leak()

Reference provided at: https://learn.adafruit.com/adafruit-4-channel-adc-breakouts/python-circuitpython

'''

import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

def init_i2c():
   #define i2c object
    i2c = busio.I2C(board.SCL, board.SDA)
    #create object
    ads = ADS.ADS1115(i2c) 
    return ads

def init_leak():
    ads = init_i2c()
    #single channel read
    chan = AnalogIn(ads,ADS.P0)
    return chan

def init_pH():
    ads = init_i2c()
    chan= AnalogIn(ads,ADS.P1)
    return chan


def read_leak():
    chan = init_leak()
    print(chan.value, chan.voltage)
    return chan.voltage

def read_pH();
    chan = init_pH()
    print(chan.value, chan.voltage)
    return chan.voltage

