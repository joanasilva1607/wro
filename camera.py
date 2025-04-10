import math
from time import sleep
import cv2

from picamera2 import Picamera2

from config import Config
from ultis import printAngle

import os

os.environ['LIBCAMERA_LOG_LEVELS'] = '4'

class Camera:
	img = None
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
		},
		"white": {
			"detected": False,
			"mask": None,
		}
	}

	@staticmethod
	def init():
		Camera.picam2 = Picamera2()
		
		Camera.picam2.configure(Camera.picam2.create_preview_configuration(main={
				"format": 'RGB888', 
				"size": (1537, 864)
			}, 
			controls={
				'FrameRate': 60, 
				"AwbEnable": False, 
				"Brightness": Config.config["camera"]["brightness"],
		}))

	@staticmethod
	def wait_load():
		while Camera.img is None:
			sleep(0.1)

	@staticmethod
	def capture():
		Camera.picam2.start()

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
			else:
				sleep(1/60)
				continue

			img = Camera.img.copy()

			# Draw Floor over img
			white = Camera.colors["white"].copy()
			if white["mask"] is not None:
				img = cv2.addWeighted(img, 1, white["mask"], 1, 0)

			for color in ["green", "red"]:
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
				sleep(1/240)
				continue

			hsv_img = cv2.cvtColor(Camera.img.copy(), cv2.COLOR_BGR2HSV)

			for color in Camera.colors:
				Camera.colors[color]["mask"] = Camera.get_hsv_mask_from_config(hsv_img, Config.config["camera"]["colors"][color])


				if color in ["green", "red"]:
					Camera.colors[color]["detected"], Camera.colors[color]["distance"], Camera.colors[color]["angle"], Camera.colors[color]["center"]  = Camera.process_traffic_sign(Camera.colors[color]["mask"])

			#closest_color = Camera.colors["green"] if Camera.colors["green"]["distance"] < Camera.colors["red"]["distance"] else Camera.colors["red"]

	@staticmethod
	def process_traffic_sign(mask):
		biggest_contour = None

		# Find biggest countour
		contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		if len(contours) != 0:
			biggest_contour = max(contours, key=cv2.contourArea)

		if biggest_contour is None:
			return None, 9999999, None, None

		x, y, w, h = cv2.boundingRect(biggest_contour)
		center_x = x + w // 2
		center_y = y + h

		if center_x == mask.shape[1] // 2:
			center_x += 1

		if center_y == mask.shape[0]:
			center_y += 1

		A = (mask.shape[1] // 2, mask.shape[0])
		B = (center_x, mask.shape[0])
		C = (center_x, center_y)

		line_angle, _, _ = printAngle(A, B, C)

		line_angle = 90 - line_angle

		if (center_x - mask.shape[1] // 2) < 0:
			line_angle = -line_angle

		line_distance = math.sqrt((center_x - mask.shape[1] // 2) ** 2 + (center_y - mask.shape[0]) ** 2)

		return True, line_distance, line_angle, (center_x, center_y)
	
	@staticmethod
	def get_hsv_mask_from_config(hsv, config):
		h_min, s_min, v_min = config["lower"]
		h_max, s_max, v_max = config["upper"]

		# HUE mask
		if h_min > h_max:
			mask1 = cv2.inRange(hsv, (0, 0, 0), (h_max, 255, 255))
			mask2 = cv2.inRange(hsv, (h_min, 0, 0), (179, 255, 255))
			h_mask = cv2.bitwise_or(mask1, mask2)
		else:
			h_mask = cv2.inRange(hsv, (h_min, 0, 0), (h_max, 255, 255))

		# SATURATION mask
		if s_min > s_max:
			mask1 = cv2.inRange(hsv, (0, 0, 0), (179, s_max, 255))
			mask2 = cv2.inRange(hsv, (0, s_min, 0), (179, 255, 255))
			s_mask = cv2.bitwise_or(mask1, mask2)
		else:
			s_mask = cv2.inRange(hsv, (0, s_min, 0), (179, s_max, 255))

		# VALUE mask
		if v_min > v_max:
			mask1 = cv2.inRange(hsv, (0, 0, 0), (179, 255, v_max))
			mask2 = cv2.inRange(hsv, (0, 0, v_min), (179, 255, 255))
			v_mask = cv2.bitwise_or(mask1, mask2)
		else:
			v_mask = cv2.inRange(hsv, (0, 0, v_min), (179, 255, v_max))

		# Combine all
		mask = cv2.bitwise_and(h_mask, s_mask)
		mask = cv2.bitwise_and(mask, v_mask)
		return mask