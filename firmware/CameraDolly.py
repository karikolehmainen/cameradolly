from __future__ import print_function
import os
import subprocess
import sys
import time
import atexit
import threading
import random
from Configuration import *
from Camera import *
from Dolly import *
from MessageBroker import *
from LensHeater import *

threads = []
stepcount = 0
numsteps = 0
counter = 0
I2CBUS = 1
# create empty threads (these will hold the stepper 1 and 2 threads)
st1 = threading.Thread()

mh = Adafruit_MotorHAT(addr=0x60,i2c_bus=I2CBUS,freq=3200)
#atexit.register(turnOffMotors)

def initiateThreads(datatrans,lensheater,configuration,dolly):
	t1 = threading.Thread(target=datatrans.worker)
	threads.append(t1)
	t1.start()

	t2 = threading.Thread(target=lensheater.worker)
	threads.append(t2)
	t2.start()

	t3 = threading.Thread(target=dolly.worker)
	threads.append(t3)
	t3.start()

	t4 = threading.Thread(target=dolly.getHead().worker)
	threads.append(t4)
	t4.start()

	print("started threads")

def getStepCount():
	return stepcount

def getCounter():
	return counter

def main():
	global stepcount
	global numsteps
	global counter
	conf = Configuration()
	conf.readConfiguration()

	images = conf.getDefaultImages()
			
	cam = Camera(conf)
	if (conf.isSimulation() == 0):
		cam.initCamera()

	dolly = Dolly(conf,mh)
	lensHeater = LensHeater(mh,conf)

	mBroker = MessageBroker(conf,cam,dolly,lensHeater)
	mBroker.connect()
	cam.setMessageBroker(mBroker)
	cam.setImageNumber(images)
	lensHeater.setMessageBroker(mBroker)
	initiateThreads(mBroker,lensHeater,conf,dolly)
	ts = time.time()
	stabbuffer = conf.getStabisationBuffer()
	print("main: going in the foreverloop (images="+str(images)+")")
	while (1):
		temperature = dolly.getTemp()
		voltage = dolly.getVoltage()
		current = dolly.getCurrent()
		power = int((voltage*current)/100000)/10.0
		#print("main: ADC values: temp: " + str(temperature) + ", power: " + str(power) + "W Voltage: "+str(int(voltage/100)/10.0)+"V")
		if (counter < cam.getImageNumber() and dolly.isRunning() == 1):
			print("main: Dolly running interval "+str((time.time()-(ts+dolly.getInterval()-stabbuffer))))
			counter = counter + 1
			# wait until enough time has passed since last photo. 
			while (time.time()<(ts+dolly.getInterval()-stabbuffer)):
				time.sleep(0.1)
			ts = time.time()
			# Move dolly
			dolly.moveDolly()
			# Wait for awhile
			time.sleep(stabbuffer)
			# Capture image
			cam.takePicture()
			mBroker.transmitPositionMessage(dolly.getPositionMM(), dolly.getAngleDeg(), counter, dolly.getHeading(), dolly.getTilt(),temperature,int(voltage/100)/10.0,power)
			statusMsq = "running"
			lensHeater.setOn();
			mBroker.transmitdata(statusMsq, conf.getTopic()+"StatusMessage")

		else:
			statusMsq = "{\"heading\":"+str(dolly.head.getHeadingDeg())+",\"running\":"+str(dolly.isRunning())+",\"position\":"+str(dolly.getPositionMM())+"}"
			mBroker.transmitdata(statusMsq, conf.getTopic()+"StatusMessage")
			lensHeater.setOff();
			counter = 0
			time.sleep(1)
	dolly.quit()
	print("main: exiting the foreverloop")
	return 0

if __name__ == "__main__":
	sys.exit(main())
