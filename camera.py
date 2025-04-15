import math
from time import sleep
import cv2

import numpy as np
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
		"white": {
			"detected": False,
			"mask": None,
		},
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

	left_wall = None
	right_wall = None
	top_wall = None

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
			Camera.img = cv2.resize(im_cp, (0, 0), fx=0.3, fy=0.3)
			Camera.frame += 1

	@staticmethod
	def visuals():
		Camera.wait_load()

		while True:
			img = Camera.combine_colored_masks(
				[Camera.colors[color]["mask"] for color in ["white", "green", "red"]],
				[(255, 255, 255), (0, 255, 0), (0, 0, 255)]
			)

			if Camera.left_wall is not None:
				# Draw left wall
				cv2.line(img, (Camera.left_wall[0], Camera.left_wall[1]), (Camera.left_wall[2], Camera.left_wall[3]), (255, 255, 0), 2)

			if Camera.right_wall is not None:
				# Draw right wall
				cv2.line(img, (Camera.right_wall[0], Camera.right_wall[1]), (Camera.right_wall[2], Camera.right_wall[3]), (0, 255, 255), 2)

			if Camera.top_wall is not None:
				# Draw top wall
				cv2.line(img, (Camera.top_wall[0], Camera.top_wall[1]), (Camera.top_wall[2], Camera.top_wall[3]), (255, 0, 255), 2)


			for color in ["green", "red"]:
				if Camera.colors[color]["detected"]:
					# Draw a point at the center of the detected traffic sign with it's color
					cv2.circle(img, Camera.colors[color]["center"], 5, (255, 0, 0), -1)

					# Draw a line from the center of the image to the detected traffic sign
					cv2.line(img, (img.shape[1] // 2, img.shape[0]), Camera.colors[color]["center"], (255, 0, 0), 2)


			# Draw frame number
			cv2.putText(img, f"Frame: {Camera.frame}", (5, 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)

			Camera.visuals_img = img


			sleep(1/50)

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
				Camera.colors[color]["mask"] = Camera.get_hsv_mask(hsv_img, Config.config["camera"]["colors"][color])


				if color in ["green", "red"]:
					Camera.colors[color]["detected"], Camera.colors[color]["distance"], Camera.colors[color]["angle"], Camera.colors[color]["center"]  = Camera.process_traffic_sign(Camera.colors[color]["mask"])


			lines = Camera.get_straight_lines_from_mask(Camera.colors["white"]["mask"])

			left_wall = None
			right_wall = None
			top_wall = None

			for line in lines:
				x1, y1, x2, y2, line_angle = line

				side_wall_angle = 12
				side_wall_margin = 6

				top_wall_angle = 180
				top_wall_margin = 2

				if abs(line_angle) > side_wall_angle - side_wall_margin and abs(line_angle) < side_wall_angle + side_wall_margin:
					if line_angle < 0:
						left_wall = line
					else:	
						right_wall = line

				if (line_angle + 180) > top_wall_angle - top_wall_margin and (line_angle + 180) < top_wall_angle + top_wall_margin:
					top_wall = line

			Camera.left_wall = left_wall
			Camera.right_wall = right_wall
			Camera.top_wall = top_wall

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
	def get_hsv_mask(hsv, config):
		h_min, s_min, v_min = config["lower"]
		h_max, s_max, v_max = config["upper"]

		mask = None

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

		# Erode and dilate to remove noise
		kernel = np.ones((3, 3), np.uint8)
		mask = cv2.erode(mask, kernel, iterations=1)
		mask = cv2.dilate(mask, kernel, iterations=1)

		#Close holes in mask
		kernel = np.ones((3, 3), np.uint8)
		mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
		#kernel = np.ones((5, 5), np.uint8)
		#mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

		return mask
	
	@staticmethod
	def combine_colored_masks(masks, colors):
		first_mask = None
		for mask in masks:
			if mask is not None:
				first_mask = mask
				break

		if first_mask is None:
			return None
		
		h, w = first_mask.shape
		output = np.zeros((h, w, 3), dtype=np.uint8)

		# Create a color image for this mask
		color_mask = np.zeros((h, w, 3), dtype=np.uint8)

		for mask, color in zip(masks, colors):
			if mask is None:
				continue
		
			color_mask[mask > 0] = color

		return cv2.add(output, color_mask)

	@staticmethod
	def get_straight_lines_from_mask(mask):
		edges = cv2.Canny(mask, 50, 150, apertureSize=3)

		# Hough Line Transform (returns rho, theta)
		lines = cv2.HoughLines(edges, 1, np.pi / 180, threshold=50)

		line_segments = []
		if lines is not None:
			for line in lines:
				rho, theta = line[0]
				a = np.cos(theta)
				b = np.sin(theta)
				x0 = a * rho
				y0 = b * rho

				# Calculate two points far enough to draw the line
				x1 = int(x0 + 1000 * (-b))
				y1 = int(y0 + 1000 * a)
				x2 = int(x0 - 1000 * (-b))
				y2 = int(y0 - 1000 * a)

				#calculate angle
				angle = math.degrees(math.atan2(y2 - y1, x2 - x1))

				# Normalize angle to be between -180 and 180
				if angle < -180:
					angle += 360
				elif angle > 180:
					angle -= 360
				
				line_segments.append((x1, y1, x2, y2, angle))

		return line_segments