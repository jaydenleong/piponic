import src.adc as a

sen = a.adc_sensors()
pH = sen.read_pH_ex()
print(pH)
