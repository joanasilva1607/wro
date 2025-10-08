# Simple REPL Compass Test
# Copy and paste this into your MicroPython REPL

from machine import Pin, I2C
import time

# Initialize I2C
print("Initializing I2C...")
i2c = I2C(1, scl=Pin(15), sda=Pin(14))

# Scan for devices
print("Scanning I2C bus...")
devices = i2c.scan()
print(f"Found devices: {[hex(d) for d in devices]}")

if not devices:
    print("ERROR: No I2C devices found!")
    print("Check connections:")
    print("- SDA to pin 14")
    print("- SCL to pin 15") 
    print("- Power to compass")
else:
    # Test compass reading
    compass_addr = 0x60  # CMPS12 default
    compass_reg = 0x02   # Bearing register
    
    if compass_addr in devices:
        print(f"Found compass at {hex(compass_addr)}")
    else:
        print(f"Compass not at expected address {hex(compass_addr)}")
        print("Trying first found device...")
        compass_addr = devices[0]
    
    print(f"Testing compass at {hex(compass_addr)}...")
    
    # Take readings
    for i in range(10):
        try:
            data = i2c.readfrom_mem(compass_addr, compass_reg, 2)
            raw = (data[0] << 8) | data[1]
            heading = raw / 10.0
            print(f"Reading {i+1}: {heading:.1f}° (raw: {raw})")
        except Exception as e:
            print(f"Reading {i+1}: FAILED - {e}")
        time.sleep(0.5)
