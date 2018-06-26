Installation:

- Install 
- Create /home/upnp/sys
- Install the following files into /home/upnp/sys:
    screens.py
    display.py
    graphutils.py
    inbus-server.py
    power.py

- Copy all files in from initscripts into /etc/init.d
- For each file, execute:
    sudo update-rc.d <file> defaults

- Reboot
