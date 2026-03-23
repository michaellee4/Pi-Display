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

    font_large = ImageFont.truetype(FONT_PATH, 72)
    font_small = ImageFont.truetype(FONT_PATH, 36)

    # Center "Hello World!" on the display
    text = "Hello World!"
    bbox = draw.textbbox((0, 0), text, font=font_large)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (epd.width - text_w) // 2
    y = (epd.height - text_h) // 2

    draw.text((x, y), text, font=font_large, fill=0)

    # Subtitle
    sub = "Waveshare 13.3\" E-Ink HAT (K)"
    sub_bbox = draw.textbbox((0, 0), sub, font=font_small)
    sub_w = sub_bbox[2] - sub_bbox[0]
    draw.text(((epd.width - sub_w) // 2, y + text_h + 20), sub, font=font_small, fill=0)

    print("Sending to display (this takes ~15-20 seconds)...")
    epd.display(epd.getbuffer(image))

    print("Done! Sleeping display...")
    time.sleep(3)
    epd.sleep()
    print("Display is asleep. All done!")

if __name__ == '__main__':
    main()
