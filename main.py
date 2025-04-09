import os
from camera import Camera
from config import Config
from lane import Lane
from robot import Robot
from server import start_flask
from ultis import start_thread

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

		start_thread(Camera.capture)

		if OBSTACLE:
			start_thread(Camera.get_traffic_signs)

		if DEBUG:
			start_thread(Camera.visuals)
			start_thread(start_flask)

		print("Threads initialized")

	@staticmethod
	def init_lanes():
		for i in range(4):
			WRO.lanes.append(Lane())

WRO.init()

# get cpu temperature
t = os.popen('vcgencmd measure_temp').readline()
cpu_temp = t.replace("temp=", "").replace("'C\n", "")
print(f"CPU Temperature: {cpu_temp}°C")