import math
from time import sleep
import cv2

from picamera2 import Picamera2

from config import Config
from ultis import printAngle, start_thread


class Camera:
	img = None
	hsv_img = None
	visuals_img = None

	frame = 0

	colors = {
		"green": {
			"detected": False,
			"angle": 0,
			"distance": 0,
			"center": (0, 0),
			"mask": None,
		},
		"red": {
			"detected": False,
			"angle": 0,
			"distance": 0,
			"center": (0, 0),
			"mask": None,
		}
	}

	@staticmethod
	def init():
		Camera.picam2 = Picamera2()
		Camera.picam2.configure(Camera.picam2.create_preview_configuration(main={"format": 'RGB888', "size": (1537, 864)}, controls={'FrameRate': 60}))

		Camera.picam2.start()

		start_thread(Camera.capture)
		start_thread(Camera.get_traffic_signs)

	@staticmethod
	def wait_load():
		while Camera.img is None:
			sleep(0.1)

	@staticmethod
	def capture():
		while True:
			crop = Config.config["camera"]["crop"]

			im_cp = Camera.picam2.capture_array()

			# Crop top half of image
			im_cp = im_cp[crop["top"]:crop["height"], crop["left"]:crop["width"]]

			# Scale image down to 1/2
			Camera.img = cv2.resize(im_cp, (0, 0), fx=0.25, fy=0.25)
			Camera.frame += 1

	@staticmethod
	def visuals():
		last_frame = 0

		Camera.wait_load()

		while True:
			if Camera.frame != last_frame:
				last_frame = Camera.frame

			img = Camera.img.copy()

			for color in Camera.colors:
				if Camera.colors[color]["detected"]:
					# Draw a point at the center of the detected traffic sign with it's color
					cv2.circle(img, Camera.colors[color]["center"], 5, (255, 0, 0), -1)

					# Draw a line from the center of the image to the detected traffic sign
					cv2.line(img, (img.shape[1] // 2, img.shape[0]), Camera.colors[color]["center"], (255, 0, 0), 2)

			Camera.visuals_img = img

	@staticmethod
	def get_frame(frame):
		# Convert the image to JPEG format
		ret, jpeg = cv2.imencode('.jpg', frame)
		if not ret:
			return None

		# Return the image as a byte array
		return jpeg.tobytes()
	
	@staticmethod
	def get_traffic_signs():
		last_frame = 0

		Camera.wait_load()

		while True:
			if Camera.frame != last_frame:
				last_frame = Camera.frame
			else:
				sleep(1/180)
				continue

			Camera.hsv_img = cv2.cvtColor(Camera.img, cv2.COLOR_BGR2HSV)

			for color in Camera.colors:
				Camera.colors[color]["detected"], Camera.colors[color]["mask"], Camera.colors[color]["distance"], Camera.colors[color]["angle"], Camera.colors[color]["center"]  = Camera.process_traffic_sign(Config.config["camera"]["colors"][color])

			#closest_color = Camera.colors["green"] if Camera.colors["green"]["distance"] < Camera.colors["red"]["distance"] else Camera.colors["red"]

	@staticmethod
	def process_traffic_sign(config):
		hsv =  Camera.hsv_img
		im = Camera.img

		h_min = config["lower"][0]
		h_max = config["upper"][0]
		s_min = config["lower"][1]
		s_max = config["upper"][1]
		v_min = config["lower"][2]
		v_max = config["upper"][2]

		if h_min > h_max:
			lower1 = (0, 0, 0)
			upper1 = (h_max, 255, 255)
			mask1 = cv2.inRange(hsv, lower1, upper1)

			lower2 = (h_min, 0, 0)
			upper2 = (179, 255, 255)
			mask2 = cv2.inRange(hsv, lower2, upper2)

			mask = cv2.bitwise_or(mask1, mask2)
		else:
			lower = (h_min, 0, 0)
			upper = (h_max, 255, 255)

			mask = cv2.inRange(hsv, lower, upper)

		if s_min > s_max:
			lower1 = (0, 0, 0)
			upper1 = (179, s_max, 255)
			mask1 = cv2.inRange(hsv, lower1, upper1)

			lower2 = (0, s_min, 0)
			upper2 = (179, 255, 255)
			mask2 = cv2.inRange(hsv, lower2, upper2)

			mask3 = cv2.bitwise_or(mask1, mask2)
			mask = cv2.bitwise_and(mask, mask3)
		else:
			lower = (0, s_min, 0)
			upper = (179, s_max, 255)
			mask1 = cv2.inRange(hsv, lower, upper)
			mask = cv2.bitwise_and(mask, mask1)

		if v_min > v_max:
			lower1 = (0, 0, 0)
			upper1 = (179, 255, v_max)
			mask1 = cv2.inRange(hsv, lower1, upper1)

			lower2 = (0, 0, v_min)
			upper2 = (179, 255, 255)
			mask2 = cv2.inRange(hsv, lower2, upper2)

			mask3 = cv2.bitwise_or(mask1, mask2)
			mask = cv2.bitwise_and(mask, mask3)
		else:
			lower = (0, 0, v_min)
			upper = (179, 255, v_max)
			mask1 = cv2.inRange(hsv, lower, upper)
			mask = cv2.bitwise_and(mask, mask1)


		biggest_contour = None

		# Find biggest countour
		contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		if len(contours) != 0:
			biggest_contour = max(contours, key=cv2.contourArea)

		if biggest_contour is None:
			return None, mask, 9999999, None, None

		x, y, w, h = cv2.boundingRect(biggest_contour)
		center_x = x + w // 2
		center_y = y + h

		if center_x == im.shape[1] // 2:
			center_x += 1

		if center_y == im.shape[0]:
			center_y += 1

		A = (im.shape[1] // 2, im.shape[0])
		B = (center_x, im.shape[0])
		C = (center_x, center_y)

		line_angle, _, _ = printAngle(A, B, C)

		line_angle = 90 - line_angle

		if (center_x - im.shape[1] // 2) < 0:
			line_angle = -line_angle

		line_distance = math.sqrt((center_x - im.shape[1] // 2) ** 2 + (center_y - im.shape[0]) ** 2)

		return True, mask, line_distance, line_angle, (center_x, center_y)