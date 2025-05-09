import time
from robot import Robot
from srf04 import Sonar
from ultis import start_thread
from config import Config

from gpiozero import Button

sw1 = Button(27, pull_up=False, bounce_time=0.1)
sw2 = Button(22, pull_up=False, bounce_time=0.1)


if sw2.is_pressed:
	sw1.wait_for_active()
	print("Started")