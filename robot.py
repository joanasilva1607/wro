from cmps12 import CMPS12

from motor import Motor
from servo import SERVO


class Robot:
	@staticmethod
	def init():
		SERVO.init()
		Motor.init()
		CMPS12.init()