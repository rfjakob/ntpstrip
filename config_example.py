WIFI_SSID = "MyFastWifi"
WIFI_PASSWORD = "sg44e54!!vgsd"

PIXELS = 144  # The number of pixels on the neopixel strip
GPIOPIN = 15  # The pin that the signal wire of the LED strip is connected to
DOTCOLOR = (0, 10, 10)  # Color of the time dot

# POSIX Timezone String. Pick one from here:
# https://github.com/nayarsystems/posix_tz_db/blob/master/zones.json
#
# More info: https://github.com/bellingeri/localPTZtime
#
# Value below is for central Europe (Vienna, Berlin, Paris, ...).
POSIX_TZ_STRING = "CET-1CEST,M3.5.0,M10.5.0/3"

# Latitude and longitude to calculate sunrise and sunset.
# Values below are for Vienna, Austria.
LAT = 48.208333
LON = 16.373056

# Background color between sunrise and sunset. Default: Yellow.
SUN_COLOR = (1, 1, 0)

# Set to True to have time run 1000x as fast
STRESS_TEST = False
