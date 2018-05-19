#!/usr/bin/env python
#
# (c) 2018 Maarten Los. All rights reserved.
# 
#
import os
import time
import sys
import thread
import json
from luma.core import cmdline
import RPi.GPIO as GPIO
from screens import MainScreen
from screens import OneLineScreen
import graphutils
from inbus.client.subscriber import Subscriber

OLED_RES = 25

def enable_oled():
    GPIO.setmode(GPIO.BCM) # Use Pi numbering (not physcial pins)
    GPIO.setup(OLED_RES, GPIO.OUT)

    # Reset OLED
    GPIO.output(OLED_RES, True)
    time.sleep(0.3)
    GPIO.output(OLED_RES, False)
    time.sleep(0.3)
    GPIO.output(OLED_RES, True)
    time.sleep(1)


def get_device():
    parser = cmdline.create_parser(description='nemo')
    args = parser.parse_args(sys.argv[1:])
    return cmdline.create_device(args)

class SharedData:
    def __init__(self, **kwargs):
        self.__dict__ = kwargs

lock = thread.allocate_lock()
event = SharedData()

def inbus_observer():
    global event
    event.has_event = False
    with Subscriber("nemo") as s:
        while True:
            try:
                payload, applicationType = s.get_published_message()
                print "Received :'" + payload + "' (Type: " + str(applicationType) + ")"
                with lock:
                    event.has_event = True
                    event.payload = payload
                    event.app_type = applicationType

            except RuntimeError:
                print "Error receiving Inbus message"

# ------- main

enable_oled()


device = get_device()
fnt = graphutils.make_font("PixelOperator.ttf", 16)


# Modes:
# 1 - Showing boot message
# 2 - Showing goodbye message
# 3 - Showing copyright + info
# 4 - Rendering artist + song + status
mode = 1

music_screen = MainScreen(device, fnt)
welcome_screen = OneLineScreen(device, fnt, "Welcome to Nemo")
goodbye_screen = OneLineScreen(device, fnt, "Goodbye")

current_screen = welcome_screen

thread.start_new_thread(inbus_observer, ())

try:
    music_screen.set_info("Song with a very long title", "Artist with a very long name")
    music_screen.resume()

    must_handle_event = False
    payload = None
    app_type = -1
    while True:
        with lock:
            if event.has_event:
                must_handle_event = True
                payload = event.payload
                app_type = event.app_type
                event.has_event = False

        if must_handle_event:
            must_handle_event = False
            if app_type == 0:
                if payload == "1":
                    current_screen = welcome_screen
                elif payload == "0":
                    current_screen = goodbye_screen
            elif app_type == 10:
                info = json.loads(payload)
                music_screen.set_info(info["title"], info["artist"])
                current_screen = music_screen
            current_screen.show()

        current_screen.tick()
        time.sleep(0.025)

except KeyboardInterrupt:
    pass

