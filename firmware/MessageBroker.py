import json
import paho.mqtt.client as mqtt
from uuid import getnode as get_mac
from Camera import *
import CameraDolly
from Configuration import *
import time
import datetime
import math
from datetime import datetime, date, timedelta
from pytz import timezone

def on_log(client, userdata, level, buf):
	#print("log: ",buf)
	print("")

class MessageBroker:
	mqtturl = "null"
	uname = "name"
	passwd = "passwd"
	type = "MQTT"

	def __init__(self, conf,camera,dolly,heater):
		# connec to server REST interface
		self.conf = conf
		self.mqtturl=conf.getMQTTURL()
		self.uname=conf.getMqttUsername()
		self.passwd=conf.getMqttPassword()
		self.camera = camera
		self.heater = heater
		self.dolly = dolly
		self.client=mqtt.Client("CameraDolly",False)
		self.client.on_message=self.on_message
		self.client.on_log=on_log
		self.client.on_connect = self.on_connect
		self.client.username_pw_set(self.uname, self.passwd)
		print("DataTransmitter.Init ready")
		#def __del__(self):
		#self.client.loop_stop()

	# Handle incoming MQTT messages. Parses control messages. Message format is "[commang]-[value]"
	# at this point it is verstile enough. If more sophistication like timestamps, etc are needed
	# better messaging has be implemented. To other direction message tries to be NGSI compliatn JSON so
	# similar approach could be used.
	def on_message(self,client, userdata, message):
		msge =str(message.payload.decode("utf-8"))
		msge = msge.strip()
		#print("message received " ,msge)
		#print("message topic=",message.topic)
		topics = message.topic.split("/")
		if (len(topics)>2):
			if (topics[2] == "rotate"):
				self.dolly.rotateHead(msge)
				return
			elif (topics[2] == "start"):
				self.dolly.start()
				return
			elif (topics[2] == "stop"):
				self.dolly.stop()
				return
			elif (topics[2] == "gotostart"):
				self.dolly.gotoStart()
				return
			elif (topics[2] == "gotoend"):
				self.dolly.gotoEnd()
				return
			elif (topics[2] == "level_horizon"):
				self.dolly.head.levelHeadHorizon()
				return
			elif (topics[2] == "StatusMessage"):
				return
			elif (topics[2] == "head_off"):
				self.dolly.head.headOff()
				return
			elif (topics[2] == "measure_track"):
				self.dolly.measureTrack()
				return
			elif (topics[2] == "align_axis"):
				self.dolly.head.alignEarthAxis(msge)
				return
			elif (topics[2] == "getcammodel"):
				self.transmitCameraModel()
				return
			elif (topics[2] == "getcamsettings"):
				self.transmitCameraSettingsLists()
				return
			elif (topics[2] == "getheatsetting"):
				self.transmitHeatSetting()
				return
			elif (topics[2] == "setheat"):
				self.heater.setPWM(int(setting))
				return
			elif (topics[2] == "rcamsettings"):
				self.transmitCameraSettings()
				return
# Legacy messages from here on...
		print("message qos=",message.qos)
		print("message retain flag=",message.retain)
		if (len(msge.split("-")) != 2):
			msg = msge
		else:
			msg,setting = msge.split("-")

		if (msg == "getstepsize"):
			self.sendStepSize()
		if (msg == "getstepcount"):
			self.sendStepCount()
		if (msg == "getmode"):
			self.sendOpMode()
		if (msg == "gettracking"):
			print("send tracking info")
			self.sendTracking()
		if (msg == "getimagenumber"):
			self.sendImageNumber()
		if (msg == "getinterval"):
			self.sendImageInterval()
		if (msg == "getposition"):
			self.transmitPositionMessage(dolly.getPositionMM, dolly.getAngleDeg(), getCounter(),dolly.getHeading(),dolly.getTilt(),dolly.getTemp(),dolly.getVoltage())
		if (msg == "setmode"):
			print("on_message: set mode to "+setting)
			self.dolly.setOperationModes(int(setting))
		if (msg == "settargetx"):
			print("on_message: set tracking X to "+setting)
			self.dolly.setTrackingX(float(setting))
		if (msg == "settargety"):
			print("on_message: set tracking Y to "+setting)
			self.dolly.setTrackingY(float(setting))
		if (msg == "setstepdistance"):
			print("on_message: set step distance to "+setting)
			self.dolly.setStepDistance(int(setting))
		if (msg == "setanglestep"):
			print("on_message: set angle step to "+setting)
			self.dolly.setStepAngle(float(setting))
		if (msg == "setanglestep"):
			print("on_message: set declination to "+setting)
			self.dolly.setDeclination(float(setting))
		if (msg == "setimagenumber"):
			print("on_message: set image number to "+setting)
			self.camera.setImageNumber(int(setting))
		if (msg == "setdeclination"):
			print("on_message: set image number to "+setting)
			self.dolly.setDeclination(float(setting))
		if (msg == "setcomperr"):
			print("on_message: set compass error "+setting)
			self.dolly.setCompassError(float(setting))
		if (msg == "interval"):
			print("on_message: set interval "+setting)
			self.dolly.setInterval(float(setting))
		if (msg == "rotateccw"):
			print("on_message:rotate CCW ")
			self.dolly.head.rotateCCW()
		if (msg == "rotatecw"):
			print("on_message:rotate CW ")
			self.dolly.head.rotateCW()
		if (msg == "get_head_angle"):
			self.dolly.head.getTilt()

	def connect(self):
		print("DataTransmitter.connect connecting to mqtt broker ", self.mqtturl)
		self.client.connect(self.mqtturl,port=1883)
		print("DataTransmitter.connect ready")

	def on_connect(self, client, userdata, flags, rc):
		if rc==0:
			print("connected OK Returned code=",rc)
		else:
			print("Bad connection Returned code=",rc)

	def getTimeStamp(self):
		ts = time.time()
		utcts = datetime.utcfromtimestamp(ts)
		zonets = timezone('UTC').localize(utcts)
		timestamp = zonets.strftime('%Y-%m-%dT%H:%M:%S')
		return timestamp
	
	# Method to construct ID field for NGSI service desciption messages (not used right now)
	def getDollyIDServiceField(self):
		mac = get_mac()
		#field = "{\n"
		field = ""
		field = field + "\"_id\":{\n"
		field = field + "\t\t\"id\":\""+mac+"\",\n"
		field = field + "\t\t\"type\":\"dolly\",\n"
		field = field + "\t\t\"servicePath\":\"/dolly\",\n"
		field = field + "}"
		return field

	# Method for contructing ID field for dolly NGSI status messages
	def getDollyIDField(self):
		mac = get_mac()
		field = ""
		field = field + "\t\"id\":\""+str(mac)+"\",\n"
		field = field + "\t\"type\":\"dolly\",\n"
		field = field + "\t\"isPattern\":\"false\""
		return field

	def transmitCameraSettings(self):
		print("transmitCameraSettings")
		message = "{\n"
		message = message + "\"contextElements\": [\n\t{\n\t"
		message = message + "\t\"attributes\": [\n"
		message = message + "\t\t{\n"
		message = message + "\t\t\tsspeeds\":["
		speeds = self.camera.getShutterSpeedList()
		print("shutter speeds: "+speeds)
		message = message + speeds
		message = message + "\t\t\t],\n"
		message = message + "\t\t\tapertures\":["
		apertures = self.camera.getApertureList()
		print("apertures: "+apertures)
		message = message + apertures
		message = message + "\t\t\t],\n"
		message = message + "\t\t\tisos\":["
		isos = self.camera.getISOList()
		print("ISOs: "+isos)
		message = message + isos
		message = message + "\t\t\t]\n"
		message = message + "\t\t}\n\t]\n"
		message = message + "\t}\n]}"
		self.transmitdata(message,self.conf.getTopic()+"CameraMessage")

	# Method for transmitting dolly position status message
	# Sends position on rail, angle of the camera head and number of images taken
	def transmitPositionMessage(self, position, angle, images,heading,tilt,temp,volt,power):
		message = "{\n"
		message = message + "\"contextElements\": [\n\t{\n\t"
		message = message + self.getDollyIDField()+",\n"
		message = message + "\t\"attributes\": [\n"
		message = message + "\t\t{\n"
		message = message + "\t\t\t\"name\":\"position\",\n"
		message = message + "\t\t\t\"type\":\"float\",\n"
		message = message + "\t\t\t\"value\":\""+str(position)+"\"\n"
		message = message + "\t\t},\n"
		message = message + "\t\t{\n"
		message = message + "\t\t\t\"name\":\"angle\",\n"
		message = message + "\t\t\t\"type\":\"float\",\n"
		message = message + "\t\t\t\"value\":\""+str(angle)+"\"\n"
		message = message + "\t\t},\n"
		message = message + "\t\t{\n"
		message = message + "\t\t\t\"name\":\"heading\",\n"
		message = message + "\t\t\t\"type\":\"float\",\n"
		message = message + "\t\t\t\"value\":\""+str(heading)+"\"\n"
		message = message + "\t\t},\n"
		message = message + "\t\t{\n"
		message = message + "\t\t\t\"name\":\"tilt\",\n"
		message = message + "\t\t\t\"type\":\"float\",\n"
		message = message + "\t\t\t\"value\":\""+str(tilt)+"\"\n"
		message = message + "\t\t},\n"
		message = message + "\t\t{\n"
		message = message + "\t\t\t\"name\":\"images\",\n"
		message = message + "\t\t\t\"type\":\"integer\",\n"
		message = message + "\t\t\t\"value\":\""+str(images)+"\"\n"
		message = message + "\t\t},\n"
		message = message + "\t\t{\n"
		message = message + "\t\t\t\"name\":\"temp\",\n"
		message = message + "\t\t\t\"type\":\"integer\",\n"
		message = message + "\t\t\t\"value\":\""+str(temp)+"\"\n"
		message = message + "\t\t},\n"
		message = message + "\t\t{\n"
		message = message + "\t\t\t\"name\":\"volt\",\n"
		message = message + "\t\t\t\"type\":\"float\",\n"
		message = message + "\t\t\t\"value\":\""+str(volt)+"\"\n"
		message = message + "\t\t},\n"
		message = message + "\t\t{\n"
		message = message + "\t\t\t\"name\":\"power\",\n"
		message = message + "\t\t\t\"type\":\"float\",\n"
		message = message + "\t\t\t\"value\":\""+str(power)+"\"\n"
		message = message + "\t\t}\n"
		message = message + "\t],\n"
		message = message + "\t\"creDate\":\""+self.getTimeStamp()+"\"\n"
		message = message + "\t}\n]}"
		self.transmitdata(message,self.conf.getTopic()+"PositionMessage")

	# Method for transmitting camera model string
	# Sends camera model to subsribers
	def transmitCameraModel(self):
		message = "{\n"
		message = message + "\"contextElements\": [\n\t{\n"
		message = message + self.getDollyIDField()+",\n"
		message = message + "\t\"attributes\": [\n"
		message = message + "\t\t{\n"
		message = message + "\t\t\t\"name\":\"cameramodel\",\n"
		message = message + "\t\t\t\"type\":\"string\",\n"
		message = message + "\t\t\t\"value\":\""+self.camera.getCameraModel()+"\"\n"
		message = message + "\t\t},\n"
		message = message + "\t\t{\n"
		message = message + "\t\t\t\"name\":\"shutterspeed\",\n"
		message = message + "\t\t\t\"type\":\"integer\",\n"
		message = message + "\t\t\t\"value\":\""+str(self.camera.getShutterSpeedIndx())+"\"\n"
		message = message + "\t\t},\n"
		message = message + "\t\t{\n"
		message = message + "\t\t\t\"name\":\"aperture\",\n"
		message = message + "\t\t\t\"type\":\"integer\",\n"
		message = message + "\t\t\t\"value\":\""+str(self.camera.getApertureIndx())+"\"\n"
		message = message + "\t\t},\n"
		message = message + "\t\t{\n"
		message = message + "\t\t\t\"name\":\"isovalue\",\n"
		message = message + "\t\t\t\"type\":\"integer\",\n"
		message = message + "\t\t\t\"value\":\""+str(self.camera.getISOIndx())+"\"\n"
		message = message + "\t\t}\n"
		message = message + "\t],\n"
		message = message + "\t\"creDate\":\""+str(self.getTimeStamp())+"\"\n"
		message = message + "\t}\n]}"
		self.transmitdata(message,self.conf.getTopic()+"CameraModelMessage")
	
	# Method for transmitting camera model string
	# Sends camera model to subsribers
	def transmitCameraSettingsLists(self):
		message = "{\n"
		message = message + "\"contextElements\": [\n\t{\n"
		message = message + self.getDollyIDField()+",\n"
		message = message + "\t\"attributes\": [\n"
		message = message + "\t\t{\n"
		message = message + "\t\t\t\"name\":\"sppertureList\",\n"
		message = message + "\t\t\t\"type\":\"string\",\n"
		message = message + "\t\t\t\"value\":\""+self.camera.getAppertureList()+"\"\n"
		message = message + "\t\t},\n"
		message = message + "\t\t{\n"
		message = message + "\t\t\t\"name\":\"shutterspeedList\",\n"
		message = message + "\t\t\t\"type\":\"string\",\n"
		message = message + "\t\t\t\"value\":\""+self.camera.getShutterSpeedList()+"\"\n"
		message = message + "\t\t},\n"
		message = message + "\t\t{\n"
		message = message + "\t\t\t\"name\":\"isoList\",\n"
		message = message + "\t\t\t\"type\":\"string\",\n"
		message = message + "\t\t\t\"value\":\""+self.camera.getISOList()+"\"\n"
		message = message + "\t\t}\n"
		message = message + "\t],\n"
		message = message + "\t\"creDate\":\""+self.getTimeStamp()+"\"\n"
		message = message + "\t}\n]}"
		self.transmitdata(message,self.conf.getTopic()+"CameraModelMessage")
	
	def transmitHeatSetting(self):
		message = "{\n"
		message = message + "\"contextElements\": [\n\t{\n"
		message = message + self.getDollyIDField()+",\n"
		message = message + "\t\"attributes\": [\n"
		message = message + "\t\t{\n"
		message = message + "\t\t\t\"name\":\"heatsetting\",\n"
		message = message + "\t\t\t\"type\":\"integer\",\n"
		message = message + "\t\t\t\"value\":\""+str(self.heater.getPWM())+"\"\n"
		message = message + "\t\t}\n"
		message = message + "\t],\n"
		message = message + "\t\"creDate\":\""+self.getTimeStamp()+"\"\n"
		message = message + "\t}\n]}"
		self.transmitdata(message,self.conf.getTopic()+"SettingMessage")
	
	def sendStepSize(self):
		message = "{\n"
		message = message + "\"contextElements\": [\n\t{\n\t"
		message = message + self.getDollyIDField()+",\n"
		message = message + "\t\"attributes\": [\n"
		message = message + "\t\t{\n"
		message = message + "\t\t\t\"name\":\"stepsize\",\n"
		message = message + "\t\t\t\"type\":\"float\",\n"
		message = message + "\t\t\t\"value\":\""+str(self.dolly.getStepSizeMM())+"\"\n"
		message = message + "\t\t},\n"
		message = message + "\t\t{\n"
		message = message + "\t\t\t\"name\":\"anglestep\",\n"
		message = message + "\t\t\t\"type\":\"float\",\n"
		message = message + "\t\t\t\"value\":\""+str(self.dolly.getAngleDeg())+"\"\n"
		message = message + "\t\t}\n"
		message = message + "\t],\n"
		message = message + "\t\"creDate\":\""+self.getTimeStamp()+"\"\n"
		message = message + "\t}\n]}"
		self.transmitdata(message,self.conf.getTopic()+"SettingMessage")
	
	def sendImageNumber(self):
		print("sendImageNumber - start")
		message = "{\n"
		message = message + "\"contextElements\": [\n\t{\n\t"
		message = message + self.getDollyIDField()+",\n"
		message = message + "\t\"attributes\": [\n"
		message = message + "\t\t{\n"
		message = message + "\t\t\t\"name\":\"imagenumber\",\n"
		message = message + "\t\t\t\"type\":\"integer\",\n"
		print("sendImageNumber - start2")
		message = message + "\t\t\t\"value\":\""+str(self.camera.getImageNumber())+"\"\n"
		print("sendImageNumber - start3")
		message = message + "\t\t}\n"
		message = message + "\t],\n"
		message = message + "\t\"creDate\":\""+self.getTimeStamp()+"\"\n"
		message = message + "\t}\n]}"
		print("sendImageNumber - end")
		self.transmitdata(message,self.conf.getTopic()+"SettingMessage")
	
	def sendImageInterval(self):
		print("sendImageInterval - start")
		message = "{\n"
		message = message + "\"contextElements\": [\n\t{\n\t"
		message = message + self.getDollyIDField()+",\n"
		message = message + "\t\"attributes\": [\n"
		message = message + "\t\t{\n"
		message = message + "\t\t\t\"name\":\"interval\",\n"
		message = message + "\t\t\t\"type\":\"float\",\n"
		print("sendImageInterval - start2")
		message = message + "\t\t\t\"value\":\""+str(self.dolly.getInterval())+"\"\n"
		print("sendImageInterval - start3")
		message = message + "\t\t}\n"
		message = message + "\t],\n"
		message = message + "\t\"creDate\":\""+self.getTimeStamp()+"\"\n"
		message = message + "\t}\n]}"
		print("sendImageInterval - end")
		self.transmitdata(message,self.conf.getTopic()+"SettingMessage")
	
	def sendOpMode(self):
		message = "{\n"
		message = message + "\"contextElements\": [\n\t{\n\t"
		message = message + self.getDollyIDField()+",\n"
		message = message + "\t\"attributes\": [\n"
		message = message + "\t\t{\n"
		message = message + "\t\t\t\"name\":\"operationmode\",\n"
		message = message + "\t\t\t\"type\":\"integer\",\n"
		message = message + "\t\t\t\"value\":\""+str(self.dolly.getOperationMode())+"\"\n"
		message = message + "\t\t}\n"
		message = message + "\t],\n"
		message = message + "\t\"creDate\":\""+self.getTimeStamp()+"\"\n"
		message = message + "\t}\n]}"
		self.transmitdata(message,self.conf.getTopic()+"SettingMessage")

	def sendTracking(self):
		#print("sendTracking - start")
		message = "{\n"
		message = message + "\"contextElements\": [\n\t{\n\t"
		message = message + self.getDollyIDField()+",\n"
		message = message + "\t\"attributes\": [\n"
		message = message + "\t\t{\n"
		message = message + "\t\t\t\"name\":\"trackx\",\n"
		message = message + "\t\t\t\"type\":\"float\",\n"
		#print("sendTracking - start2")
		message = message + "\t\t\t\"value\":\""+str(self.dolly.getTrackingX())+"\"\n"
		message = message + "\t\t},\n"
		message = message + "\t\t{\n"
		message = message + "\t\t\t\"name\":\"tracky\",\n"
		message = message + "\t\t\t\"type\":\"float\",\n"
		message = message + "\t\t\t\"value\":\""+str(self.dolly.getTrackingY())+"\"\n"
		message = message + "\t\t}\n"
		message = message + "\t],\n"
		message = message + "\t\"creDate\":\""+self.getTimeStamp()+"\"\n"
		message = message + "\t}\n]}"
		print("sendTracking - end")
		self.transmitdata(message,self.conf.getTopic()+"SettingMessage")

	def transmitdata(self,data,topic):
		#print("DataTransmitter.transmitdata topic:"+topic+" msg:"+data)
		datastr = str(data)
		datastr = datastr.replace("'","\"")
		self.client.publish(topic,payload=datastr,qos=0, retain=False)

	def worker(self):
		self.client.subscribe("/CameraDolly/#")
		self.client.loop_start()
		try:
			while True:
				time.sleep(1)
		except KeyboardInterrupt:
			print("exiting")
		self.client.disconnect()
		self.client.loop_stop()
#print("DataTransmitter.trasnmitdata ready")

