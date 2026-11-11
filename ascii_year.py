# Prints 25 lines (every 15 days) of the year 2025 sun progression as ascii art

import main

t = 1735729200 # 2025-01-01 12:00 CET

while True:
    now = main.localTimeOfDay(t)
    now.h = 12
    if now.year > 2025:
        break

    sunrise, sunset = main.sun_times(now)

    main.render_time(now, sunrise, sunset)
    
    # Add 15 days
    t += 15*3600*24
