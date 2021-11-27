
import gphoto2 as gp
import logging
import time
from Configuration import *
from MessageBroker import *

class Camera:
	cameramodel = "unknown"
	
	def __init__(self, configuration):
		self.config = configuration
		self.running = 0
		self.cameramodel = "unknown"
		self.images = 1000
		self.shutterspeeds = list()
		self.shutterspeed = ""
		self.apertures = list()
		self.aperture = ""
		self.isos = list()
		self.iso = ""
		#self.camconfig = ""

	def setMessageBroker(self,messagebroker):
		self.mBroker = messagebroker

	def initCamera(self):
		#logging.basicConfig(format='%(levelname)s: %(name)s: %(message)s', level=logging.WARNING)
	
		gp.check_result(gp.use_python_logging())
		context = gp.gp_context_new()
		self.camera = gp.check_result(gp.gp_camera_new())
		while True:
			try:
				gp.gp_camera_init(self.camera,context)
				#self.camera.init(context)
				self.camconfig = gp.check_result(gp.gp_camera_get_config(self.camera))
			except gp.GPhoto2Error as ex:
				print("BUIUYAAH")
				# no camera, try again in 2 seconds
				time.sleep(2)
				continue
			# operation completed successfully so exit loop
			break
		# find the capture target config item
		capture_target = gp.check_result(gp.gp_widget_get_child_by_name(self.camconfig, 'capturetarget'))
		value = gp.check_result(gp.gp_widget_get_value(capture_target))
		print('Current setting:', value)
		for n in range(gp.check_result(gp.gp_widget_count_choices(capture_target))):
			choice = gp.check_result(gp.gp_widget_get_choice(capture_target, n))
			print('Choice:', n, choice)

		gp.check_result(gp.gp_widget_set_value(capture_target, "Memory card"))
		gp.check_result(gp.gp_camera_set_config(self.camera, self.camconfig, context))

		abilities = gp.check_result(gp.gp_camera_get_abilities(self.camera))
		self.cameramodel = abilities.model
		
		# try to read shutter spekkeds
		for child in gp.check_result(gp.gp_widget_get_children(self.camconfig)):
			label = gp.check_result(gp.gp_widget_get_label(child))
			name = gp.check_result(gp.gp_widget_get_name(child))
			child_type = gp.gp_widget_get_type(child)
			print("cam conf: "+label+" : "+name+" type: ")

		#childitem = gp.gp_widget_get_child_by_name(self.camconfig, 'imgsettings')
		childitem = gp.check_result(gp.gp_widget_get_child_by_name(self.camconfig, 'shutterspeed2'))
		print("shutterspeed = "+str(childitem))

		#capture_settings = gp.check_result(gp.gp_widget_get_child_by_name(self.camconfig, 'imgsettings'))
#		print("number of chouses:"+range(gp.gp_widget_count_choices(childitem)))
		k = 0
		while (k <  gp.gp_widget_count_choices(childitem)):
			setting = gp.check_result(gp.gp_widget_get_choice(childitem, k))
			self.shutterspeeds.append(setting)
			#print('setting:', k, setting)
			k = k+1
		self.shutterspeed = gp.check_result(gp.gp_widget_get_value(childitem))
		print("current shutterspeed: ",str(self.shutterspeed))

		childitem = gp.check_result(gp.gp_widget_get_child_by_name(self.camconfig, 'iso'))
		k = 0
		while (k <  gp.gp_widget_count_choices(childitem)):
			setting = gp.check_result(gp.gp_widget_get_choice(childitem, k))
			self.isos.append(setting)
			#print('setting:', k, setting)
			k = k+1
		self.iso = gp.check_result(gp.gp_widget_get_value(childitem))
		print("current ISO: ",str(self.iso))

		childitem = gp.check_result(gp.gp_widget_get_child_by_name(self.camconfig, 'f-number'))
		k = 0
		while (k <  gp.gp_widget_count_choices(childitem)):
			setting = gp.check_result(gp.gp_widget_get_choice(childitem, k))
			self.apertures.append(str(setting))
			#print('setting:', k, setting)
			k = k+1
		self.aperture = gp.check_result(gp.gp_widget_get_value(childitem))
		print("current aperture: ",str(self.aperture))

	def setShutterSpeedIndx(self,index):
		self.setShutterSpeed(self.shutterspeeds[index])
	def getShutterSpeedIndx(self):
		return self.shutterspeeds.index(self.shutterspeed)
	def getShutterSpeedList(self):
		retval = ""
		index = 0
		while (index < len(self.shutterspeeds)):
			retval = retval + "\"" +self.shutterspeeds[index] + "\""
			index = index + 1
			if (index < len(self.shutterspeeds)):
				retval = retval + ","
		return retval
	
	def setShutterSpeed(self,speed):
		capture_target = gp.check_result(gp.gp_widget_get_child_by_name(self.camconfig, 'shutterspeed2'))
		gp.check_result(gp.gp_widget_set_value(capture_target, speed))
		gp.check_result(gp.gp_camera_set_config(self.camera, self.camconfig, context))
		self.shutterspeed = speed

	def getShutterSpeed(self):
		return self.shutterspeed
	
	def setApertureIndx(self,index):
		self.setAperture(self.apertures[index])
	def getApertureIndx(self):
		return self.apertures.index(self.aperture)
	def getApertureList(self):
		retval = ""
		print("getApertureList: "+ str(len(self.apertures)))
		index = 0
		while (index < len(self.apertures)):
			print(self.apertures[index])
			retval = retval + "\"" + self.apertures[index] + "\""
			index = index + 1
			if (index < len(self.apertures)):
				retval = retval + ","
		print("getApertureList ret: "+retval)
		return retval
	
	def setAperture(self,aperture):
		capture_target = gp.check_result(gp.gp_widget_get_child_by_name(self.camconfig, 'f-number'))
		gp.check_result(gp.gp_widget_set_value(capture_target, aperture))
		gp.check_result(gp.gp_camera_set_config(self.camera, self.camconfig, context))
		self.aperture = aperture
	
	def getAperture(self):
		return self.aperture
	
	def setISOIndx(self, index):
		self.setISO(self.isos[index])
	def getISOIndx(self):
		return self.isos.index(self.iso)
	def getISOList(self):
		retval = ""
		index = 0
		while (index < len(self.isos)):
			retval = retval + "\"" + self.isos[index] + "\""
			index = index + 1
			if (index < len(self.isos)):
				retval = retval + ","
		return retval
	
	def setISO(self,iso):
		capture_target = gp.check_result(gp.gp_widget_get_child_by_name(self.camconfig, 'iso'))
		gp.check_result(gp.gp_widget_set_value(capture_target, iso))
		gp.check_result(gp.gp_camera_set_config(self.camera, self.camconfig, context))
		self.iso = iso

	def getISO(self):
		return self.iso
	
	def takePicture(self):
		if (self.config.isSimulation() == 0):
			file_path = gp.check_result(gp.gp_camera_capture(self.camera, gp.GP_CAPTURE_IMAGE))
			print('Camera file path: {0}/{1}'.format(file_path.folder, file_path.name))
		else:
			print("Camera.takePicture() simulated")

	def setImageNumber(self, images):
		self.images = images

	def getImageNumber(self):
		print("Camera.getImageNumber "+str(self.images))
		return self.images

	def __del__(self):
		gp.check_result(gp.gp_camera_exit(self.camera))

	def getCameraModel(self):
		if (self.config.isSimulation() == 0):
			return self.cameramodel
		else:
			return "Simulation"
	
	def sendModel(self):
		self.mBroker.trasnmitdata("cammodel"+self.cameramodel, self.config.getTopic()+"StatusMessage")
