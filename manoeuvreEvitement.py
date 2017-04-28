#-*- coding:utf8 -*

# manoeuvre d'evitement du robot
# juste l'evitement
# rien d'autre

from threading import Thread
import math

import sys
import motion
import time
from naoqi import ALProxy
import math
import time



if len(sys.argv) < 2:
	robotIp="localhost"
	robotPort=11212
elif sys.argv[1] == "robot":
	robotIp="172.20.28.198"
	robotPort=9559
	print("TRying to connect to robot..")
else:
	robotIp="localhost"
	robotPort=11212	


#if (len(sys.argv) >= 2):
#    robotIp = sys.argv[1]
#if (len(sys.argv) >= 3):
#    robotPort = int(sys.argv[2])

print robotIp
print robotPort

# Init proxies.
try:
    motionProxy = ALProxy("ALMotion", robotIp, robotPort)
except Exception, e:
    print "Could not create proxy to ALMotion"
    print "Error was: ", e

try:
    postureProxy = ALProxy("ALRobotPosture", robotIp, robotPort)
except Exception, e:
    print "Could not create proxy to ALRobotPosture"
    print "Error was: ", e

try:
    voicePxy = ALProxy("ALTextToSpeech", robotIp, robotPort)
except Exception, e:
    print "Could not create proxy to text2speech"
    print "Error was: ", e

try:
    memoryProxy = ALProxy("ALMemory", robotIp, robotPort)
except Exception, e:
    print "Could not create proxy to ALMemory"
    print "Error was: ", e

try:
    sonarProxy = ALProxy("ALSonar", robotIp, robotPort)
except Exception, e:
    print "Could not create proxy to ALSonar"
    print "Error was: ", e


STATE_TURN_RIGHT = 2
STATE_TERMINATED = 3
STATE_STANDBYE = 4

CONTROL_STATE_DODGE = 1




class Evitement:
	def __init__(self):
		self.state = STATE_STANDBYE
		self.ask_state = 0
		self.next_state = 9
		self.standed_by = True
		self.theta = 0
		self.x = 0
		self.y = 0
		self.control_state = 0
		self.saved_time = 0
		sonarProxy.subscribe("SonarApp")
	
	def test_stand_by(self):
		if self.standed_by:
			self.standed_by = True
			motionProxy.wakeUp()
			postureProxy.goToPosture("StandInit", 0.5)
			motionProxy.setWalkArmsEnabled(True, True)
			motionProxy.setMotionConfig([["ENABLE_FOOT_CONTACT_PROTECTION", True]])
			

	def run(self):	
		
		valL = memoryProxy.getData("Device/SubDeviceList/US/Left/Sensor/Value")
    		valR = memoryProxy.getData("Device/SubDeviceList/US/Right/Sensor/Value")
			
		if (valL < 0.5) or (valR < 0.5):
			self.control_state = CONTROL_STATE_DODGE
			self.save_time = time.clock()
		#sonarProxy.unsubscribe("SonarApp")
    		#print valL, valR
    		#sonarProxy.unsubscribe("SonarApp");

		if self.control_state  == CONTROL_STATE_DODGE:
			valL = memoryProxy.getData("Device/SubDeviceList/US/Left/Sensor/Value")
    			valR = memoryProxy.getData("Device/SubDeviceList/US/Right/Sensor/Value")
			
			if (valL < 1.5) or (valR < 1.5) and (time.clock() - self.saved_time) < 2:
				self.next_state = STATE_TURN_RIGHT
			else:
				self.next_state = STATE_STANDBYE
				self.control_state = 0


		if self.next_state == STATE_TURN_RIGHT:
			
			if self.state != STATE_TURN_RIGHT:
				print('VIRAGE A DROITE')
				if ((self.state != STATE_TERMINATED) and (self.state != STATE_STANDBYE)):
					print("stop move")
					motionProxy.stopMove()

				self.test_stand_by()
				motionProxy.moveInit()
				motionProxy.move(0, 0, -0.3)
			self.state = STATE_TURN_RIGHT

		elif self.next_state == STATE_STANDBYE:
			if ((self.state != STATE_TERMINATED) and (self.state != STATE_STANDBYE)):
				print("stop move")
				motionProxy.stopMove()

			if not self.standed_by:
				self.standed_bye = True
				motionProxy.rest()
			self.state = STATE_STANDBYE
				


if __name__ == "__main__":
	evitement = Evitement()
	while True:
		evitement.run()
	












