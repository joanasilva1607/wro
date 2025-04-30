from time import sleep
import time
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

		Robot.angle_offset = (offset if offset is not None else CMPS12.bearing3599() + 180) + angle

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

			speed_min = 0.3
			speed_max = 0.5

			speed_range = speed_max - speed_min
			speed = speed_min + (abs(ratio) * speed_range)

			if reverse:
				Motor.backward(speed)
			else:
				Motor.forward(speed)

			sleep(1/1000)

	@staticmethod
	def MoveLane(wall_distance=26, timeout=None, clockwise=True, wall_distance_slowdown=70, slow_lane=False, compass=True, side_sonar=None):
		start_time = time.time()
		while Robot.sonar[Sonar.Front].distance > 14:

			if timeout is not None:
				interval = time.time() - start_time

				if interval > timeout:
					Motor.stop()
					return
			
			diff_distance = 0 if not side_sonar else (side_sonar.distance - wall_distance)

			if (clockwise):
				diff_distance = -diff_distance

			diff_compass = 0 if not compass else 180 - Robot.GetAngle()

			servo_angle = (diff_distance * 0.25) + (diff_compass * 0.2)
			servo_angle = int(SERVO.center + servo_angle)

			SERVO.set_angle(servo_angle)
			
			if slow_lane:
				Motor.forward(0.3)
			else:
				Motor.forward(1 if Robot.sonar[Sonar.Front].distance > wall_distance_slowdown else 0.45)

			time.sleep(1/20)
		end_time = time.time()

		duration = end_time - start_time
		return duration