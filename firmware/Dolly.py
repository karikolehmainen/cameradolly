import logging
import time
import math
from encoder import Encoder
from datetime import datetime
from Configuration import *
from CameraHead import *
from MessageBroker import *
import RPi.GPIO as GPIO
from Adafruit_MotorHAT import *
import Adafruit_ADS1x15

class Dolly:
	LINEAR         = 0
	ANGULAR        = 1
	LINEARANGLULAR = 2
	LOCKLINEAR     = 3
	LOCKANGLULAR   = 4
	I2CBUS         = 1
	endGPIO        = 26
	startGPIO      = 20
	enc1GPIO       = 19
	enc2GPIO       = 13
	direction      = 0
	lastTick       = 0
	lastvalue      = 0
	loopinterval   = 2
	tickDistance   = 3.333333333333333 # 12 position rotary enoder 20 teeth rol and 2mm pitch belt
	BACKWARD       = Adafruit_MotorHAT.FORWARD
	FORWARD        = Adafruit_MotorHAT.BACKWARD
	running        = False
	atTheStart     = False
	atTheEnd       = False
	PWM            = 196
	PWMmin	       = 128
	PWMmax	       = 512
	speed          = 0

	def __init__(self, configuration,motorhat):
		# create a default object, no changes to I2C address or frequency
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self.endGPIO,   GPIO.IN, pull_up_down=GPIO.PUD_UP)
		GPIO.setup(self.startGPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		GPIO.setup(self.enc1GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		GPIO.setup(self.enc2GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		GPIO.add_event_detect(self.endGPIO,   GPIO.BOTH, callback=self.endCallback, bouncetime=300)
		GPIO.add_event_detect(self.startGPIO, GPIO.BOTH, callback=self.startCallback, bouncetime=300)
		enc = Encoder(self.enc1GPIO,self.enc2GPIO, callback=self.encCallback)
		self.mh = motorhat
		self.config = configuration
		self.running = 0

		self.dollyMotor= self.mh.getMotor(2)      # Linear movement motor
		self.dollyMotor.setSpeed(self.PWM)
		
		# 2mm pitch timing belt.
		# Motor speed full throttle 30rpm
		# grey code encoder 12 positions 20 teeth roll => 40mm per rev
		# 3.33mm per tick
		# Speed is (1200mm / minute) -> (20mm / sec) -> (166 msec / tick)
		#
		self.head = CameraHead(self.mh,configuration)
		self.interval = self.config.getDefInterval()

		self.xdist = 0
		self.ydist = 0
		self.mode  = Dolly.LINEAR

		self.atTheEnd = False
		self.atTheStart = False

		self.pitch = self.config.getLinearPitch()
		self.teeth = self.config.getLinearTeeth()
		self.trackLength = self.config.getTrackLength()
		self.tickDistance = (self.pitch*self.teeth)/12
		self.targetSpeed = 5 # default speed 5mm/sec
		self.declination = 0.0

		self.position = 0
		self.anglecount = 0
		self.direction = self.FORWARD
		self.initADC()

	def move(self,direction,speed):
		if (direction == self.BACKWARD):
			if  (GPIO.input(self.startGPIO)== GPIO.HIGH):
				print("going for beginning at speed: "+str(int(speed)))
				self.dollyMotor.setSpeed(int(speed))
				self.dollyMotor.run(direction)
			else:
				print("Dolly.move: at the start already")
		else:
			if (GPIO.input(self.endGPIO)== GPIO.HIGH):
				print("going for end at speed: "+str(int(speed)))
				self.dollyMotor.setSpeed(int(speed))
				self.dollyMotor.run(direction)
			else:
				print("Dolly.move: at the end already")


	def initADC(self):
		self.adc = Adafruit_ADS1x15.ADS1115(address=0x48, busnum=self.I2CBUS)
		self.adc.gain = 1
		self.chanCurr = 0
		self.chanVolt = 1
		self.chanTemp = 2
		self.mvoltage = 3300
		self.adcMAX = 32767
		#self.adc.start_adc(0)

	def quit(self):
		print("Dolly.stop")
		#self.adc.stop_adc()

	def startCallback(self,channel):
		if (GPIO.input(self.startGPIO)==GPIO.LOW):
			self.atTheStart = True
			self.atTheEnd = False
			self.dollyMotor.run(Adafruit_MotorHAT.RELEASE)
			print("falling edge detected on START")
		else:
			print("rising edge detected on START")
			self.atTheStart = False

	def endCallback(self,channel):
		if (GPIO.input(self.endGPIO)==GPIO.LOW):
			print("falling edge detected on END")
			self.atTheStart = False
			self.atTheEnd = True
			self.dollyMotor.run(Adafruit_MotorHAT.RELEASE)
		else:
			print("rising edge detected on END")
			self.atTheEnd = False

	def encCallback(self,value):
		ts = self.timestamp()
		direction = value-self.lastvalue
		self.lastvalue = value
		if (self.lastTick != 0):
			delta = ts-self.lastTick
			self.calcSpeed(delta)
		self.lastTick = ts
		# update position on track
		if (self.direction == self.FORWARD):
			self.position = self.position+self.tickDistance
		else:
			self.position = self.position-self.tickDistance

	def calcSpeed(self,ts):
		self.speed = self.tickDistance/ts
		print("dollyspeed: "+str(self.speed)+"mm/sec lastvalue: "+str(self.lastvalue))
		return self.speed

	def measureTrack(self):
		self.gotoStart()
		# clear distance counter
		self.position = 0
		# move dolly to the end
		self.gotoEnd()
		self.trackLength = self.position
		# move back to start
		self.gotoStart()
		if (self.position != 0):
			print("measureTrack difference in dist: " +str(self.position))
			self.position = 0
		print("measureTrack length: "+str(self.trackLength))
		# save track length
		configuration.setTrackLegth(self.trackLength)

	def rotateHead(self, speed):
		self.head.rotateHead(speed)

	def moveDolly(self):
		if (self.mode == Dolly.LINEAR):
			self.move(self.FORWARD,self.PWM)

		if (self.mode == Dolly.ANGULAR):
			print("self.mode == Dolly.ANGULAR")
			self.rotateHead(self.speed)

		# add these later
		#if (self.mode == Dolly.LINEARANGLULAR):
		#	print("self.mode == Dolly.LINEARANGLULAR")
		#	self.head.rotateHead(self.anglesteps)
		#	self.anglecount = self.anglecount+self.anglesteps
		#	self.stepDolly(self.numsteps)
		#	self.stepcount = self.stepcount+self.numsteps

		#if (self.mode == Dolly.LOCKLINEAR):
		#	print("self.mode == Dolly.LOCKLINEAR")
		#	self.stepDolly(self.numsteps)
		#	anglechange = self.calculateAngularDelta() # radians
		#	print("LOCKLINEAR anglechange = "+str(anglechange))
		#	self.head.rotateHead(anglechange)
		#	self.anglecount = self.anglecount+anglechange
		#	self.stepcount = self.stepcount+self.numsteps

		#if (self.mode == Dolly.LOCKANGLULAR):
		#	print("self.mode == Dolly.LOCKANGLULAR")
		#	stepstomove = self.calculateLinearSteps()
		#	print("LOCKANGLULAR stepstomove = "+str(stepstomove))
		#	self.stepDolly(stepstomove)
		#	self.stepcount = self.stepcount+stepstomove
		#	self.head.rotateHead(self.anglesteps)
		#	self.anglecount = self.anglecount+self.anglesteps

	# ADC read functions
	def getTemp(self):
		valueS1 = self.adc.read_adc(self.chanTemp)
		S1voltage = (valueS1/self.adcMAX)*self.mvoltage
		return S1voltage

	def getVoltage(self):
		#divider = 0.222422975571551
		divider = 0.255
		value = self.adc.read_adc(self.chanVolt)
		voltage = (value/self.adcMAX)*self.mvoltage
		return int(voltage/divider)
		#return voltage

	def getCurrent(self):
		# voltage read by ADC with divider 1 divided by measured mA 
		divider = 1332.609027375103/230.0
		value = self.adc.read_adc(self.chanCurr)
		voltage = (value/self.adcMAX)*self.mvoltage
		#return voltage
		return int(voltage/divider)

	# retuns linear position of the dolly in millimeters
	def getPositionMM(self):
		return self.position

	def getAngleDeg(self):
		return self.head.getHeading()
		#steps = self.config.getAngularStepsPerTeeth()
		#return float(self.anglecount)*float(360.0/(self.angleteeth*steps))
	def getHeading(self):
		return self.head.getHeading()

	def getTilt(self):
		return self.head.getTilt()

	def setOperationModes(self,mode):
		if (self.running == 1):
			self.running = 0
			self.gotoStarte()
			self.anglularHome()
		self.mode = mode

	def getOperationMode(self):
		return self.mode

	# units meters
	def setTrackingX(self,xdist):
		self.xdist = xdist

	# units meters
	def setTrackingY(self,ydist):
		self.ydist = ydist

	def getTrackingY(self):
		return self.ydist

	def getTrackingX(self):
		return self.xdist

	# units meters
	def setStepDistance(self,dist):
		self.numsteps = self.distanceToStepsMM(dist)

	# units meters
	def setStepAngle(self,angle):
		self.anglesteps = math.radians(angle)
		print("setStepAngle "+str(angle)+" -> "+str(self.anglesteps))

	# Move andular axis to home and set counter to zero
	def anglularHome(self):
		self.running = 0

	def isRunning(self):
		return self.running

	def start(self):
		# moe to start
		self.gotoStart()
		# calculate needed speed
		self.direction = self.FORWARD
		self.move(self.direction, self.PWM) 
		self.running = 1

	def adjustSpeed(self, delta):
		# we need to slow down delta positive
		if (delta > 0):
			self.PWM = self.PWM*(delta/100)
			if (self.PWM < self.PWMmin):
				self.PWM = self.PWMmin
		# we need to speed up delta negative
		elif(delta < 0):
			self.PWM = self.PWM*(1+(-1*delta)/100)
			if (self.PWM > self.PWMmax):
				self.PWM = self.PWMmax
		self.move(self.direction, self.PWM)

	def stop(self):
		self.dollyMotor.run(Adafruit_MotorHAT.RELEASE)
		self.running = 0

	def getHeadAlignment(self):
		accel_x = sensor.getX()
		accel_z = sensor.getZ()
		print('Accel X={0}, Accel Z={1}'.format(accel_x, accel_z))
	
	def setInterval(self,inter):
		self.interval = inter

	def getInterval(self):
		return self.interval

	def gotoStart(self):
		self.stop()
		print("gotoStart: stopped, now seeking home")
		self.move(self.BACKWARD,255)
		while (self.atTheStart == False):
			time.sleep(self.loopinterval)
			print("gotoStart: are we there yet?")
		self.position = 0
		print("gotoStart: now at start")


	def gotoEnd(self):
		self.stop()
		print("gotoEnd: stopped, now seeking end")
		#move dolly until oneof the interrupts fires
		self.direction = self.FORWARD
		self,move(self.direction,255)
		while(self.atTheEnd == False):
			time.sleep(0.5)
		self.direction = Adafruit_MotorHAT.BACKWARD
		print("gotoEnd: ready")
		self.running = 0

	def timestamp(self):
		now = datetime.now()
		str_ts = "%02d.%06d"%(now.second,now.microsecond)
		return float(str_ts)

	def worker(self):
		while True:
			if (self.running):
				ts = self.timestamp()
				tdelta = ts-self.lastTick
				self.calcSpeed(tdelta)
				delta = (self.speed-self.targetSpeed)/self.targetSpeed
				print("speed: "+str(self.speed)+" target: "+str(self.targetSpeed))
				if(delta < 0.001 or delta > 0.001):
					self.adjustSpeed(delta)
			# thread loop
			time.sleep(self.loopinterval)

