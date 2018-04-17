#
# (c) 2018 Maarten Los. All rights reserved.
# 
#
import RPi.GPIO as GPIO
import time
import json
from inbus.client.subscriber import Subscriber

Debug=0

# BCM numbering (not BOARD)
OLED_RES = 25

AppKey = "nemo"

GPIO.setmode(GPIO.BCM) # Use Pi numbering (not physcial pins)
GPIO.setup(OLED_RES, GPIO.OUT)

# Reset OLED
GPIO.output(OLED_RES, True)
time.sleep(0.5)
GPIO.output(OLED_RES, False)
time.sleep(0.5)
GPIO.output(OLED_RES, True)


while True:
    time.sleep(10)
