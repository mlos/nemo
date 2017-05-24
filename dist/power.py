#
# (c) 2017 Maarten Los. All rights reserved.
# 
#
import RPi.GPIO as GPIO
import time
from subprocess import call

Debug=1

PWR_BTN_IN = 12
LED_R_CTL = 16
LED_G_CTL = 18

PowerButtonPressedDuration = 3 # seconds

if Debug:
  def rising_callback(channel):
    print('RISING Edge detected on channel %s'%channel)


GPIO.setmode(GPIO.BOARD)
GPIO.setup(PWR_BTN_IN, GPIO.IN)
GPIO.setup(LED_R_CTL, GPIO.OUT)
GPIO.setup(LED_G_CTL, GPIO.OUT)

#if Debug:
#  GPIO.add_event_detect(PWR_BTN_IN, GPIO.FALLING, callback=rising_callback,bouncetime=200)

GPIO.output(LED_R_CTL, True)
GPIO.output(LED_G_CTL, True)

call(["touch","/tmp/power"])

# Start polling
while True:
  print "."
  GPIO.wait_for_edge(PWR_BTN_IN, GPIO.RISING)
  startTime=time.time()
  Done = False
  while GPIO.input(PWR_BTN_IN) == GPIO.HIGH and not Done:
    if (time.time() - startTime) >= PowerButtonPressedDuration:
      Done = True
      GPIO.output(LED_R_CTL, False)
      if Debug:
        print "Powering off (not for real)"
      else:
        GPIO.cleanup()
        call(["poweroff"])
      exit(0)
  print "NO Power off"
  call(["touch","/tmp/NO.power.off"])
  


