**spectro**

Supports a Raspberry Pi, controlling a C12666MA spectrometer hosted on an Arduino Uno.

# HARDWARE
- RPi 2 with a TFT display 
- Hamamatsu C12666MA Spectrometer mounted to an Arduino
- RPi talks to Arduino via serial with USB
- RPi will also have a camera, to record the area that is being measured.
- all in an enclosure with a battery
- button to trigger a new reading
- have some kind of audio or visual output to indicate a sample has been taken

# CORE FUNCTIONALITY:
- RPi will have a library of known spectrometer profiles
  - RPi will have a training mode to add new samples
  - RPi will have a calibration mode to compare a known sample against earlier saved profiles
- After taking a measurement the RPi will tell us what profiles it matches
- Three modes of use for the spectrometer:
  - spectroscopy with ambient light
  - color measurement with white led
  - fluorescence spectroscopy
- Arduino is dumb, it just takes shots with the spectrometer in one of its three modes
- Offloading the entire database 
- Pictures need to be preserved as carefully as the data
- Serve RESTful web transactions asynchronously (Parallel requests and pictures take a long time)
- Mark each picture with sample info
