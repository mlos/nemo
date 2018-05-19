#
# (c) 2017, 2018 Maarten Los. All rights reserved.
# 
#
import RPi.GPIO as GPIO
import time
import json
from subprocess import call
from inbus.client.publisher import Publisher

Debug=0

# BCM numbering (not BOARD)
PWR_BTN_IN = 18
LED_R_CTL = 23

AppKey = "nemo"
AppType = 0

PowerButtonPressedDuration = 3 # seconds

if Debug:
  def rising_callback(channel):
    print('RISING Edge detected on channel %s'%channel)


GPIO.setmode(GPIO.BCM) # Use Pi numbering (not physcial pins)
GPIO.setup(PWR_BTN_IN, GPIO.IN)
GPIO.setup(LED_R_CTL, GPIO.OUT)
# Green LED is handled in  /etc/rc.d/bootled

#if Debug:
#  GPIO.add_event_detect(PWR_BTN_IN, GPIO.FALLING, callback=rising_callback,bouncetime=200)

# Red LED off (high=off)
GPIO.output(LED_R_CTL, True)

call(["touch","/tmp/power"])

inbus = Publisher(AppKey)

# Start polling
while True:
  GPIO.wait_for_edge(PWR_BTN_IN, GPIO.RISING)
  startTime=time.time()
  Done = False
  while GPIO.input(PWR_BTN_IN) == GPIO.HIGH and not Done:
    if (time.time() - startTime) >= PowerButtonPressedDuration:
      Done = True
      # Reset pin to input and pull-down. This will make sure LED_R will
      # light up by default
      GPIO.setup(LED_R_CTL, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)
      inbus.publish("0", AppType)
      if Debug:
        print "Powering off (not for real)"
      else:
        call(["poweroff"])
      exit(0)

  inbus.publish("1", AppType)
  call(["touch","/tmp/NO.power.off"])

