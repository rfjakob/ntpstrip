# Prints 24 lines of the year 2025 sun progression as ascii art

import config
import main
import neopixel
import Suntime
import time

sunrise = main.TimeOfDay()
sunset = main.TimeOfDay()

t = 1735729200 # 2025-01-01 12:00 CET

while True:
    now = main.localTimeOfDay(t)
    now.h = 12
    if now.year > 2025:
        break

    sun = Suntime.Sun(config.LAT, config.LON, now.utc_offset_h)
    _, _, _, sunrise.h, sunrise.m = sun.get_sunrise_time(time.localtime(t))
    _, _, _, sunset.h, sunset.m = sun.get_sunset_time(time.localtime(t))

    main.render_time(now, sunrise, sunset)
    
    # Add 15 days
    t += 15*3600*24
