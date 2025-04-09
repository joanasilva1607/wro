from time import sleep
from servo import SERVO

servo = SERVO()

min=79
mid=91
max=103

sleep(2)

while True:
    for i in range(min, max+1):
        servo.set_angle(i)
        sleep(0.015)

    for i in range(max, min-1, -1):
        servo.set_angle(i)
        sleep(0.015)