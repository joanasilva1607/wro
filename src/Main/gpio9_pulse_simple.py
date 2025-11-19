#!/usr/bin/env python3
"""
Simple GPIO9 Pulse Detector - REPL friendly version
Quick test to see if GPIO9 is receiving pulses
"""

import time
from machine import Pin

# Initialize GPIO9
pin = Pin(9, Pin.IN)
print("GPIO9 initialized. Current state:", pin.value())

# Statistics
rising_count = 0
falling_count = 0
last_state = pin.value()
last_rising_time = None
periods = []

def handle_interrupt(p):
    global rising_count, falling_count, last_state, last_rising_time, periods
    current_time = time.ticks_us()
    new_state = p.value()
    
    if new_state == 1 and last_state == 0:  # Rising edge
        rising_count += 1
        if last_rising_time is not None:
            period = time.ticks_diff(current_time, last_rising_time)
            periods.append(period)
            if len(periods) > 100:
                periods.pop(0)
        last_rising_time = current_time
        print(f"RISING EDGE #{rising_count}")
    
    elif new_state == 0 and last_state == 1:  # Falling edge
        falling_count += 1
        print(f"FALLING EDGE #{falling_count}")
    
    last_state = new_state

# Enable interrupts
pin.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=handle_interrupt)
print("Interrupts enabled. Monitoring GPIO9...")
print("Press Ctrl+C to stop")

try:
    while True:
        time.sleep(1)
        if periods:
            avg_period = sum(periods) / len(periods)
            freq = 1000000.0 / avg_period if avg_period > 0 else 0
            print(f"Stats: {rising_count} rising, {falling_count} falling, ~{freq:.2f}Hz")
        else:
            print(f"Stats: {rising_count} rising, {falling_count} falling, no frequency data yet")
except KeyboardInterrupt:
    print("\nStopped")
    pin.irq(handler=None)




