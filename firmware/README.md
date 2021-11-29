# Instructions #

## Installation ##
TDB

## Interfaces ##

LMS303DHC Magnetometer / accelerometer in I2C bus 
- accelerometer address 0x24 
- magnetometer address 0x30

PCA9685 PWM interface for motoro contol in I2C bus
- address 0x60

ADS1115 ADC converter for battery measurement / temeperature sensor reading
- address 0x48

Head rotation sensor (gray code generator) on GPIO04 and GPIO18

Track rotation sensor (gray code generator) on GPIO13 and GPIO19

Endstop sensors (buttons) on GPIO20 and GPIO26

In ADC there are three channels of four in use
- Channel 0 input from current meter
- Channel 1 input from voltage divider for battery V
- Channel 3 input from lens temperature sensor 3.3/NTC


