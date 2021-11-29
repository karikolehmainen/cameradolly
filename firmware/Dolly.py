import logging
import time
import math
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

	def __init__(self, configuration,motorhat):
		# create a default object, no changes to I2C address or frequency
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		GPIO.add_event_detect(26, GPIO.FALLING, callback=self.endCallback, bouncetime=300)
		GPIO.add_event_detect(21, GPIO.FALLING, callback=self.startCallback, bouncetime=300)
		self.mh = motorhat
		self.config = configuration
		self.running = 0

		self.dollyMotor= self.mh.getMotor(2)      # Linear movement motor
		self.dollyMotor.setSpeed(255)
		
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

		self.atTheEnd = 0
		self.atTheStart = 0

		self.pitch = self.config.getLinearPitch()
		self.teeth = self.config.getLinearTeeth()

		self.declination = 0.0

		self.stepcount = 0
		self.anglecount = 0
		self.numsteps = self.config.getStepsPerFrame()
		self.anglesteps = 0  # steps to rotate camera per frame (used in LocAngular and Anglular modes)
		self.direction = Adafruit_MotorHAT.FORWARD
		self.angleteeth = self.config.getAngularTeeth()
		self.anglestepsperteeth = self.config.getAngularStepsPerTeeth()
		self.initADC()

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
		print("falling edge detected on 20")
		self.atTheStart = 1
		self.atTheEnd = 0

	def endCallback(self,channel):
		print("falling edge detected on 26")
		self.atTheStart = 0
		self.atTheEnd = 1

	#recommended for auto-disabling motors on shutdown!
	def turnOffMotors(self):
		kit.stepper1.release()
		kit.stepper2.release()

	def rotateHead(self, speed):
		self.head.rotateHead(speed)

	def moveDolly(self):
		if (self.mode == Dolly.LINEAR):
			self.stepDolly(self.numsteps)
			self.stepcount = self.stepcount+self.numsteps

		if (self.mode == Dolly.ANGULAR):
			print("self.mode == Dolly.ANGULAR")
			self.head.rotateHead(self.anglesteps)
			self.anglecount = self.anglecount+self.anglesteps

		if (self.mode == Dolly.LINEARANGLULAR):
			print("self.mode == Dolly.LINEARANGLULAR")
			self.head.rotateHead(self.anglesteps)
			self.anglecount = self.anglecount+self.anglesteps
			self.stepDolly(self.numsteps)
			self.stepcount = self.stepcount+self.numsteps

		if (self.mode == Dolly.LOCKLINEAR):
			print("self.mode == Dolly.LOCKLINEAR")
			self.stepDolly(self.numsteps)
			anglechange = self.calculateAngularDelta() # radians
			print("LOCKLINEAR anglechange = "+str(anglechange))
			self.head.rotateHead(anglechange)
			self.anglecount = self.anglecount+anglechange
			self.stepcount = self.stepcount+self.numsteps

		if (self.mode == Dolly.LOCKANGLULAR):
			print("self.mode == Dolly.LOCKANGLULAR")
			stepstomove = self.calculateLinearSteps()
			print("LOCKANGLULAR stepstomove = "+str(stepstomove))
			self.stepDolly(stepstomove)
			self.stepcount = self.stepcount+stepstomove
			self.head.rotateHead(self.anglesteps)
			self.anglecount = self.anglecount+self.anglesteps

	def stepDolly(self,steps):
		count = 0
		if (self.direction == Adafruit_MotorHAT.FORWARD and self.atTheEnd == 0):
			print("stepDolly FORWARD")
			while (count < steps):
				self.dollyMotor.run(self.direction)
				#check if GPIO is cleared and clear the flag
				if(GPIO.input(21) is False):
					self.atTheStart = 0
				count = count + 1
				time.sleep(1)
		if (self.direction == Adafruit_MotorHAT.BACKWARD and self.atTheStart == 0):
			print("stepDolly BACKWARD")
			#check if GPIO is cleared and clear the flag
			while (count < steps):
				self.dollyMotor.run(self.direction)
				if(GPIO.input(26) is False):
					self.atTheEnd = 0
				count = count + 1
				time.sleep(1)
		self.dollyMotor.run(Adafruit_MotorHAT.RELEASE)

	def calculateLinearSteps(self):
		if (self.mode == Dolly.LOCKANGLULAR):
			#determine X position
			x_comp = self.xdist-self.stepsToDistanceM(self.stepcount)
			y_comp = self.ydist
			alpha  = math.atan(x_comp/y_comp) # radians
			#delta is the angle in new position
			delta  = alpha - self.anglesteps # changed
			# determine how much x_component need to be moved
			print("calculateLinearSteps x_comp:"+str(x_comp)+" alpha:"+str(alpha)+" delta:"+str(delta))
			return self.distanceToStepsM(math.tan(delta)*y_comp)
		else:
			return 0

	def calculateAngularDelta(self):
		if (self.mode == Dolly.LOCKLINEAR):
			# position where we start
			x_comp = self.xdist-self.stepsToDistanceM(self.stepcount)
			y_comp = self.ydist
			alpha  = math.atan(x_comp/y_comp) # radians of the first position
			#delta is the angle in new position
			x_delta = self.xdist-self.stepsToDistanceM(self.stepcount+self.numsteps)
			#x_delta =
			delta  = alpha - math.atan(x_delta/y_comp)

			print("calculateAngularSteps x_comp:"+str(x_comp)+" alpha:"+str(alpha)+" delta:"+str(delta))
			return delta
		else:
			return 0
	# ADC read functions
	def getTemp(self):
		valueS1 = self.adc.read_adc(self.chanTemp)
		S1voltage = (valueS1/self.adcMAX)*self.mvoltage
		return S1voltage

	def getVoltage(self):
		divider = 0.222422975571551
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
		pitch = self.config.getLinearPitch()
		teeth = self.config.getLinearTeeth()
		result = float(self.stepcount)*(float(pitch*teeth)/12.0)
		print("Dolly.getPositionMM = "+str(result))
		return result

	def getPositionM(self):
		return self.getPositionMM()/1000.0

	# retuns linear step size of the dolly in millimeters
	def getStepSizeMM(self):
		#print("Dolly.getPositionMM "+str(self.pitch)+" x "+str(self.teeth) + " x " + str(self.stepsPerRev))
		ditance = (self.numsteps*self.pitch*self.teeth)/self.stepsPerRev
		#print("Dolly.getStepSizeMM = " + str(ditance))
		return ditance

	def getAngleDeg(self):
		return self.head.getHeading()
		#steps = self.config.getAngularStepsPerTeeth()
		#return float(self.anglecount)*float(360.0/(self.angleteeth*steps))
	def getHeading(self):
		return self.head.getHeading()

	def getTilt(self):
		return self.head.getTilt()

	def linearHome(self):
		#move dolly until oneof the interrupts fires
		print("linearHome: moving until interrupted")
		self.direction = STEPPER.BACKWARD
		self.stepDolly(self.stepcount)
		while(self.atTheStart == 0):
			self.stepDolly(self.numsteps)
		self.direction = STEPPER.FORWARD
		print("linearHome: ready")
		self.stepcount = 0
		self.running = 0

	def setOperationModes(self,mode):
		if (self.running == 1):
			self.running = 0
			self.linearHome()
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
		self.running = 1

	def stop(self):
		self.running = 0

	def stepsToDistanceM(self,steps):
		pitch = self.config.getLinearPitch()
		teeth = self.config.getLinearTeeth()
		return (((teeth*pitch)/self.stepsPerRev)*steps)/1000
	
	def stepsToDistanceMM(self,steps):
		pitch = self.config.getLinearPitch()
		teeth = self.config.getLinearTeeth()
		return (((teeth*pitch)/self.stepsPerRev)*steps)
	
	def distanceToStepsM(self,dist):
		pitch = self.config.getLinearPitch()
		teeth = self.config.getLinearTeeth()
		return int((1000*dist)/(((teeth*pitch)/self.stepsPerRev)))

	def distanceToStepsMM(self,dist):
		pitch = self.config.getLinearPitch()
		teeth = self.config.getLinearTeeth()
		return int((dist)/(((teeth*pitch)/self.stepsPerRev)))

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
		self.linearHome()

	def gotoEnd(self):
		self.stop()
		print("gotoEnd: stopped, now seeking end")
		#move dolly until oneof the interrupts fires
		self.direction = Adafruit_MotorHAT.FORWARD
		while(self.atTheEnd == 0):
			self.stepDolly(self.numsteps)
			self.stepcount = self.stepcount+self.numsteps
		self.direction = Adafruit_MotorHAT.BACKWARD
		print("gotoEnd: ready")
		self.stepcount = 0
		self.running = 0
        
