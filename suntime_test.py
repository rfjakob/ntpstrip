#!/usr/bin/micropython

import time
import Suntime

# July 10, 2024
jul10 = time.localtime(1720645605)

print("Calculating for July 10, 2024")
print()

print("Vienna sunrise:")
sun = Suntime.Sun(48.208333, 16.373056, 2)
print(sun.get_sunrise_time(jul10))

print("North Pole sunrise:")
sun = Suntime.Sun(89, 16.373056, 0)
try:
	print(sun.get_sunrise_time(jul10))
except Exception as e:
	print(type(e), e)

print("South Pole sunrise:")
sun = Suntime.Sun(-89, 16.373056, 0)
try:
	print(sun.get_sunrise_time(jul10))
except Exception as e:
	print(type(e), e)
