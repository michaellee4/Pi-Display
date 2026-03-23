import sys
import os
import time

# Add the Waveshare library to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'e-Paper/RaspberryPi_JetsonNano/python/lib'))

from waveshare_epd import epd13in3k
from PIL import Image, ImageDraw, ImageFont

FONT_PATH = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

def main():
    print("Initializing display...")
    epd = epd13in3k.EPD()
    epd.init()
    epd.Clear()

    print("Drawing image...")
    image = Image.new('1', (epd.width, epd.height), 255)  # white background
    draw = ImageDraw.Draw(image)

    cx, cy = epd.width // 2, epd.height // 2
    r = 200  # face radius

    # Face outline
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=0, width=6)

    # Eyes
    eye_r = 20
    eye_y = cy - 70
    draw.ellipse((cx - 80 - eye_r, eye_y - eye_r, cx - 80 + eye_r, eye_y + eye_r), fill=0)
    draw.ellipse((cx + 80 - eye_r, eye_y - eye_r, cx + 80 + eye_r, eye_y + eye_r), fill=0)

    # Smile (arc)
    smile_margin = 80
    draw.arc(
        (cx - r + smile_margin, cy - r + smile_margin, cx + r - smile_margin, cy + r - smile_margin),
        start=20, end=160, fill=0, width=6
    )

    print("Sending to display (this takes ~15-20 seconds)...")
    epd.display(epd.getbuffer(image))

    print("Done! Sleeping display...")
    time.sleep(3)
    epd.sleep()
    print("Display is asleep. All done!")

if __name__ == '__main__':
    main()
