
from gpiozero import DigitalOutputDevice, PWMOutputDevice

class Motor():
	@staticmethod
	def init():
		Motor.m1 = DigitalOutputDevice(5)
		Motor.m2 = DigitalOutputDevice(6)
		Motor.m_pwm = PWMOutputDevice(13)
	
	@staticmethod
	def forward(speed):
		Motor.m1.on()
		Motor.m2.off()
		Motor.m_pwm.value = speed
	
	@staticmethod
	def backward(speed):
		Motor.m1.off()
		Motor.m2.on()
		Motor.m_pwm.value = speed
	
	@staticmethod
	def stop():
		Motor.m1.off()
		Motor.m2.off()
		Motor.m_pwm.value = 0