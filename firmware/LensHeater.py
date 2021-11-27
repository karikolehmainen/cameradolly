
import time
from Configuration import *
from MessageBroker import *
from Adafruit_MotorHAT import Adafruit_MotorHAT, Adafruit_StepperMotor


class LensHeater:
	def __init__(self, motorhat,config):
		self.pwmFreq = 10
		self.pwm = 50
		self.mh = motorhat
		self.config = config
		self.running = 0
	
	def setMessageBroker(self,messagebroker):
		self.mBroker = messagebroker
	
	def worker(self):
		counter = 0
		while True:
			if (self.running == 1):
				time.sleep(1/self.pwmFreq)
				counter = counter+1
				if (counter < self.pwm):
					self.mh.setPin(0,1)
				else:
					self.mh.setPin(0,0)
				if (counter > 100):
					counter = 0
			else:
				self.mh.setPin(0,0)

	def setPWM(self,count):
		self.pwm = count
	
	def setOn(self):
		self.running = 1
	
	def setOff(self):
		self.running = 0

	def setPwmFreq(self,freq):
		self.pwmFreq = freq

	def getPWM(self):
		return self.pwm
	def getPwmFreq(self):
		return self.pwmFreq
