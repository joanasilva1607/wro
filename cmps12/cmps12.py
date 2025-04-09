import smbus
import time

class CMPS12():
	CMPS12_SOFTVER = 0

	CMPS12_BEARING = 1
	CMPS12_DEGBEAR = 2
	CMPS12_DEGBEAR1 = 3
	CMPS12_PITCH = 4
	CMPS12_ROLL = 5

	CMPS12_REGADDR = 22

	def __init__(self, address=0x60, bus_num=1):
		self.bus_num = bus_num
		self.address = address
		self.bus = smbus.SMBus(bus=bus_num)

	def read_reg(self, reg_addr):
		try:
			return self.bus.read_byte_data(self.address, reg_addr)
		except IOError:
			print("Error Reading CMPS12")
			return 0

	def write_reg(self, reg_addr, value):
		try:
			self.bus.write_byte_data(self.address, reg_addr, value)
			time.sleep(0.1)
		except IOError:
			print("Error Writing CMPS12")

	def softwareVersion(self):
		return self.read_reg(self.CMPS12_SOFTVER)

	def bearing255(self):
		bear = self.read_reg(self.CMPS12_BEARING)
		return bear #Compass Bearing as a byte, i.e. 0-255 for a full circle

	def bearing3599(self):
		bear1 = self.read_reg(self.CMPS12_DEGBEAR)
		bear2 = self.read_reg(self.CMPS12_DEGBEAR1)
		bear = (bear1 << 8) + bear2
		bear = bear/10.0
		return bear #Compass Bearing as a word, i.e. 0-3599 for a full circle, representing 0-359.9 degrees.

	def pitch(self):
		pitch = self.read_reg(self.CMPS12_PITCH)
		return pitch

	def roll(self):
		roll = self.read_reg(self.CMPS12_ROLL)
		return roll