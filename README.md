# spectro

Supports a Raspberry Pi, controlling a C12666MA spectrometer hosted on an Arduino Uno.

## HARDWARE
- RPi 2 with a TFT display 
- Hamamatsu C12666MA Spectrometer mounted to an Arduino
- RPi talks to Arduino via serial with USB
- RPi will have a camera, to record the location of the sample
- RPi will have a microphone to record voice notes on the sample
- RPi may have a TFT touchscreen (for heads up mode)
- RPi may have a GPS receiver
- RPi will also have a button to trigger a new reading (for headless mode)
- RPi creates audio or visual output to indicate a sample has been taken
- Experimenting with packaging, but it may be a two piece tethered object, with the battery and RPi in the base and the rest in the remote.

## CORE FUNCTIONALITY:
- RPi will have a library of known spectrometer profiles
  - RPi will have a training mode to add new samples
  - RPi will have a calibration mode to compare a known sample against earlier saved profiles
  - RPi may also attempt to match new samples against unknown compounds based on their known chemical properties
- After taking a spectrometer measurement the RPi will tell us what profiles it matches
- Three modes of use for the spectrometer:
  - Spectroscopy with ambient light
  - Color measurement with white led
  - Fluorescence spectroscopy
- Arduino is dumb, it just takes shots with the spectrometer in one of its three modes
- Support for offloading the entire database 
- Samples and some other operations may be processed asynchronously 
- Picture will be marked with identifying sample info
- Application will be served locally as an API, which will be consumed by an outward-facing html application
- No security on the RPi (you already have physical control of the device, anything short of full disk encryption would allow you to own the data and FDE is too much overhead in this case), 
  - But there will be another app which can serve up group and sample data from an AWS-hosted Docker-contained app, that app will have security

## SOFTWARE
- Django with Python 3 
