import sys
import os
import time

# Add the Waveshare library to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'e-Paper/RaspberryPi_JetsonNano/python/lib'))

from waveshare_epd import epd13in3k
from PIL import Image, ImageDraw

def draw_face(epd, happy):
    image = Image.new('1', (epd.width, epd.height), 255)
    draw = ImageDraw.Draw(image)

    cx, cy = epd.width // 2, epd.height // 2
    r = 200

    # Face outline
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=0, width=6)

    # Eyes
    eye_r = 20
    eye_y = cy - 70
    draw.ellipse((cx - 80 - eye_r, eye_y - eye_r, cx - 80 + eye_r, eye_y + eye_r), fill=0)
    draw.ellipse((cx + 80 - eye_r, eye_y - eye_r, cx + 80 + eye_r, eye_y + eye_r), fill=0)

    # Mouth — smile (20→160) or frown (200→340)
    mouth_margin = 80
    if happy:
        draw.arc(
            (cx - r + mouth_margin, cy - r + mouth_margin, cx + r - mouth_margin, cy + r - mouth_margin),
            start=20, end=160, fill=0, width=6
        )
    else:
        draw.arc(
            (cx - r + mouth_margin, cy - mouth_margin, cx + r - mouth_margin, cy + r + mouth_margin - 20),
            start=200, end=340, fill=0, width=6
        )

    return image

def main():
    print("Initializing display...")
    epd = epd13in3k.EPD()
    epd.init()
    epd.Clear()

    happy = True
    try:
        while True:
            label = "smiley" if happy else "frowny"
            print(f"Drawing {label} face...")
            image = draw_face(epd, happy)
            print("Sending to display (this takes ~15-20 seconds)...")
            epd.display(epd.getbuffer(image))
            print(f"Showing {label} face. Switching in 10 seconds...")
            time.sleep(10)
            happy = not happy
    except KeyboardInterrupt:
        print("\nStopped. Sleeping display...")
        epd.sleep()
        print("Display is asleep. All done!")

if __name__ == '__main__':
    main()
