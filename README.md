# nemo

** UPDATE: Added [Power Management Circuitry](PMC.md)**

- - -
## The Concept

Welcome to Nemo, the **ne**tworked **m**usic b**o**x. The project describes my efforts to create a homebrew UPnP renderer, with the following goals:

* Produce a simple device, to extend my already [existing][ref-tuner] [stack][ref-cdplayer] of [Technics][ref-amplifier] [gear][ref-equalizer] (no need yet for an AV Receiver)
* Give the Raspberry Pi I have lying around a home
* Brush up my electronics skills

### UPnP

[UPnP][ref-upnp] stands for Universal Plug and Play and is the technology that underpins [DLNA][ref-dlna] , which lets you stream media between devices connected in your home network, and that comes with virtually any audio or TV equipment you can buy nowadays.

UPnP has a notion of three logical components:

* a Media Server holding audio, video, photo's, etc.
* a Renderer, reproducing content from the Media Server
* a Control Point controlling the Renderer and the Media Server 


### Context
The following diagram illustrates the UPnP context in which Nemo operates. A [smartphone app][ref-app] (the Control Point) selects a song from the music library on the [NAS][ref-nas] (the Media Server) and instructs Nemo (the Renderer) to reproduce it.

- - -
![Context](diagrams/generated/Concept.png =600x)
- - -

## The Requirements
Nemo is conceived to fulfill the following needs:

* Repurpose my [Raspberry Pi model B][ref-pi]
* Good enough audio quality, but at least better than what's [built-in][ref-pi-audio]
* The ability to gracefully power off the device (orderly shutdown of the [system software][ref-raspbian]). Although the Pi [draws relatively little power][ref-pi-power], it doesn't seem right to leave it powered on 24/7.
* Feedback about operational state (booting, playing, powering off). A user should be able to see what's going on.
* [RCA][ref-rca-jack] jack to connect it to standard stereo equipment.
* LAN connection to easily hook it up to the home network (no Wi-Fi configuration troubles)

## The Design
### Hardware
The following schematic illustrates the high level hardware design.
- - -
![Block diagram](diagrams/generated/BlockDiagram.png =600x)
- - -
The following components are used:

**RPI** - Raspberry Pi 1 Model B. The core of the system.

**PWR** - 5V power supply.

**BTN_1** and **BTN_2** - Function buttons to control **DISP**

**DISP** - A [128x128 pixel OLED][ref-oled] for displaying song and artist information

**SNDC** - An [external USB sound card][ref-usb-sound], for "good enough" quality audio

**PWR_RES** - The power and reset button.

**LED_RGB** - Status LED for system feedback, with support for red, yellow, green and purple colors. A single [RGB LED][ref-led] neatly fulfills this function.

**PMC** - The [Power Management Circuitry](PMC.md), interfaces with the **RPI** and is responsible for making sure the LEDs have the right color and enabling the **PWR_RES** button depending on the system state.

- - - 

### Software

Follows

### Hardware / Software interface

Follows

- - - 
- 







[ref-upnp]: http://en.wikipedia.org/wiki/Universal_Plug_and_Play
[ref-dlna]: http://www.dlna.org
[ref-amplifier]: http://www.hifiengine.com/manual_library/technics/su-x955.shtml
[ref-equalizer]: http://www.hifiengine.com/manual_library/technics/sh-e66.shtml
[ref-tuner]: https://www.hifiengine.com/manual_library/technics/sl-pj27a.shtml
[ref-cdplayer]: http://www.hifiengine.com/manual_library/technics/st-x933l.shtml
[ref-nas]: http://www.synology.com/en-us/products
[ref-app]: http://itunes.apple.com/us/app/ds-audio/id321495303?mt=8
[ref-pi]: http://www.raspberrypi.org/products/model-b/
[ref-pi-audio]: http://raspberrypi.stackexchange.com/questions/3626/how-to-get-better-audio-quality-from-audio-jack-output
[ref-raspbian]: http://raspbian.org
[ref-pi-power]: http://www.pidramble.com/wiki/benchmarks/power-consumption
[ref-rca-jack]: http://www.lifewire.com/rca-jack-definition-3134804
[ref-usb-sound]: http://www.google.nl/search?q=HDE+7.1+channel+booster
[ref-oled]: http://www.google.nl/search?q=128x128+OLED
[ref-led]: http://www.google.nl/search?q=diffused+RGB+LED+5mm