#!/usr/bin/env python
#
# (c) 2018 Maarten Los. All rights reserved.
# 
#
import os
import time
import sys
from PIL import ImageFont, Image, ImageDraw
from luma.core import cmdline
from luma.core.render import canvas
from luma.core.image_composition import ImageComposition, ComposableImage
import RPi.GPIO as GPIO
from screens import MainScreen
import graphutils

OLED_RES = 25

def enable_oled():
    GPIO.setmode(GPIO.BCM) # Use Pi numbering (not physcial pins)
    GPIO.setup(OLED_RES, GPIO.OUT)

    # Reset OLED
    GPIO.output(OLED_RES, True)
    time.sleep(1)
    GPIO.output(OLED_RES, False)
    time.sleep(1)
    GPIO.output(OLED_RES, True)
    time.sleep(1)


def get_device():
    parser = cmdline.create_parser(description='nemo')
    args = parser.parse_args(sys.argv[1:])
    return cmdline.create_device(args)


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

    
#def showing_boot_message():
#    message = "Welcome to Nemo"
#    with canvas(device) as draw:
#        draw_marker(draw)
#        size = draw.textsize(message, font=fnt)
#        left = device.width//2 - size[0]//2
#        top = device.height//2 - size[1]//2 - 5
#        draw.text((left, top), message, fill="white", font=fnt)


#while True:
#    showing_boot_message()
#    time.sleep(1)
    

m = MainScreen(device, fnt)

try:
    m.set_info("Song with a very long title", "Artist with a very long name")
    m.resume()

    while True:
        m.tick()
        time.sleep(0.025)

except KeyboardInterrupt:
    pass

