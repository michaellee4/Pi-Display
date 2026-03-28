import sys
sys.path.append('e-Paper/RaspberryPi_JetsonNano/python/lib')
from waveshare_epd import epd13in3k

epd = epd13in3k.EPD()
epd.init()
epd.Clear()
epd.sleep()
print("Screen cleared.")
