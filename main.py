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


def wifi_connect():
    """
    Connect to wifi using credentials in config.py.
    Blocks until we are connected.
    """

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(config.WIFI_SSID, config.WIFI_PASSWORD)

    while True:
        status = wifi_pretty_status(wlan.status())
        print(f"Waiting for wifi, status={status}")
        if wlan.isconnected():
            break
        time.sleep(1)

    ip = wlan.ifconfig()[0]
    print(f"Wifi connected, ip={ip}")


def ntp_sync():
    while True:
        print("Initial NTP sync....")
        try:
            ntptime.settime()
            break
        except Exception as e:
            print(f"NTP sync failed: {e}")
            time.sleep(1)

    print(f"NTP sync ok")


def status_pixel(np, color):
    """
    Show boot progress in first pixel
    """
    np[0] = color
    np.write()


def render_time(np, hour, minute, seconds):
    """
    Show the current time as a single dot on the LED strip
    """
    np.fill((0, 0, 0))

    fractional_day = hour / 24 + minute / 1440 + seconds / 86400
    index = int(math.floor(np.n * fractional_day))

    print(
        f"Local time: {hour:02}h{minute:02}m{seconds:02}s = {fractional_day:.06}d = pixel #{index+1:3}"
    )

    np[index] = config.DOTCOLOR
    np.write()


def main():
    np = neopixel.NeoPixel(machine.Pin(config.GPIOPIN), config.PIXELS)
    status_pixel(np, (10, 0, 0))

    wifi_connect()
    status_pixel(np, (0, 10, 0))

    ntp_sync()
    need_ntp_resync = False
    status_pixel(np, (0, 0, 10))

    while True:
        t = time.time()
        _, _, _, hour, minute, seconds, _, _, _ = localPTZtime.tztime(
            t, config.POSIX_TZ_STRING
        )

        render_time(np, hour, minute, seconds)

        # NTP resync every day at 0h
        if hour == 23:
            need_ntp_resync = True
        if hour == 0 and need_ntp_resync:
            try:
                ntptime.settime()
                need_ntp_resync = False
                print(f"NTP resync ok")
                status_pixel(np, (0, 0, 0))
            except Exception as e:
                print(f"NTP resync failed: {e}")
                status_pixel(np, (10, 10, 0))

        time.sleep(10)


if __name__ == "__main__":
    main()
