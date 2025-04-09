import copy
import json
from time import sleep
from ultis import start_thread


class Config:
	config = {
		"camera": {
			"crop": {
				"left": 0,
				"top": 280,
				"width": 1537,
				"height": 864
			},
			"colors": {
				"green": {
					"lower": [
						51,
						134,
						15
					],
					"upper": [
						77,
						255,
						255
					]
				},
				"red": {
					"lower": [
						9,
						134,
						24
					],
					"upper": [
						77,
						255,
						255
					]
				}
			}
		}
	}

	@staticmethod
	def init():
		try:
			with open("./config.json") as f:
				Config.config = json.load(f)
		except FileNotFoundError:
			Config.save_config()
			print("Config file not found. Created a new one with default settings.")
		except json.JSONDecodeError:
			print("Config file is corrupted. Please check the file format.")
			Config.save_config()
			print("Created a new config file with default settings.")

		Config.old_config = copy.deepcopy(Config.config)  # Use deep copy here

	@staticmethod
	def load_config():
		with open("./config.json") as f:
			Config.config = json.load(f)
	
	@staticmethod
	def save_config():
		with open("./config.json", "w") as f:
			json.dump(Config.config, f, indent=4)