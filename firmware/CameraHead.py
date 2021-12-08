import time
from datetime import datetime
import math
from encoder import Encoder
from Configuration import *
from MessageBroker import *
from Adafruit_MotorHAT import *
import RPi.GPIO as GPIO
#from LIS3DH import LIS3DH
from LSM303 import *
from LSM303 import *

class CameraHead:
	ROTATETOLERANCE = 0.05
	enc1 = 4
	enc2 = 18
	defaultspeed = 255
	def __init__(self, motorhat,config):
		self.mh = motorhat
		#self.IMU = LIS3DH(debug=True)
		#self.IMU.setRange(LIS3DH.RANGE_2G)
		self.IMU = LSM303()
		self.mh = motorhat
		self.tiltMotor = self.mh.getMotor(1)      # Head Tilt motor
		self.tiltMotor.setSpeed(255)
		self.rotateMotor = self.mh.getMotor(4)      #  Head Motor on channel 4
		self.rotateMotor.setSpeed(self.defaultspeed)
		#self.levelMargin = 0.0174533 # 1° in radians
		self.levelMargin = 0.00436333 # 0.5° in radians
		self.alignMargin = 0.00872665 # 0.5°
		#Rotation speed sensor
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self.enc1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		GPIO.setup(self.enc2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		GPIO.add_event_detect(self.enc1,   GPIO.FALLING, callback=self.testCallback, bouncetime=300)
		#self.enc = Encoder(4,18, callback=self.encCallback)
		self.targetTicktime = 0
		self.loopinterval = 2
		self.speed=196
		self.running = False
		self.lastTick = self.timestamp()
		self.lastEncTick = self.lastTick
		# inlined encoder code
		self.state = '00'
		self.enc_direction = None 

	def testCallback(self,channel):
		print("testCallback")
		p1 = GPIO.input(self.enc1)
		p2 = GPIO.input(self.enc2)
		newState = "{}{}".format(p1, p2)
		ts = self.timestamp()
		delta = ts-self.lastEncTick
		self.lastEncTick = ts
		#print("Encoder.transitionOccurred: " + str(newState) + " old state: " + self.state + " delta:" + str(delta))
		if self.state == "00": # Resting position
			if newState == "01": # Turned right 1
				self.enc_direction = "R"
				self.encCallback(0) #
			elif newState == "10": # Turned left 1
				self.enc_direction = "L"
				self.encCallback(0) #
		elif self.state == "01": # R1 or L3 position
			if newState == "11": # Turned right 1
				self.enc_direction = "R"
				self.encCallback(0) #
			elif newState == "00": # Turned left 1
				if self.enc_direction == "L":
					self.encCallback(0)
		elif self.state == "10": # R3 or L1
			if newState == "11": # Turned left 1
				self.enc_direction = "L"
				self.encCallback(0) #
			elif newState == "00": # Turned right 1
				if self.enc_direction == "R":
					self.encCallback(0)
		else: # self.state == "11"
			if newState == "01": # Turned left 1
				self.enc_direction = "L"
				self.encCallback(0) #
			elif newState == "10": # Turned right 1
				self.enc_direction = "R"
				self.encCallback(0) #
			elif newState == "00": # Skipped an intermediate 01 or 10 state, but if we know direction then a turn is complete
				if self.enc_direction == "L":
					self.encCallback(0)
				elif self.direction == "R":
					self.encCallback(0)
		self.state = newState

	def encCallback(self,value):
		#print("encoderCallback")
		ts = self.timestamp()
		#self.direction = value-self.lastvalue
		#self.lastvalue = value
		print("HEAD.encCallback: value: "+str(value)+" direction: "+str(self.direction))
		if (self.lastTick != 0):
			delta = ts-self.lastTick
			self.adjustSpeed(delta)
			print("HEAD.encCallback: delta: " + str(delta))
		self.lastTick = ts

	def adjustSpeed(self,delta):
		diff = self.targetTicktime - delta
		# this speed is likey to be bogus
		if (abs(delta)<0.7):
			return
		if (diff > self.ROTATETOLERANCE):
			self.speed = self.speed - 10
		elif (diff < self.ROTATETOLERANCE):
			self.speed = self.speed + 10

		print("HEAD.adjustSpeed: "+str(diff)+" new speed: "+str(self.speed))
		self.rotateMotor.setSpeed(int(self.speed))
		self.rotateMotor.run(self.direction)

	def setMessageBroker(self,messagebroker):
		self.mBroker = messagebroker

	def getHeading(self):
		accel, mag = self.IMU.read()
		accel_x, accel_y, accel_z = accel
		mag_x, mag_y, mag_z = mag
		#print('Accel X={0}, Accel Y={1}, Accel Z={2}, Mag X={3}, Mag Y={4}, Mag Z={5}'.format(accel_x, accel_y, accel_z, mag_x, mag_y, mag_z))
		compassHeadin = 0
		if (mag_x != 0):
			compassHeadin = math.atan(mag_y/mag_x)
		return compassHeadin
		#return 0 # Got only accelerometer...

	def getTilt(self):
		#accel, mag = self.lsm303.read()
		#accel_x, accel_y, accel_z = accel
		#mag_x, mag_y, mag_z = mag
		#print('Accel X={0}, Accel Y={1}, Accel Z={2}, Mag X={3}, Mag Y={4}, Mag Z={5}'.format(accel_x, accel_y, accel_z, mag_x, mag_y, mag_z))
		(accel,mag) = self.IMU.read()
		#print(accel)
		#print(mag)
		accel_x = accel[0]
		accel_z = accel[2]
		tilt = 0
		if (accel_z != 0):
			tilt = math.atan(accel_x/accel_z)
		return tilt

	def setDeclination(self,dec):
		self.declination = dec

	# rotate head with speed target given as degree / seconds
	def rotateHead(self,speed,dir=Adafruit_MotorHAT.FORWARD):
		print("CameraHead.rotateHead: "+str(speed))
		# convert speed to time target between tick
		self.targetSpeed = float(speed)
		# head has 1:90 and 1:30 reduction gears 
		self.targetTicktime = 30/(90*30*self.targetSpeed)
		self.direction = dir
		self.rotateMotor.setSpeed(int(self.speed))
		self.rotateMotor.run(self.direction)
		self.running = True
	
	def tiltHead(self,speed=255,dir=Adafruit_MotorHAT.FORWARD,delay=0.1):
		print("tiltHead"+str(speed))
		self.tiltMotor.setSpeed(speed)
		self.tiltMotor.run(dir)
		time.sleep(delay)
		self.tiltMotor.run(Adafruit_MotorHAT.RELEASE)
		time.sleep(delay*5)

	def rotateCW(self):
		self.rotateMotor.run(Adafruit_MotorHAT.FORWARD)
		time.sleep(self.rotateTick)
		self.rotateMotor.run(Adafruit_MotorHAT.RELEASE)
						 
	def rotateCCW(self):
		self.rotateMotor.run(Adafruit_MotorHAT.BACKWARD)
		time.sleep(self.rotateTick)
		self.rotateMotor.run(Adafruit_MotorHAT.RELEASE)
						 
	def headOff(self):
		self.rotateMotor.run(Adafruit_MotorHAT.RELEASE)
	def stop(self):
		self.headOff()

	def levelHeadHorizon(self):
		tilt = self.getTilt()
		count = 0
		while(math.fabs(tilt) > self.levelMargin and count < 15):
			print("levelHeadHorizon: "+str(math.fabs(tilt))+" margin: "+str(self.levelMargin))
			if (tilt < 0):
				self.tiltHead(dir=Adafruit_MotorHAT.FORWARD)
			else:
				self.tiltHead(dir=Adafruit_MotorHAT.BACKWARD)
			tilt = self.getTilt()
			count = count + 1
		print("Horizon leveled")

	def alignEarthAxis(self,latitude): # radians
		tilt = self.getTilt()
		#targetAngle = 1.5708 - float(latitude)
		targetAngle = float(latitude)
		
		while(math.fabs(tilt-targetAngle) > self.alignMargin):
			print("alignEarthAxis: delta "+str(math.fabs(targetAngle-tilt))+" tilt: "+str(tilt)+" target: "+str(targetAngle))
			if (tilt < targetAngle):
				self.tiltHead(dir=Adafruit_MotorHAT.FORWARD)
			else:
				self.tiltHead(dir=Adafruit_MotorHAT.BACKWARD)
			tilt = self.getTilt()
		print("Axis aligned")

	def timestamp(self):
		now = datetime.now()
		str_ts = "%02d.%06d"%(now.second,now.microsecond)
		return float(str_ts)

	def worker(self):
		while True:
			#if (self.running):
			time.sleep(self.loopinterval)
