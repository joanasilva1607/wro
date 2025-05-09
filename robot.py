import re
from time import sleep
import time
from cmps12 import CMPS12

from motor import Motor
from servo import SERVO
from srf04 import SRF04, Sonar


from ultis import start_thread


class Robot:
	sonar = []

	@staticmethod
	def init():
		SERVO.init()
		Motor.init()
		CMPS12.init()
		SERVO.set_angle(SERVO.center)

		Robot.sonar = []

		#Robot.sonar.append(SRF04(14, 15))
		Robot.sonar.append(SRF04(18, 23))
		Robot.sonar.append(SRF04(24, 25))
		Robot.sonar.append(SRF04(20, 21))
		#Robot.sonar.append(SRF04(1, 16))

		for sonar in Robot.sonar:
			start_thread(sonar.start)

		SERVO.set_angle(SERVO.min)
		time.sleep(0.3)
		SERVO.set_angle(SERVO.max)
		time.sleep(0.3)
		SERVO.set_angle(SERVO.min)
		time.sleep(0.3)
		SERVO.set_angle(SERVO.center)



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
	def RotateAngle(angle, reverse=False, relative=True):
		Motor.stop()

		offset_bak = Robot.angle_offset

		if relative:
			Robot.angle_offset = CMPS12.bearing3599() + 180 + angle
		else:
			Robot.angle_offset += angle

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
				sleep(0.05)
				is_first_loop = False

			speed_min = 0.4
			speed_max = 0.8

			speed_range = speed_max - speed_min
			speed = speed_min + (abs(ratio) * speed_range)

			if reverse:
				Motor.backward(speed)
			else:
				Motor.forward(speed)

			sleep(1/1000)
		Robot.angle_offset = offset_bak

	@staticmethod
	def MoveLane(wall_distance=26, 
			  timeout=None, 
			  clockwise=True, 
			  wall_distance_slowdown=70, 
			  slow_lane=False, 
			  compass=True,
			  side_sonar=None,
			  sonar_multiplier=0.25,
			  compass_multiplier=0.1, 
			  max_speed=1,
			  until_distance=14):
		start_time = time.time()

		while Robot.sonar[Sonar.Front].distance > (until_distance + 1) or Robot.sonar[Sonar.Front].distance < (until_distance - 1):

			if timeout is not None:
				interval = time.time() - start_time

				if interval > timeout:
					Motor.stop()
					return
			
			diff_distance = 0 if not side_sonar else (side_sonar.distance - wall_distance)

			if (clockwise):
				diff_distance = -diff_distance

			if abs(diff_distance) > 20:
				diff_distance = 0

			diff_compass = 0 if not compass else 180 - Robot.GetAngle()

			if compass and side_sonar:
				if abs(diff_compass) > 25:
					diff_distance = 0

			servo_angle = (diff_distance * sonar_multiplier) + (diff_compass * compass_multiplier)

			if Robot.sonar[Sonar.Front].distance < until_distance:
				servo_angle = -servo_angle

			servo_angle = int(SERVO.center + servo_angle)

			SERVO.set_angle(servo_angle)
			
			if slow_lane:
				if Robot.sonar[Sonar.Front].distance > until_distance:
					Motor.forward(0.5)
				else:
					Motor.backward(0.5)
			else:
				if Robot.sonar[Sonar.Front].distance > until_distance:
					Motor.forward(max_speed if Robot.sonar[Sonar.Front].distance > wall_distance_slowdown else 0.4)
				else:
					Motor.backward(max_speed if Robot.sonar[Sonar.Front].distance > wall_distance_slowdown else 0.4)

			time.sleep(1/60)
		end_time = time.time()

		Motor.stop()

		duration = end_time - start_time
		return duration
	
	@staticmethod
	def ObstacleCorner(last_inside=False, color_inside=None, color_outside=None, is_first_lane=False):
		Robot.RotateAngle(0, reverse=True, relative=False)
		
		if last_inside:
			Robot.MoveLane(
					until_distance=99999,
					max_speed=0.6,
					timeout=0.3
					)
		
		time.sleep(0.2)

		next_obstacle_inside = False

		if color_inside["detected"] and color_outside["detected"]:
			next_obstacle_inside=(color_inside["distance"] < color_outside["distance"])
		elif color_inside["detected"]:
			next_obstacle_inside = True
		else:
			next_obstacle_inside = False
			
		Robot.RotateAngle(-50 if next_obstacle_inside else 50, relative=True)

		Motor.forward(0.6)

		if next_obstacle_inside is False and is_first_lane:
			time.sleep(0.15)
		else:
			if next_obstacle_inside:
				time.sleep(0.6)
			else:
				while Robot.sonar[Sonar.Front].distance > 23:
					time.sleep(1/1000)
		
		Robot.RotateAngle(0, relative=False)


		return next_obstacle_inside
