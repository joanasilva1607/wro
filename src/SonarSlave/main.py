from machine import Pin, time_pulse_us, UART
import time

# Define the GPIO pins for the SRF04
echos = [Pin(8, Pin.IN, pull=Pin.PULL_DOWN), Pin(12, Pin.IN, pull=Pin.PULL_DOWN), Pin(10, Pin.IN, pull=Pin.PULL_DOWN), Pin(15, Pin.IN, pull=Pin.PULL_DOWN)]
triggers = [Pin(9, Pin.OUT), Pin(7, Pin.OUT), Pin(11, Pin.OUT), Pin(14, Pin.OUT)]

uart = UART(0, baudrate=115200, tx=Pin(16), rx=Pin(17))


def measure_distance(trigger, echo):
    # Ensure trigger is low initially
    trigger.value(0)
    time.sleep_us(2)

    # Send 10µs pulse to trigger
    trigger.value(1)
    time.sleep_us(10)
    trigger.value(0)

    try:
        # Measure the duration of the echo pulse (max wait 30ms)
        pulse_time = time_pulse_us(echo, 1, 17500)

        # Convert pulse time to distance (cm)
        distance = pulse_time / 58.0

        if distance > 250:
            distance = 250

        return int(distance)
    except:
        return -1
    
while True:
    distances = []
    for i in range(4):
        dist = measure_distance(triggers[i], echos[i])
        distances.append(dist)
        time.sleep(1/960)

    time.sleep(1/960)
    
    uart.write(bytearray(distances))