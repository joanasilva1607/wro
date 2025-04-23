from time import sleep
from cmps12 import CMPS12

from motor import Motor
from servo import SERVO
from srf04 import SRF04, Sonar


class Robot:
	sonar = []

	@staticmethod
	def init():
		SERVO.init()
		Motor.init()
		CMPS12.init()
		SERVO.set_angle(SERVO.center)

		Robot.sonar = []

		Robot.sonar.append(SRF04(14, 15))
		Robot.sonar.append(SRF04(18, 23))
		Robot.sonar.append(SRF04(24, 25))
		Robot.sonar.append(SRF04(20, 21))
		Robot.sonar.append(SRF04(1, 16))

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
	def RotateAngle(angle, reverse=False, offset=None):
		Motor.stop()
		SERVO.set_angle(SERVO.center)
		sleep(0.5)

		Robot.angle_offset = offset if offset is not None else CMPS12.bearing3599() + 180 + angle

		max_offset = 50
		margin = 2.5

		is_first_loop = True

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

			#Wait for the servo to reach the target angle
			if is_first_loop:
				sleep(0.2)
				is_first_loop = False

			speed_min = 0.4
			speed_max = 0.6

			speed_range = speed_max - speed_min
			speed = speed_min + (abs(ratio) * speed_range)

			if reverse:
				Motor.backward(speed)
			else:
				Motor.forward(speed)

			sleep(1/1000)