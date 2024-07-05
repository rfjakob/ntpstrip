import network
import time
import json
import ntptime
import neopixel
import math
import machine

import localPTZtime

# Local config
import config

class TimeOfDay:
    def __init__(self, h, m, s):
        self.h = h
        self.m = m
        self.s = s

def wifi_pretty_status(status):
    """
    Pretty-print network.WLAN.status()
    """
    well_known = {
        network.STAT_IDLE: "IDLE",
        network.STAT_CONNECTING: "CONNECTING",
        network.STAT_WRONG_PASSWORD: "WRONG_PASSWORD",
        network.STAT_NO_AP_FOUND: "NO_AP_FOUND",
        network.STAT_CONNECT_FAIL: "CONNECT_FAIL",
        network.STAT_GOT_IP: "GOT_IP",
    }

    if status in well_known:
        return f"{status}/{well_known[status]}"

    # Yes, this happens. The docs are incomplete.
    return f"{status}"


def wifi_connect(wlan):
    """
    Connect to wifi using credentials in config.py.
    Waits at most 20 seconds for a connection.
    """

    wlan.active(False)
    wlan.active(True)
    print(f'Connecting to wifi "{config.WIFI_SSID}"...')
    wlan.connect(config.WIFI_SSID, config.WIFI_PASSWORD)
    status_pixel(STATUS_CONNECTING)

    retry = 1
    maxretry = 20

    while retry <= maxretry:
        status = wifi_pretty_status(wlan.status())
        print(f"Waiting for wifi {retry}/{maxretry}, status={status}")

        if wlan.isconnected():
            ip = wlan.ifconfig()[0]
            print(f"Wifi connected, ip={ip}")
            status_pixel(STATUS_HAVE_WIFI)
            return True

        time.sleep(1)
        retry += 1

    return False


def ntp_sync():
    retry = 1
    maxretry = 3

    while retry <= maxretry:
        print(f"NTP sync try {retry}/{maxretry}...")
        try:
            t_before = time.time()
            ntptime.settime()
            offset = t_before - time.time()
            print(f"NTP sync ok, our clock error was {offset:+}s")
            status_pixel(STATUS_HAVE_NTP)
            return True
        except Exception as e:
            print(f"NTP sync failed: {e}")

        time.sleep(1)
        retry += 1

    status_pixel(STATUS_HAVE_WIFI)
    return False


STATUS_CONNECTING = (10, 0, 0)
STATUS_HAVE_WIFI = (0, 10, 0)
STATUS_HAVE_NTP = (0, 0, 0)

status_pixel_value = (0, 0, 0)


def status_pixel(color=None):
    """
    Show boot progress in first pixel
    """
    global status_pixel_value
    status_pixel_value = color

    global np
    np[0] = status_pixel_value
    np.write()


def render_time(now):
    """
    Show the current time as a single dot on the LED strip
    """
    global np
    np.fill((0, 0, 0))

    # The fill() overwrote the status pixel. Restore it.
    np[0] = status_pixel_value

    fractional_day = now.h / 24 + now.m / 1440 + now.s / 86400
    index = int(math.floor(np.n * fractional_day))

    np[index] = config.DOTCOLOR
    np.write()

    return index


def localTimeOfDay(t: float):
    """
    Convert a `time.time()` timestamp to local time
    """
    _, _, _, hour, minute, seconds, _, _, _ = localPTZtime.tztime(
        t, config.POSIX_TZ_STRING
    )
    return TimeOfDay(hour, minute, seconds)


def main():
    # Onboard LED shows that main.py has started executing
    led = machine.Pin("LED", machine.Pin.OUT)
    led.on()

    global np
    np = neopixel.NeoPixel(machine.Pin(config.GPIOPIN), config.PIXELS)
    wlan = network.WLAN(network.STA_IF)

    print("Initial sync...")
    while True:
        if wifi_connect(wlan):
            pass
        else:
            continue

        if ntp_sync():
            last_ntp_sync = time.time()
            break

    # Don't distract from the time display
    led.off()

    loop_count = 0
    loop_sleep = 10
    if config.STRESS_TEST:
        loop_sleep = 0

    # Main loop
    while True:
        loop_count += 1

        t = time.time()
        if config.STRESS_TEST:
            t += loop_count * 60

        now = localTimeOfDay(t)
        index = render_time(now)
        wifi_status = wifi_pretty_status(wlan.status())
        print(
            f"{now.h:02}h{now.m:02}m{now.s:02}s = pixel #{index+1:3}, wifi={wifi_status}, loop={loop_count}"
        )

        # NTP resync needed?
        if t < last_ntp_sync + 24 * 3600:
            # No
            time.sleep(loop_sleep)
            continue

        # Yes
        if ntp_sync():
            last_ntp_sync = t
        else:
            # Probably failed due to wifi problems. Try reconnecting.
            wifi_connect(wlan)


if __name__ == "__main__":
    main()
