import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from threading import Thread
import RPi.GPIO as GPIO
import time
import src.pins



class ph_control(object):
    def __init__(self):
        self.ads=0
        self.init_i2c()
        self.leak_sensor = 0
        self.init_leak()
        self.pH_sensor = 0
        self.init_pH()

    def init_i2c(self):
        #define i2c object
        i2c = busio.I2C(board.SCL, board.SDA)
        #create object
        self.ads = ADS.ADS1115(i2c) 

    def init_leak(self):
        self.leak_sensor= AnalogIn(self.ads,ADS.P0)
         
    def init_ph(self):
        self.pH_sensor= AnalogIn(self.ads,ADS.P2)

    def init_pH(self):
        self.pH_sensor= AnalogIn(self.ads,ADS.P2)
       
    def read_leak(self):
        return self.leak_sensor.voltage

    def read_pH(self):
        pH_voltage = self.pH_sensor.voltage
        pH = 7.7 +(pH_voltage-1.65)*(-3.3)
        return pH

    def read_ph(self):
        pH_voltage = self.pH_sensor.voltage
        pH = 7.7 +(pH_voltage-1.65)*(-3.3)
        return pH
	
 
    def test_ph(self):
        print('init start')
        self.pH_sensor= AnalogIn(self.ads,ADS.P2)
        pH_voltage = self.pH_sensor.voltage
        pH = 4.7 +(pH_voltage-1.65)*(-3.3)
        while True:
            time.sleep(5)
            print('loop start')
            self.pH_sensor= AnalogIn(self.ads,ADS.P2)
            pH_voltage = self.pH_sensor.voltage
            pH = 4.7 +(pH_voltage-1.65)*(-3.3)
            if (pH<=8.2):
                print('pump opened')
                GPIO.setup(26,GPIO.OUT)
                GPIO.output (26,GPIO.HIGH)
                time.sleep(5)
                GPIO.output (26,GPIO.LOW)
                time.sleep(5)

class wl_control(object):
    def __init__(self):
        self.ads=0
        self.init_i2c()
        self.leak_sensor = 0
        self.init_leak()
        self.pH_sensor = 0
        self.init_pH()

    def init_i2c(self):
        #define i2c object
        i2c = busio.I2C(board.SCL, board.SDA)
        #create object
        self.ads = ADS.ADS1115(i2c) 

    def init_leak(self):
        self.leak_sensor= AnalogIn(self.ads,ADS.P0)
         
    def init_ph(self):
        self.pH_sensor= AnalogIn(self.ads,ADS.P1)

    def init_pH(self):
        self.pH_sensor= AnalogIn(self.ads,ADS.P1)
       
    def read_leak(self):
        return self.leak_sensor.voltage

    def read_pH(self):
        pH_voltage = self.pH_sensor.voltage
        pH = 7.7 +(pH_voltage-1.65)*(-3.3)
        return pH

    def read_ph(self):
        pH_voltage = self.pH_sensor.voltage
        pH = 7.7 +(pH_voltage-1.65)*(-3.3)
        return pH
		
    def test_wl(self):
        while True:
            #print('valve opened')
            time.sleep(6)
		
		
#Create Class
First = wl_control()
FirstThread=Thread(target=First.test_wl)
FirstThread.start()

#Create Class
Second = ph_control()
SecondThread=Thread(target=Second.test_ph)
SecondThread.start()
