import time
from gpiozero import DigitalOutputDevice, DigitalInputDevice, DistanceSensor

class SRF04():
	def __init__(self, trigger, echo):
		self.trigger = DigitalOutputDevice(trigger)
		self.echo = DigitalInputDevice(echo)
		self.trigger.off()

	def getCM(self):
		self.trigger.on()
		time.sleep(0.00001)
		self.trigger.off()

		start_time = time.time()
		stop_time = start_time

		self.echo.wait_for_active()
		start_time = time.time()
		
		self.echo.wait_for_inactive()
		stop_time = time.time()
		

		elapsed = stop_time-start_time

		print("Elapsed: ", elapsed)
		distance = (elapsed * 34300)/2
		distance = round(distance, 1)

		time.sleep(1/240)

		return distance

sonar =  SRF04(14, 15)
#sensor = DistanceSensor(trigger=14, echo=15)

for i in range(10):
	#print("Distance: ", sensor.distance * 100)
	print("Distance: ", sonar.getCM())
	time.sleep(0.5)