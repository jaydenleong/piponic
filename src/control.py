
#----------------------------------------------Template--------------------------------------------------#
# This is a brief template on creating *new threading modules*
# 1. Create a class, for example: class ph_control(object):
# 2. Copy all the exiting initialization functions for sensors
# 3. Add the new initialization function for the new sensor/device
# 4. Set up the threading module at the end of this file, this includes:
# 4.1. Define your class, for example: VARIABLE_NAME = NAME_OF_THE_CLASS()
# 4.2. Create the thread module, for example: NAME_OF_THREAD = Thread(target = VARIABLE_NAME.FUNCTION_NAME) 
# Notice that the FUNCTION_NAME should be the function in the class (defined before), and is the one that you would like it to iterate
# 4.3. Start the thread, for example: NAME_OF_THREAD.start()




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
	self.x = 4.7
	self.desired_ph = 7

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


    def calibrate(self):
	x = read
	
 
    def test_ph(self):
        print('init start')
	print('the value of x is', end=' ')
	print(self.x)
        self.pH_sensor= AnalogIn(self.ads,ADS.P2)
        pH_voltage = self.pH_sensor.voltage
        pH = 4.7 +(pH_voltage-1.65)*(-3.3)		#test self.x here
        while True:
            time.sleep(2)
            print('loop start')
            self.pH_sensor= AnalogIn(self.ads,ADS.P2)
            pH_voltage = self.pH_sensor.voltage
            pH = 4.7 +(pH_voltage-1.65)*(-3.3)		#test self.x here
            if (pH<=8.2):				#test self.desired_ph here
                print('pump opened')
                GPIO.setup(26,GPIO.OUT)
                GPIO.output (26,GPIO.HIGH)
                time.sleep(2)
                GPIO.output (26,GPIO.LOW)
                time.sleep(2)

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
