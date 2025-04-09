from config import Config
import serial


class SERVO():
	@staticmethod
	def init():
		SERVO.ser = serial.Serial("/dev/ttyAMA4", baudrate=115200, timeout=1)

		SERVO.center = Config.config["robot"]["center_steering"]
		SERVO.min = SERVO.center - Config.config["robot"]["max_steering_offset"]
		SERVO.max = SERVO.center + Config.config["robot"]["max_steering_offset"]

		SERVO.set_angle(SERVO.center)

	@staticmethod
	def set_angle(angle):
		if angle < SERVO.min:
			angle = SERVO.min
		elif angle > SERVO.max:
			angle = SERVO.max

		SERVO.ser.write(bytes([angle]))