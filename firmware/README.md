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

## MQTT Message Format ##
MQTT communication is migrating away from payload messages that were format <command>-<value>. Now commands are set with MQTT topics in format:
  /CameraDolly/<sub_topic> 
possible value is given in payload. For instace rotating camera head with specific angular speed can be given with following MQTT message:
  mosquitto_pub -h localhost -p 1883 -u cdolly -P dolly -t "CameraDolly/rotate" -m "0.004125296125"
Angular speed is given as degrees in second. Above command matches head rotation speed with earth angular speed

- "start": Start Dolly opration
- "stop": Stop Dolly operation

### /CameraDolly/rotate ###
Rotates camera head with anglural speed defined in the message body. Unit is degrees per second

### /CameraDolly/start ###
  Starts dolly operation. No parameters necessary
  
### /CameraDolly/stop ###
  Stops dolly opration. No parameters necessary
  
### /CameraDolly/gotostart ###
  Moves dolly to the begining of the track. No parameters necessary

### /CameraDolly/gotoend ###
  Moves dolly to the end of the track. No parameters necessary

### /CameraDolly/level_horizon ###
  Level Camera head with horizon. Seeks position so that accelerometer is level with horizon. No paramters necessary
  
### /CameraDolly/head_off ###
  Turns camera head off. This is reduntant with stop message but left here for possible case that only head would be turned off. No parameters necessary.

### /CameraDolly/measure_track ###
  Measure track by moving dolly from start to end and back. No parameters necessary.
  
### Getters ###
- "cammodel": Retrieve Camera Model
- "camsettinglists": Return camera settings
- "getstepsize": Return dolly step size
- "getstepcount": Get number of steps so far
- "getmode": Return dolly operation mode
- "gettracking": Get tracking info
- "getimagenumber": return image numeber counter
- "getinterval": return image interval
- "getposition": transmit dolly position message
- "getheatsetting": return lens heater setting
### Setters ###
- "setheat (int)": set lens heater to °C temp 
- "setmode (int)": set dolly to operation mode enumeration
- "settargetx (double)": set tracing tarket X coordinate to x meters from rail start
- "settargety (double)": set tracing tarket Y coordinate to x meters perpenticular from rail
- "setstepdistance (int)": define distance on the rail between images in millimeters
- "setanglestep (float)": define angular distance of camerarotation between images
- "setdeclination (float)": define declination 
- "setcomperr (float)": set compass error
- "setimagenumber (int)": define how many images to take
- "interval (float)": define seconds between images
- "rotateccw": rotate head to counter clockwise direction
- "rotatecw": rotate head to clockwise direction
- "rcamsettings": trasmitt camera settings
- "get_head_angle": return camera head tilt angle
- "align_axis": align camera head with earth axis

