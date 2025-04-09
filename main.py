import os
from camera import Camera
from config import Config
from server import start_flask
from ultis import start_thread


DEBUG = True


Config.init()
Camera.init()

if DEBUG:
	start_thread(start_flask)

# get cpu temperature
t = os.popen('vcgencmd measure_temp').readline()
cpu_temp = t.replace("temp=", "").replace("'C\n", "")
print(f"CPU Temperature: {cpu_temp}°C")