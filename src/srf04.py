import time
from gpiozero import DigitalOutputDevice, DigitalInputDevice, DistanceSensor

class SRF04():
	distance = 0
	active = True

	def __init__(self, trigger, echo):
		self.trigger = DigitalOutputDevice(trigger)
		self.echo = DigitalInputDevice(echo)
		self.trigger.off()

	def start(self):
		while True:
			if self.active is True:
				distance = self.getCM()

				if distance < 7 or distance > 400:
					continue

				self.distance = distance
			time.sleep(1/20)

	def getCM(self):
		self.trigger.on()
		time.sleep(0.0001)
		self.trigger.off()

		start_time = time.time()
		stop_time = start_time

		self.echo.wait_for_active(timeout=0.05)
		start_time = time.time()
		
		self.echo.wait_for_inactive(timeout=0.05)
		stop_time = time.time()
		

		elapsed = stop_time-start_time

		distance = (elapsed * 34300)/2
		distance = round(distance, 1)

		return distance


class Sonar:
	#BackRight = 0
	FrontRight = 0
	Front = 1
	FrontLeft = 2
	#BackLeft = 4