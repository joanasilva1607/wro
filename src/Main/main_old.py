import time
from machine import Pin, PWM, I2C, UART

motor_dir = 1  #1: forward, -1: backward

class Motor():
	@staticmethod
	def init():
		Motor.m1 = Pin(1, Pin.OUT)      # Direction pin 1
		Motor.m2 = Pin(2, Pin.OUT)      # Direction pin 2
		Motor.m_pwm = PWM(Pin(0))      # PWM pin
		Motor.m_pwm.freq(1000)          # Set PWM frequency (adjust as needed)

	@staticmethod
	def forward(speed):
		global motor_dir
		motor_dir = 1
		Motor.m1.value(0)
		Motor.m2.value(1)
		Motor.m_pwm.duty_u16(int(speed * 65535))  # speed: 0.0 to 1.0

	@staticmethod
	def backward(speed):
		global motor_dir
		motor_dir = -1
		Motor.m1.value(1)
		Motor.m2.value(0)
		Motor.m_pwm.duty_u16(int(speed * 65535))  # speed: 0.0 to 1.0

	@staticmethod
	def stop():
		Motor.m1.value(0)
		Motor.m2.value(0)
		Motor.m_pwm.duty_u16(0)
		
class Servo:
	__servo_pwm_freq = 50
	__min_u16_duty = 1802
	__max_u16_duty = 7864
	center_steering = 91
	max_steering_offset = 11
	min_angle = center_steering - max_steering_offset
	max_angle = center_steering + max_steering_offset
	current_angle = 0.001


	def __init__(self, pin):
		self.__initialise(pin)


	def update_settings(self, servo_pwm_freq, min_u16_duty, max_u16_duty, min_angle, max_angle, pin):
		self.__servo_pwm_freq = servo_pwm_freq
		self.__min_u16_duty = min_u16_duty
		self.__max_u16_duty = max_u16_duty
		self.min_angle = min_angle
		self.max_angle = max_angle
		self.__initialise(pin)


	def move(self, angle):
		# round to 2 decimal places, so we have a chance of reducing unwanted servo adjustments
		angle = round(angle, 2)
		# do we need to move?

		if angle < self.min_angle:
			angle = self.min_angle
		elif angle > self.max_angle:
			angle = self.max_angle

		if angle == self.current_angle:
			return
		self.current_angle = angle
		# calculate the new duty cycle and move the motor
		duty_u16 = self.__angle_to_u16_duty(angle)
		self.__motor.duty_u16(duty_u16)
	
	def stop(self):
		
		self.__motor.deinit()
	
	def get_current_angle(self):
		return self.current_angle

	def __angle_to_u16_duty(self, angle):
		return int((angle - self.min_angle) * self.__angle_conversion_factor) + self.__min_u16_duty


	def __initialise(self, pin):
		self.current_angle = -0.001
		self.__angle_conversion_factor = (self.__max_u16_duty - self.__min_u16_duty) / (self.max_angle - self.min_angle)
		self.__motor = PWM(Pin(pin))
		self.__motor.freq(self.__servo_pwm_freq)

class CMPS12:
	def __init__(self, i2c=None, id=1, sda_pin=14, scl_pin=15, addr=None, reg=0x02):
		"""Initialise the CMPS12 reader.

		Args:
			i2c: optional existing I2C object (if provided, sda_pin/scl_pin/id are ignored)
			id: I2C bus id used when creating a new I2C object (default 0)
			sda_pin, scl_pin: pins to use if creating the I2C object
			addr: 7-bit I2C address of the compass; if None the driver will attempt to auto-detect
			reg: register address where the 16-bit bearing (high, low) is stored (default 1)
		"""
		if i2c is None:
			self.i2c = I2C(id, scl=Pin(scl_pin), sda=Pin(sda_pin))
		else:
			self.i2c = i2c

		self.reg = reg
		self.address = addr if addr is not None else self._auto_find_address()

	def _auto_find_address(self):
		# Common 7-bit I2C addresses for compass modules. We'll probe each
		# and pick the first that responds to a small read from the bearing reg.
		candidates = [0x60, 0x1E, 0x42, 0x0C, 0x1C]
		for a in candidates:
			try:
				# try to read two bytes from the expected register
				self.i2c.readfrom_mem(a, self.reg, 2)
				return a
			except Exception:
				pass
		# fallback default commonly used by some CMPS modules
		return 0x60

	def read_raw(self):
		"""Read raw 16-bit value from the compass register.

		Returns None on failure or an integer 0..65535 on success.
		"""
		try:
			data = self.i2c.readfrom_mem(self.address, self.reg, 2)
			if len(data) != 2:
				return None
			return (data[0] << 8) | data[1]
		except Exception:
			return None

	def get_heading(self):
		"""Return the heading in degrees (0.00 .. 359.99) if possible.

		The function attempts to interpret the 16-bit value produced by
		different compass firmwares:
		  - If value <= 36000 it's likely hundredths of a degree -> value/100
		  - If value <= 3600 it's likely tenths of a degree -> value/10
		  - Otherwise treat as raw 0..65535 mapping to 0..360 degrees
		Returns a float (degrees) or None when reading fails.
		"""
		raw = self.read_raw()
		if raw is None:
			return None

		return raw / 10.0

	def get_heading_radians(self):
		import math
		h = self.get_heading()
		return None if h is None else h * (math.pi / 180.0)

	def read_debug(self):
		"""Return (raw, degrees) for debugging or None on failure."""
		raw = self.read_raw()
		if raw is None:
			return None
		return raw, self.get_heading()



servo=Servo(pin=3)
compass = CMPS12(id=1, sda_pin=14, scl_pin=15, addr=0x60)
uart = UART(0, baudrate=115200, tx=Pin(16), rx=Pin(17))


angle_offset = compass.get_heading() + 180

Motor.init()

# GPIO pins for encoder signals
pin_a = Pin(7, Pin.IN, Pin.PULL_UP)  # A (DT)
pin_b = Pin(6, Pin.IN, Pin.PULL_UP)  # B (CLK)

position = 0  # Global position counter
last_state = pin_a.value()

def handle_encoder(pin):
	global position, last_state
	a_val = pin_a.value()


	if a_val != last_state:
		global motor_dir
		position += motor_dir # Clockwise
		last_state = a_val
	
# Set up interrupt on A signal
pin_a.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=handle_encoder)

current_val = -1

steps_per_cm = 67.28

def get_distance():
	 return position / steps_per_cm

def move_distance_cm(target_cm, relative=True):
	target_distance = 0
	inital_distance = get_distance()

	if relative:
		target_distance = get_distance() + target_cm
	else:
		target_distance = target_cm

	prev_speed = 0
	max_speed = 0.8
	min_speed = 0.2

	slow_distance = 20
	stop_distance = 5
	slowdown_started = False

	while True:
		diff = target_distance - get_distance()
		initial_diff = get_distance() - inital_distance
		
		reverse = diff < 0

		if reverse:
			diff = -diff
			initial_diff = -initial_diff


		speed = max_speed

		# No primeiros 20cm
		if initial_diff < stop_distance:
			speed = min_speed

		elif initial_diff < slow_distance:
			speed_interval = max_speed - min_speed
			distance_interval = slow_distance - stop_distance
			
			speed = min_speed + (speed_interval * (initial_diff - stop_distance) / distance_interval)


		# Quando falta < 20cm
		if diff < stop_distance:
			speed = min_speed

		elif diff < slow_distance:
			if slowdown_started == False:
				slowdown_started = True
				max_speed = prev_speed 
				
			speed_interval = max_speed - min_speed
			distance_interval = slow_distance - stop_distance
			
			speed = min_speed + (speed_interval * (diff - stop_distance) / distance_interval)

		if reverse:
			Motor.backward(speed)
		else:
			Motor.forward(speed)
	
		prev_speed = speed

		if diff <= 0:
			break
	
	Motor.stop()

def GetAngle():
		global angle_offset

		bear = compass.get_heading()
		bear -= angle_offset % 360.0

		if bear >= 360.0:
			bear -= 360.0
		elif bear <= 0:
			bear += 360.0

		return bear

def MoveLane(target_cm, relative=True,
			 clockwise=True,
			 wall_distance=50,
			 side_sonar=None,
			 compass=True,
			 sonar_multiplier=0.25,#0.35
			 compass_multiplier=0.1#0.3
			):
	

	target_distance = 0
	inital_distance = get_distance()

	if relative:
		target_distance = get_distance() + target_cm
	else:
		target_distance = target_cm

	prev_speed = 0
	max_speed = 0.8
	min_speed = 0.22

	slow_distance = 20
	stop_distance = 5
	slowdown_started = False

	dir = 0

	while True:

		if uart.any():
			data = uart.read(4)  # read 4 bytes
			frente, tras, dir, esq = data

		diff_distance = 0 if not side_sonar else (dir - wall_distance)

		if (clockwise):
			diff_distance = -diff_distance

		if abs(diff_distance) > 50:
			diff_distance = 0

		diff_compass = 0 if not compass else 180 - GetAngle()

		if compass and side_sonar:
			if abs(diff_compass) > 20:
				diff_distance = 0

		servo_angle = (diff_distance * sonar_multiplier) + (diff_compass * compass_multiplier)

		diff = target_distance - get_distance()
		initial_diff = get_distance() - inital_distance
		
		reverse = diff < 0

		if reverse:
			diff = -diff
			initial_diff = -initial_diff

		speed = max_speed

		# No primeiros 20cm
		if initial_diff < stop_distance:
			speed = min_speed

		elif initial_diff < slow_distance:
			speed_interval = max_speed - min_speed
			distance_interval = slow_distance - stop_distance
			
			speed = min_speed + (speed_interval * (initial_diff - stop_distance) / distance_interval)


		# Quando falta < 20cm
		if diff < stop_distance:
			speed = min_speed

		elif diff < slow_distance:
			if slowdown_started == False:
				slowdown_started = True
				max_speed = prev_speed 
				
			speed_interval = max_speed - min_speed
			distance_interval = slow_distance - stop_distance
			
			speed = min_speed + (speed_interval * (diff - stop_distance) / distance_interval)

		servo_angle = servo_angle/speed*max_speed
		servo_angle = int(servo.center_steering + servo_angle)

		if reverse:
			Motor.backward(speed)
			servo.move(-servo_angle)
		else:
			Motor.forward(speed)
			servo.move(servo_angle)
	
		prev_speed = speed

		time.sleep(1/1000)

		if diff <= 0:
			break
	
	Motor.stop()

def RotateAngle(angle, reverse=False, relative=True, timeout=None):
		global angle_offset

		Motor.stop()

		offset_bak = angle_offset

		if relative:
			angle_offset = compass.get_heading() + 180 + angle
		else:
			angle_offset += angle

		max_offset = 50
		margin = 1

		is_first_loop = True

		start_time = time.time()


		while True:
			interval = time.time() - start_time

	

			if timeout is not None:
				if interval > timeout:
					Motor.stop()
					servo.move(servo.center_steering)
					return

			current_bearing = GetAngle()


			if abs(current_bearing - 180) <= margin:
				Motor.stop()
				servo.move(servo.center_steering)
				break

			

			offset = current_bearing - 180

			# Clamp the offset
			if abs(offset) > max_offset:
				offset = max_offset if offset > 0 else -max_offset

			ratio = (offset / max_offset)

			angle_adjustment = ratio * Servo.max_steering_offset

			angle_min_adjustment = 3

			if abs(angle_adjustment)<angle_min_adjustment:
				if angle_adjustment<0:
					angle_adjustment=-angle_min_adjustment
				else:
					angle_adjustment=angle_min_adjustment


			if reverse:
				angle_adjustment = -angle_adjustment



			angle = int(servo.center_steering - angle_adjustment)
			servo.move(angle)

			
	


			#Wait for the servo to reach the target angle
			if is_first_loop:
				time.sleep(0.15)
				is_first_loop = False

			speed_min = 0.22
			speed_max = 0.4

			speed_range = speed_max - speed_min
			speed = speed_min + (abs(ratio) * speed_range)

			if reverse:
				Motor.backward(speed)
			else:
				Motor.forward(speed)

			time.sleep(1/5000)
		angle_offset = offset_bak


RotateAngle(90, relative=True)
#move_distance_cm(-100, relative=True)
#MoveLane(200, relative=True, side_sonar=True, clockwise=False)
# Main loop to display position
while True:
	if current_val != position:  # The encoder value has changed!
		print(f'Distance', get_distance())  # Do something with the new value
		print(f'Encoder', position)  # Do something with the new value
		current_val = position  # Track this change as the last know value
			
		print('Compass heading (deg):', '{:.2f}'.format(compass.get_heading()))

   
	time.sleep(0.5)


