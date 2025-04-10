from time import sleep
from cmps12 import CMPS12

from motor import Motor
from servo import SERVO


class Robot:
	@staticmethod
	def init():
		SERVO.init()
		Motor.init()
		CMPS12.init()

	@staticmethod
	def GetAngle():
		bear = CMPS12.bearing3599()

		bear -= Robot.angle_offset % 360.0

		if bear >= 360.0:
			bear -= 360.0
		elif bear <= 0:
			bear += 360.0

		return bear

	@staticmethod
	def RotateAngle(angle, reverse=False):
		Robot.angle_offset = CMPS12.bearing3599() + 180 + angle

		max_offset = 50
		margin = 1

		while True:
			current_bearing = Robot.GetAngle()

			if abs(current_bearing - 180) <= margin:
				Motor.stop()
				SERVO.set_angle(SERVO.center)
				break

			offset = current_bearing - 180

			# Clamp the offset
			if abs(offset) > max_offset:
				offset = max_offset if offset > 0 else -max_offset

			ratio = (offset / max_offset)

			angle_adjustment = ratio * (SERVO.center - SERVO.min)

			if reverse:
				angle_adjustment = -angle_adjustment

			angle = int(SERVO.center - angle_adjustment)
			SERVO.set_angle(angle)

			speed_min = 0.2
			speed_max = 0.6

			speed_range = speed_max - speed_min
			speed = speed_min + (abs(ratio) * speed_range)

			if reverse:
				Motor.backward(speed)
			else:
				Motor.forward(speed)

			sleep(1/1000)
