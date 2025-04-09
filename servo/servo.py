import serial


class SERVO():
	min=79
	mid=91
	max=103
	delay=0.002

	def __init__(self, address=0x60, bus_num=1):
		self.ser = serial.Serial("/dev/ttyAMA4", baudrate=115200, timeout=1)
		self.set_angle(self.mid)

	def set_angle(self, angle):
		if angle < self.min:
			angle = self.min
		elif angle > self.max:
			angle = self.max

		self.ser.write(bytes([angle]))