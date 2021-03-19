
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
#-----------------------------------------------CODE COMPLETE---------------------------------------------#
# class ph_control(object):
# VARIABLE_NAME = NAME_OF_THE_CLASS()
# NAME_OF_THREAD = Thread(target = VARIABLE_NAME.FUNCTION_NAME) 
# NAME_OF_THREAD.start()




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

        self.pH_sensor = 0
        self.init_pH()
        self.pH_intercept = 7
        self.pH_offset = 1.65
        self.pH_slope = -3.3
	    self.desired_ph = 7

    def init_i2c(self):
        #define i2c object
        i2c = busio.I2C(board.SCL, board.SDA)
        #create object
        self.ads = ADS.ADS1115(i2c) 

    def init_ph(self):
        self.pH_sensor= AnalogIn(self.ads,ADS.P2)

    def init_pH(self):
        self.pH_sensor= AnalogIn(self.ads,ADS.P2)
       
    def read_pH(self):
        pH_voltage = self.pH_sensor.voltage
        pH = self.pH_intercept +(pH_voltage-self.pH_offset)*(self.pH_slope)
        return pH

    def read_ph(self):
        pH_voltage = self.pH_sensor.voltage
        pH = self.pH_intercept +(pH_voltage-self.pH_offset)*(self.pH_slope)
        return pH

    # Calibration function
    # Intended to assist with the calibration of the pH_probe at regular (eg. monthly) intervals 
    #
    # REQUIRES USER ENGAGEMENT - THEY MUST CHANGE THE pH PROBE SOLUTION WHEN PROMPTED
    # total process will take about 3 minutes.  
    #
    #  inputs: self, pH of calibration solution 1 (eg 7), pH of calibration solution 2 (eg. 4)
    # updates: self.pH_slope, self.pH_intercept
    #use: ph_control.calibrate(self,7,4)
    def calibrate(self, calibration_pH_1, calibration_pH_2):
        #this function constructs a linear function of the form: 
        # y = m(x-offset)+b
        # or 
        # pH = (slope)*(voltage-offset_voltage)+ pH_at_offset_voltage
         
        print('Please place the pH probe in the first solution with pH ',calibration_pH_1,', and mix the solution with the probe. Wait 60 seconds.')
         #should we wait for confirmation? From testing, 1 minute is not enough          
        for _ in range(60):
            time.sleep(1)
            print('.')
        print('Reading now')   
        v1 = self.pH_sensor.voltage # read the pH meter's voltage in the known solution

        print('Please place the pH probe in the second solution with pH ',calibration_pH_2,', and mix the solution with the probe. Wait 60 seconds.')
         #should we wait for confirmation? From testing, 1 minute is not enough
        for _ in range(60):
            time.sleep(1)
            print('.')
        print('Reading now')   
        v2 = self.pH_sensor.voltage # read the pH meter's voltage in the known solution
        
        #calculate slope of pH-voltage curve (should be negative)
        self.pH_slope = (calibration_pH_1-calibration_pH_2)/(v1-v2)

        #pH curve 'intercept' anchored around first datapoint
        self.pH_intercept = calibration_pH_1
        self.pH_offset = v1



            
	
 
    def test_ph(self):
        print('init start')
	print('the value of x is', end=' ')
	print(self.x)
        self.pH_sensor= AnalogIn(self.ads,ADS.P2)
        pH_voltage = self.pH_sensor.voltage
        pH = self.pH_offset + (pH_voltage-1.65)*(self.pH_slope)		#test self.x here
        while True:
            time.sleep(2)
            print('loop start')
            self.pH_sensor= AnalogIn(self.ads,ADS.P2)
            pH = self.read_pH()
            if (pH<=self.desired_pH):			#test self.desired_ph here
                print('pump opened')
                GPIO.setup(26,GPIO.OUT)
                GPIO.output (26,GPIO.HIGH)
                time.sleep(2)
                GPIO.output (26,GPIO.LOW)
                time.sleep(2)

class wl_control(object):				#It turns out to be a bug when there's no (object)
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
