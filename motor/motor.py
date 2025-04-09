
from gpiozero import DigitalOutputDevice, PWMOutputDevice

class Motor():
	def __init__(self):
		self.m1 = DigitalOutputDevice(5)
		self.m2 = DigitalOutputDevice(6)
		self.m_pwm = PWMOutputDevice(13)

	def forward(self, speed):
		self.m1.on()
		self.m2.off()
		self.m_pwm.value = speed

	def backward(self, speed):
		self.m1.off()
		self.m2.on()
		self.m_pwm.value = speed

	def stop(self):
		self.m1.off()
		self.m2.off()
		self.m_pwm.value = 0