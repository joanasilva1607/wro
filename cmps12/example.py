from cmps12 import CMPS12

compass = CMPS12()


print("Version ",  compass.softwareVersion())
print("Bearing(255) ", compass.bearing255())
print("Bearing(360.0) ", compass.bearing3599())
print("Pitch ", compass.pitch())
print("Roll ", compass.roll())