# Software Design Project

## OBS Scene Switcher

To initialise PlatformIO, ensure PlatformIO Core is installed and run

```console
pio project init --board nanoatmega328
```

The python scripts require a .env file located in the same directory.

Example .env contents:

```console
HOST=localhost
PORT=4455
OBS_PASSWORD=password                   # set in OBS app
SERIAL_PORT=/dev/cu.usbserial-1430  # can be found on Mac with command: ls /dev/cu*
```
