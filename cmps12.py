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

	def init(address=0x60, bus_num=1):
		CMPS12.bus_num = bus_num
		CMPS12.address = address
		CMPS12.bus = smbus.SMBus(bus=bus_num)

	def read_reg(reg_addr):
		try:
			return CMPS12.bus.read_byte_data(CMPS12.address, reg_addr)
		except IOError:
			print("Error Reading CMPS12")
			return 0

	def write_reg(reg_addr, value):
		try:
			CMPS12.bus.write_byte_data(CMPS12.address, reg_addr, value)
			time.sleep(0.1)
		except IOError:
			print("Error Writing CMPS12")

	def softwareVersion():
		return CMPS12.read_reg(CMPS12.CMPS12_SOFTVER)

	def bearing255():
		bear = CMPS12.read_reg(CMPS12.CMPS12_BEARING)
		return bear #Compass Bearing as a byte, i.e. 0-255 for a full circle

	def bearing3599():
		bear1 = CMPS12.read_reg(CMPS12.CMPS12_DEGBEAR)
		bear2 = CMPS12.read_reg(CMPS12.CMPS12_DEGBEAR1)
		bear = (bear1 << 8) + bear2
		bear = bear/10.0
		return bear #Compass Bearing as a word, i.e. 0-3599 for a full circle, representing 0-359.9 degrees.

	def pitch():
		pitch = CMPS12.read_reg(CMPS12.CMPS12_PITCH)
		return pitch

	def roll():
		roll = CMPS12.read_reg(CMPS12.CMPS12_ROLL)
		return roll