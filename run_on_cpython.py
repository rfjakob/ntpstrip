#!/usr/bin/env python3
"""
Run the clock code on a PC with regular CPython by replacing the
MicroPython hardware modules (machine, network, neopixel, ntptime, utime)
with fakes. The LED strip shows up as the ASCII art that render_time()
prints.

Usage:
    ./run_on_cpython.py                  # run main.py
    ./run_on_cpython.py --stress         # run main.py with STRESS_TEST = True
    ./run_on_cpython.py ascii_year.py    # run another script

Uses config.py if it exists, otherwise config_example.py.
"""

import os
import runpy
import sys
import time
import types

# MicroPython has no timezone support: time.localtime() and time.mktime()
# work in UTC. Make CPython behave the same.
os.environ["TZ"] = "UTC"
time.tzset()

# On MicroPython, time.time() returns whole seconds as an int.
_cpython_time = time.time
time.time = lambda: int(_cpython_time())


class FakePin:
    OUT = 1

    def __init__(self, *args, **kwargs):
        pass

    def on(self):
        pass

    def off(self):
        pass


class FakeWLAN:
    def __init__(self, interface):
        self._connected = False

    def active(self, on):
        pass

    def connect(self, ssid, password):
        self._connected = True

    def isconnected(self):
        return self._connected

    def status(self):
        return network.STAT_GOT_IP if self._connected else network.STAT_IDLE

    def ifconfig(self):
        return ("127.0.0.1", "255.0.0.0", "127.0.0.1", "127.0.0.1")


class FakeNeoPixel(list):
    def __init__(self, pin, n):
        super().__init__([(0, 0, 0)] * n)

    def fill(self, color):
        self[:] = [color] * len(self)

    def write(self):
        pass


machine = types.ModuleType("machine")
machine.Pin = FakePin

network = types.ModuleType("network")
network.STA_IF = 0
network.STAT_IDLE = 0
network.STAT_CONNECTING = 1
network.STAT_WRONG_PASSWORD = -3
network.STAT_NO_AP_FOUND = -2
network.STAT_CONNECT_FAIL = -1
network.STAT_GOT_IP = 3
network.WLAN = FakeWLAN

neopixel = types.ModuleType("neopixel")
neopixel.NeoPixel = FakeNeoPixel

ntptime = types.ModuleType("ntptime")
ntptime.settime = lambda: None  # The PC clock is already NTP-synced

sys.modules.update(
    machine=machine,
    network=network,
    neopixel=neopixel,
    ntptime=ntptime,
    utime=time,
)

here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)

if not os.path.exists(os.path.join(here, "config.py")):
    print("config.py not found, using config_example.py")
    import config_example

    sys.modules["config"] = config_example

args = sys.argv[1:]
if "--stress" in args:
    args.remove("--stress")
    import config

    config.STRESS_TEST = True

script = args[0] if args else "main.py"
runpy.run_path(os.path.join(here, script), run_name="__main__")
