# Camera Timelapse Dolly #
This camera dolly was born from desire to take moving timelapse videos in cold 
environment. Project has not evolved in features much since its conception 
during 2016 but in implementation much so. First implementation was using Adafruit
Motor HAT with NEMA17 stepper motors to move dolly and rotate camera head. Only new
feature is autamtec head alignment according to earth axis that has appeared 
since the first version. This is noe third revision. 
## Features ##
Summary of main high level features of the dolly
- Move camera along rail using timing belt
- End stops to detect end of rail
- Rotate camera 360° 
- Provide 8V power for camera (necessary in freezing conditions)
- Have lens heating element with temperature sensor
- Align camera rotation axis with earth axis for star tracking
- Control camera via USB interface
- Mobile app controls and 3G/4G connectivity

## Changes and rationale ##
Major change has been to ditch stepper motors in favour of DC motors. Main reason
behind the change was to enable star tracking and loooong exposures (like minutes
not seconds) as well as preserve energy. 
Also full size raspberry pi has been changes to Zero for more compact construction
and slightly less power consumption. Main drawback of this is the loss of 4G 
connectivity.
