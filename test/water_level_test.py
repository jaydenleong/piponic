


import src.water_level as WL


water_level_sensor = WL.water_level()

water_level = water_level_sensor.read()

print('Water Level (binary):',water_level)
