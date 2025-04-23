from asyncio import FIRST_COMPLETED
import os
import time
from camera import Camera
from config import Config
from lane import Lane
from motor import Motor
from robot import Robot
from mycontroller import init_my_controller
from server import start_flask
from servo import SERVO
from srf04 import Sonar
from ultis import start_thread
from cmps12 import CMPS12

DEBUG = True
OBSTACLE = True

class WRO:
	clockwise = True
	current_lane = 0
	current_lap = 0

	lanes = []

	@staticmethod
	def init():
		WRO.init_lanes()

		Config.init()
		Camera.init()
		Robot.init()

		if OBSTACLE:
			start_thread(Camera.capture)
			start_thread(Camera.get_traffic_signs)

		if DEBUG:
			start_thread(Camera.visuals)
			start_thread(start_flask)
			start_thread(init_my_controller)

		time.sleep(1)

		if OBSTACLE:
			WRO.obstacle_challenge()
		else:
			print("Open Challenge")
			WRO.open_challenge()

		print("Threads initialized")

	@staticmethod
	def open_challenge():
		wall_distance = 26
		wall_distance_slowdown = 70

		parking_lane_offset = 0



		start_position_vertical = None
		start_position_horizontal = None

		WRO.front_sonar = Robot.sonar[Sonar.Front]
		
		WRO.side_sonar = WRO.front_sonar

		start_thread(WRO.front_sonar.start)

		time.sleep(1)

		if WRO.side_sonar.distance < 40:
			start_position_horizontal = 0
		elif WRO.side_sonar.distance < 60:
			start_position_horizontal = 1
		else:
			start_position_horizontal = 2

		while WRO.current_lap < 4:
			if WRO.current_lane == 0 or WRO.current_lane == 12:
				match start_position_horizontal:
					case 0:
						wall_distance = 26
					case 1:
						wall_distance = 40
					#case 2:
					case _:
						wall_distance = 60
			else:
				wall_distance = 26


			Robot.angle_offset = CMPS12.bearing3599() + 180

			if WRO.current_lane == 0:
				parking_lane_offset = Robot.angle_offset

			if WRO.current_lane == 12:
				Robot.angle_offset = parking_lane_offset

			start_time = time.time()
			while WRO.front_sonar.distance > 14:
				if WRO.current_lane == 12:
					interval = time.time() - start_time

					if interval > (4.3 if start_position_vertical == 0 else 7.5):
						Motor.stop()
						return
				
				# Seguir parede até canto
				diff_distance = WRO.side_sonar.distance - wall_distance

				if WRO.current_lane == 0:
					diff_distance = 0

				if (WRO.clockwise):
					diff_distance = -diff_distance

				diff_compass = 180 - Robot.GetAngle()

				servo_angle = (diff_distance * 0.25) + (diff_compass * 0.2)
				servo_angle = int(SERVO.center + servo_angle)

				SERVO.set_angle(servo_angle)
				
				if WRO.current_lane == 0 or WRO.current_lane == 12 or (WRO.front_sonar.distance < wall_distance_slowdown and WRO.current_lane == 11):
					Motor.forward(0.3)
				else:
					Motor.forward(1 if WRO.front_sonar.distance > wall_distance_slowdown else 0.45)

				time.sleep(1/20)
			end_time = time.time()

			duration = end_time - start_time

			if WRO.current_lane == 0:
				print(duration)
				if duration < 6:
					print("Second half")
					start_position_vertical = 1
				else:
					print("First half")
					start_position_vertical = 0

			Motor.stop()
			SERVO.set_angle(SERVO.center)
			time.sleep(0.25)

			if WRO.current_lane == 0:
				WRO.clockwise = Robot.sonar[Sonar.FrontLeft].getCM() < Robot.sonar[Sonar.FrontRight].getCM()

				WRO.side_sonar = Robot.sonar[Sonar.FrontLeft] if WRO.clockwise else Robot.sonar[Sonar.FrontRight]
				start_thread(WRO.side_sonar.start)
				time.sleep(1)

			if start_position_horizontal > 0:
				if WRO.current_lane == 11:
					Motor.backward(0.3)
					time.sleep(1.5 if start_position_vertical == 1 else 2.5)
					Motor.stop()
					time.sleep(0.2)

			Robot.RotateAngle(90 if WRO.clockwise else -90, reverse=True)
			time.sleep(0.25)
			Motor.forward(0.5)
			time.sleep(0.5)

			WRO.current_lane += 1
			WRO.current_lap = int(WRO.current_lane / 4)

	@staticmethod
	def obstacle_challenge():
		parking_lane_offset =  CMPS12.bearing3599() + 180
		
		WRO.clockwise = Robot.sonar[Sonar.FrontLeft].getCM() < Robot.sonar[Sonar.FrontRight].getCM()
		WRO.side_sonar = Robot.sonar[Sonar.FrontLeft] if WRO.clockwise else Robot.sonar[Sonar.FrontRight]

		WRO.front_sonar = Robot.sonar[Sonar.Front]

		start_thread(WRO.side_sonar.start)
		start_thread(WRO.front_sonar.start)

		#Setup Colors
		color_outside = Camera.colors["green"] if WRO.clockwise else Camera.colors["red"]
		color_inside = Camera.colors["red"] if WRO.clockwise else Camera.colors["green"]

		# Sair do estacionamento
		Robot.RotateAngle(70 if WRO.clockwise else -70, offset=parking_lane_offset)
		
		time.sleep(0.5)

		#Sair estacionamento
		if color_inside["detected"]:
			Robot.RotateAngle(30 if WRO.clockwise else -30)
			time.sleep(0.2)
			Motor.forward(0.7)
			time.sleep(0.4)
			Robot.RotateAngle(0, offset=parking_lane_offset)
			time.sleep(1)
		else:
			Robot.RotateAngle(0, offset=parking_lane_offset)

		# 80 dentro
		# 20 fora
		# 40 fora com estacionamento


	@staticmethod
	def init_lanes():
		for i in range(4):
			WRO.lanes.append(Lane())

WRO.init()

# get cpu temperature
t = os.popen('vcgencmd measure_temp').readline()
cpu_temp = t.replace("temp=", "").replace("'C\n", "")
print(f"CPU Temperature: {cpu_temp}°C")