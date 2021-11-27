import json
from pprint import pprint

class Configuration:
	json_conf = []
	def __init__(self):
		print("Init")
	
	def readConfiguration(self):
		print("Reading configuration file")
		with open('/etc/cameradolly.json', 'r') as handle:
			self.json_conf = json.load(handle)
	def getMqttUsername(self):
		return self.json_conf["configuration"]["mqtt_username"]
	def getMqttPassword(self):
		return self.json_conf["configuration"]["mqtt_password"]
	def getMQTTURL(self):
		return self.json_conf["configuration"]["mqtt_address"]
	def getTopic(self):
		return self.json_conf["configuration"]["mqtt_topic"]
	def getStepsPerFrame(self):
		return self.json_conf["configuration"]["stepsperframe"]
	def getDefaultDirection(self):
		return self.json_conf["configuration"]["defaultdirection"]
	def getDefaultImages(self):
		return self.json_conf["configuration"]["defaultimages"]
	def getStepperSpeed(self):
		return self.json_conf["configuration"]["stepperspeed"]
	def getStepsPerRev(self):
		return self.json_conf["configuration"]["steps_rev"]
	def getLinearPitch(self):
		return self.json_conf["configuration"]["linear_pitch"]
	def getLinearTeeth(self):
		return self.json_conf["configuration"]["linear_teeth"]
	def getAngularTeeth(self):
		return self.json_conf["configuration"]["anglular_teeth"]
	def getAngularStepsPerTeeth(self):
		return self.json_conf["configuration"]["anglular_steps_teeth"]
	def getStabisationBuffer(self):
		return self.json_conf["configuration"]["stabilisationtime"]
	def getDefInterval(self):
		return self.json_conf["configuration"]["interval"]
	def isSimulation(self):
		return self.json_conf["configuration"]["simulate"]
