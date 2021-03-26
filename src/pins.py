#This file stores the GPIO pin values as constants for human and machine reference
RELAY1 = 26
peristaltic_pump = RELAY1

RELAY2 = 19
Water_level_solenoid = RELAY2

RELAY3 = 13
RELAY4 = 6

I2C_SDA = 2
I2C_SCL = 3

TEMP = 4
WATER_LEVEL = 17

# TODO(JAYDEN): move this to better location
DEFAULT_DEVICE_CONFIG = {
  'max_ph': 10,
  'min_ph': 5,
  'max_temperature': 25,
  'min_temperature': 15,
  'peristaltic_pump_on': False,
  'target_ph': 7,
  'update_interval_minutes': 30,
  'low_battery_volts' : 1,
  'leak_threshold' : 0.25,
};


#ADC0 PINS
#P0 Outer Leak detector
#P1 pH sensor
#P2 Battery voltage
#P3 Enclosure Leak detector

#ADC1 Pins
#P0 (Currently unused)
#P1         ''
#P2         ''
#P3         ''


