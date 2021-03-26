
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
import src.pins as pins
import src.relay as relay
import src.water_level as water_level



class pH_control(object):
    def __init__(self):
        self.ads=0
        self.init_i2c()

        self.pH_sensor = 0
        self.init_pH()
        self.pH_intercept = 7
        self.pH_offset = 1.65
        self.pH_slope = -3.3
        self.desired_pH = 7
        
        self.relay_pullup = 1 # sets the mode of the pins that connect to the relay. If your relay is active low, you want to be in Pull-up mode, otherwise pull-down mode. 

    def init_i2c(self):
        #define i2c object
        i2c = busio.I2C(board.SCL, board.SDA)
        #create object
        self.ads = ADS.ADS1115(i2c) 

    def init_ph(self):
        self.pH_sensor= AnalogIn(self.ads,ADS.P1)

    def init_pH(self):
        self.pH_sensor= AnalogIn(self.ads,ADS.P1)
       
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
    def calibrate1(self, calibration_pH_1):
        #this function constructs a linear function of the form: 
        # y = m(x-offset)+b
        # or 
        # pH = (slope)*(voltage-offset_voltage)+ pH_at_offset_voltage
         
        print('Please place the pH probe in the first solution with pH ',calibration_pH_1,', and mix the solution with the probe. Wait 60 seconds.')
         #Wait for 2 minutes         
        for _ in range(120):
            time.sleep(1)
            print('.')
        print('Reading now')   
        # set the pH_offset to be the middle of the 
        self.pH_offset = self.pH_sensor.voltage # read the pH meter's voltage in the known solution 1

    def calibrate2 (self, calibration_pH_1, calibration_pH_2):
        print('Please place the pH probe in the second solution with pH ',calibration_pH_2,', and mix the solution with the probe. Wait 60 seconds.')
         #Wait for 2 minutes
        for _ in range(120):
            time.sleep(1)
            print('.')
        print('Reading now')   

        v2 = self.pH_sensor.voltage # read the pH meter's voltage in the known solution 2
        
        #calculate slope of pH-voltage curve (should be negative)
        self.pH_slope = (calibration_pH_1-calibration_pH_2)/(self.pH_offset-v2)

        #pH curve 'intercept' anchored around first datapoint
        self.pH_intercept = calibration_pH_1



    #Control loop where pH is checked and if it is too low, pH-increasing solution (KOH, or CaOH) is added
    def pH_control_loop(self):
        print('pH control loop initialization start')
        pH = self.read_pH()
        #initialize relay pins
        if(self.relay_pullup):
            relay.init_pullup(pins.peristaltic_pump)
        else:  
            relay.init(pins.peristaltic_pump)

        # start of loop    
        while True:
            time.sleep(2)
            print('pH control loop start')

            pH = self.read_pH()
            if (pH<=self.desired_pH):	# desired_pH should be set as the minimum value you want your pH to be at.
                print('Peristalitic Pump started')
                # Turn on peristaltic pump for 2 seconds
                relay.on(pins.peristaltic_pump)
                time.sleep(2)

                relay.off(pins.peristaltic_pump)
                time.sleep(2)



class wl_control(water_level.water_level):				
    def __init__(self):
        self.relay_pullup = 1
        super().__init__(self) #init water_level sensor class

         
    def read_level(self):
        return super().read()

    def water_level_control_loop(self):
        if(self.relay_pullup):
            relay.init_pullup(pins.Water_level_solenoid)
        else:  
            relay.init(pins.Water_level_solenoid)
        while True:

            #TODO: double check Benny's water-level control algorithm recommendations

            #if the water level is low, turn on solenoid for 2 seconds
            if(self.read_level==0):
                relay.on_pu(pins.Water_level_solenoid)
                time.sleep(2)

                relay.off_pu(pins.Water_level_solenoid)
                time.sleep(2)
            
            
            #print('valve opened')
            time.sleep(6)
		
		
#Create Class
First = wl_control()
FirstThread=Thread(target=First.water_level_control_loop)
FirstThread.start()

#Create Class
Second = pH_control()
SecondThread=Thread(target=Second.pH_control_loop)
SecondThread.start()
