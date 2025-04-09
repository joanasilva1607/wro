from cmps12.cmps12 import CMPS12

from robot.motor.motor import Motor
from servo.servo import SERVO


class Robot:
	@staticmethod
	def init():
		Robot.servo = SERVO()
		Robot.motor = Motor()