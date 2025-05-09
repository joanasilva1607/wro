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


from gpiozero import Button

sw1 = Button(27, pull_up=False, bounce_time=0.1)
sw2 = Button(22, pull_up=False, bounce_time=0.1)


if not sw2.is_pressed:
	quit()

def ExitRobot():
	Motor.stop()
	os._exit(1)

sw2.when_deactivated = ExitRobot


DEBUG = False
OBSTACLE = False
RUN = True

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

		if RUN:
			sw1.wait_for_active()
			time.sleep(1.5)
			if OBSTACLE:
				print("Obstacle Challenge")
				WRO.obstacle_challenge()
			else:
				print("Open Challenge")
				WRO.open_challenge()

		print("Threads initialized")

	@staticmethod
	def open_challenge():
		parking_lane_offset = 0
		wall_distance = 26

		WRO.front_sonar = Robot.sonar[Sonar.Front]
		WRO.side_sonar  = None

		start_position_vertical = None
		start_position_horizontal = None

		time.sleep(1)

		side_distance_left = Robot.sonar[Sonar.FrontLeft].distance
		side_distance_right = Robot.sonar[Sonar.FrontRight].distance


		while WRO.current_lane < 13:
			#Calculate horizontal start position
			if WRO.current_lane == 0:
				side_distance = side_distance_left if WRO.clockwise else side_distance_right
				if side_distance < 40:
					start_position_horizontal = 0
				elif side_distance < 60:
					start_position_horizontal = 1
				else:
					start_position_horizontal = 2

			if WRO.current_lane == 0 or WRO.current_lane == 12:
				match start_position_horizontal:
					case 0:
						wall_distance = 26
					case 1:
						wall_distance = 40
					#case 2:11
					case _:
						wall_distance = 60
			else:
				wall_distance = 26

			Robot.angle_offset = CMPS12.bearing3599() + 180

			if WRO.current_lane == 0 or WRO.current_lane == 12:
				parking_lane_offset = Robot.angle_offset

			timeout = None

			if WRO.current_lane == 12:
				timeout = (1.5 if start_position_vertical == 0 else 2)

			duration = Robot.MoveLane(timeout=timeout, 
							 wall_distance=wall_distance, 
							 clockwise=WRO.clockwise,
							 wall_distance_slowdown=40,
							 #slow_lane=(WRO.current_lane == 0 or WRO.current_lane == 12),
							 side_sonar=WRO.side_sonar)

			if WRO.current_lane == 0:
				if duration < 6:
					start_position_vertical = 1
				else:
					start_position_vertical = 0

			Motor.stop()
			SERVO.set_angle(SERVO.center)
			time.sleep(0.05)

			if WRO.current_lane == 0:
				WRO.clockwise = Robot.sonar[Sonar.FrontLeft].distance < Robot.sonar[Sonar.FrontRight].distance
				WRO.side_sonar = Robot.sonar[Sonar.FrontLeft] if WRO.clockwise else Robot.sonar[Sonar.FrontRight]

			if start_position_horizontal > 0:
				if WRO.current_lane == 11:
					Motor.backward(0.3)
					time.sleep(1.5 if start_position_vertical == 1 else 2.5)
					Motor.stop()
					time.sleep(0.2)

			Robot.RotateAngle(90 if WRO.clockwise else -90, reverse=True)

			WRO.current_lane += 1
			WRO.current_lap = int(WRO.current_lane / 4)
		Motor.stop()

	@staticmethod
	def obstacle_challenge():
		sonar_multiplier = 0.25
		parking_lane_offset =  CMPS12.bearing3599() + 180
		compass_offset = parking_lane_offset
		Robot.angle_offset = compass_offset
		
		WRO.clockwise = Robot.sonar[Sonar.FrontLeft].distance < Robot.sonar[Sonar.FrontRight].distance
		WRO.side_sonar = Robot.sonar[Sonar.FrontLeft] if WRO.clockwise else Robot.sonar[Sonar.FrontRight]

		if WRO.clockwise:
			Robot.sonar[Sonar.FrontRight].active = False
		else:
			Robot.sonar[Sonar.FrontLeft].active = False

		WRO.front_sonar = Robot.sonar[Sonar.Front]

		#Setup Colors
		color_outside = Camera.colors["green"] if WRO.clockwise else Camera.colors["red"]
		color_inside = Camera.colors["red"] if WRO.clockwise else Camera.colors["green"]

		# Sair do estacionamento
		Robot.RotateAngle(60 if WRO.clockwise else -60)
		
		time.sleep(1/5)

		previous_lane_alignment = False

		if color_inside["detected"] and color_outside["detected"]:
			previous_lane_alignment=(color_inside["distance"] < color_outside["distance"])
		elif color_inside["detected"]:
			previous_lane_alignment = True
		else:
			previous_lane_alignment = False

		if previous_lane_alignment:
			if color_inside["distance"] > 400:
				previous_lane_alignment = False

		#Sair estacionamento
		if previous_lane_alignment:
			Robot.RotateAngle(30 if WRO.clockwise else -30)
			Motor.forward(0.55)
			time.sleep(0.5)
			Robot.RotateAngle(0, relative=False)
		else:
			Robot.RotateAngle(0, relative=False)


		inside = 75
		outside = 25
		outside_parking = 35

		wall_distance = inside if previous_lane_alignment else outside_parking


		Robot.MoveLane(wall_distance=wall_distance,
			side_sonar=WRO.side_sonar,
			sonar_multiplier=sonar_multiplier,
			clockwise=WRO.clockwise,
			until_distance=15,
			max_speed=0.6,
			wall_distance_slowdown=40
			)
		
		time.sleep(0.5)
		
		Robot.MoveLane(wall_distance=wall_distance,
			side_sonar=WRO.side_sonar,
			sonar_multiplier=sonar_multiplier,
			clockwise=WRO.clockwise,
			until_distance=35,
			max_speed=0.5
			)

		WRO.current_lane = 1

		while True:
			compass_offset += 90 if WRO.clockwise else -90
			Robot.angle_offset = compass_offset


			is_first_lane = WRO.current_lane % 4 == 0	

			print(f"Current lane: {WRO.current_lane} Current lap: {WRO.current_lap}")

			next_obstacle_inside = Robot.ObstacleCorner(
						last_inside=previous_lane_alignment, 
						color_inside=color_inside, 
						color_outside=color_outside,
						is_first_lane=is_first_lane
						)
			
			wall_distance = inside if next_obstacle_inside else (outside_parking if is_first_lane else outside)

			Robot.MoveLane(wall_distance=wall_distance,
					clockwise=WRO.clockwise, 
					side_sonar=WRO.side_sonar,
					sonar_multiplier=sonar_multiplier,
					max_speed=0.7,
					timeout=1.4,
					)
			
			if WRO.current_lane == 12:
				Motor.stop()
				break

			
			Robot.RotateAngle(15 if next_obstacle_inside else -15, relative=False)
			time.sleep(1/2)

			previous_lane_alignment = next_obstacle_inside
			next_obstacle_inside = False

			if color_inside["detected"] and color_outside["detected"]:
				next_obstacle_inside=(color_inside["distance"] < color_outside["distance"])
			elif color_inside["detected"]:
				next_obstacle_inside = True
			else:
				next_obstacle_inside = False


			if next_obstacle_inside != previous_lane_alignment:
				Robot.RotateAngle(-60 if next_obstacle_inside else 60, relative=False)

				Motor.forward(0.6)
				if next_obstacle_inside is False and is_first_lane:
					time.sleep(0.6)
				else:
					while Robot.sonar[Sonar.Front].distance > 23:
						time.sleep(1/1000)

			Robot.RotateAngle(0, relative=False)

			wall_distance = inside if next_obstacle_inside else (outside_parking if is_first_lane else outside)

			Robot.MoveLane(wall_distance=wall_distance,
					clockwise=WRO.clockwise, 
					side_sonar=WRO.side_sonar,
					sonar_multiplier=sonar_multiplier,
					max_speed=0.6,
					until_distance=13,
					wall_distance_slowdown=30
					)
			
			Robot.MoveLane(wall_distance=wall_distance,
					clockwise=WRO.clockwise, 
					side_sonar=WRO.side_sonar,
					sonar_multiplier=sonar_multiplier,
					max_speed=0.5,
					until_distance=40
					)
			
			
			previous_lane_alignment = next_obstacle_inside
			WRO.current_lane += 1
			WRO.current_lap = int(WRO.current_lane / 4)
		

	@staticmethod
	def init_lanes():
		for i in range(4):
			WRO.lanes.append(Lane())

WRO.init()

# get cpu temperature
t = os.popen('vcgencmd measure_temp').readline()
cpu_temp = t.replace("temp=", "").replace("'C\n", "")
print(f"CPU Temperature: {cpu_temp}°C")