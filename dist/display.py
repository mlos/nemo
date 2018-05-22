#!/usr/bin/env python
#
# (c) 2018 Maarten Los. All rights reserved.
# 
#
import os
import time
import sys
import thread
import signal
import json
import socket
from luma.core import cmdline
import RPi.GPIO as GPIO
from screens import MusicScreen
from screens import OneLineScreen
from screens import MultiLineScreen
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

def disable_oled():
    GPIO.output(OLED_RES, False)
    
def sighandler(signum, frame):
    disable_oled()
    sys.exit(1)

def get_device():
    parser = cmdline.create_parser(description='nemo')
    args = parser.parse_args(sys.argv[1:])
    return cmdline.create_device(args)

class SharedData:
    def __init__(self, **kwargs):
        self.__dict__ = kwargs

lock = thread.allocate_lock()
event = SharedData()
event.has_event = False

def inbus_observer():
    global event
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


def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

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

music_screen = MusicScreen(device, fnt)
welcome_screen = OneLineScreen(device, fnt, "Welcome to Nemo")
goodbye_screen = OneLineScreen(device, fnt, "Shutting down...")
ready_screen = OneLineScreen(device, fnt, "Ready to rock")
about_screen = MultiLineScreen(device, fnt, [ 
    ("Nemo", 4),
    ("(c) Maarten Los", 24),
    (get_ip_address(), 46)])

current_screen = welcome_screen

thread.start_new_thread(inbus_observer, ())

# Trap SIGHUP
signal.signal(signal.SIGHUP, sighandler)

PAUSED = 0
PLAYING = 1
STOPPED = 2

try:
    must_handle_event = False
    payload = None
    app_type = -1
    stop_requested = False
    MIN_STOP_TIME = 2 # seconds

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
                    current_screen = about_screen
                elif payload == "0":
                    current_screen = goodbye_screen
            elif app_type == 10:
                info = json.loads(payload)
                music_screen.set_info(info["title"], info["artist"])
                play_state = info["playstate"]
                if play_state in [ PAUSED, PLAYING ]:
                    stop_requested = False
                    current_screen = music_screen
                    if play_state == PAUSED:
                        music_screen.pause()
                    elif play_state == PLAYING:
                        music_screen.play()
                elif play_state == STOPPED:
                    # when skipping to next song, state is STOP.
                    # this mechanism ensures hysteresis to only show
                    # stop when really stopped
                    if not stop_requested:
                        time_stop_requested = time.time()
                        stop_requested = True
                        must_handle_event = True
                    else:
                        if (time.time() - time_stop_requested) > MIN_STOP_TIME:
                            current_screen = ready_screen
                            must_handle_event = False
                        else:
                            must_handle_event = True

            current_screen.show()

        current_screen.tick()
        time.sleep(0.025)

except KeyboardInterrupt:
    pass

