import sys
import os
import time
from datetime import datetime, timedelta

sys.path.append(os.path.join(os.path.dirname(__file__), 'e-Paper/RaspberryPi_JetsonNano/python/lib'))

from waveshare_epd import epd13in3k
from PIL import Image, ImageDraw, ImageFont

FONT_PATH      = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FONT_PATH_REG  = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'

# Mock departures from Grove St — (destination, minutes_from_now, status)
DEPARTURES = [
    ("World Trade Center",  2,  "ON TIME"),
    ("33rd Street",         6,  "ON TIME"),
    ("Journal Square",      9,  "ON TIME"),
    ("World Trade Center",  13, "DELAYED"),
    ("Newark",              17, "ON TIME"),
    ("Hoboken",             21, "ON TIME"),
    ("33rd Street",         25, "ON TIME"),
    ("World Trade Center",  31, "ON TIME"),
]

def draw_schedule(epd):
    W, H = epd.width, epd.height  # 960 x 680
    image = Image.new('1', (W, H), 255)
    draw = ImageDraw.Draw(image)

    font_huge   = ImageFont.truetype(FONT_PATH, 52)
    font_large  = ImageFont.truetype(FONT_PATH, 34)
    font_medium = ImageFont.truetype(FONT_PATH, 26)
    font_small  = ImageFont.truetype(FONT_PATH, 22)
    font_reg    = ImageFont.truetype(FONT_PATH_REG, 22)

    now = datetime.now()

    # ── Header bar ──────────────────────────────────────────────────────────
    HEADER_H = 90
    draw.rectangle((0, 0, W, HEADER_H), fill=0)

    # Station name
    draw.text((24, 16), "Grove Street", font=font_huge, fill=255)

    # "PATH" badge on the right
    badge_text = "PATH"
    badge_bbox = draw.textbbox((0, 0), badge_text, font=font_large)
    badge_w = badge_bbox[2] - badge_bbox[0] + 24
    badge_x = W - badge_w - 20
    draw.rectangle((badge_x, 18, badge_x + badge_w, HEADER_H - 18), outline=255, width=3)
    draw.text((badge_x + 12, 22), badge_text, font=font_large, fill=255)

    # Current time
    time_str = now.strftime("%-I:%M %p")
    time_bbox = draw.textbbox((0, 0), time_str, font=font_medium)
    time_x = badge_x - (time_bbox[2] - time_bbox[0]) - 30
    draw.text((time_x, 30), time_str, font=font_medium, fill=255)

    # ── Column headers ───────────────────────────────────────────────────────
    COL_H = 44
    col_y = HEADER_H
    draw.rectangle((0, col_y, W, col_y + COL_H), fill=0)

    COL_DEST   = 0
    COL_TIME   = 560
    COL_MINS   = 720
    COL_STATUS = 840

    headers = [
        (COL_DEST   + 20, "DESTINATION"),
        (COL_TIME   + 10, "DEPARTS"),
        (COL_MINS   + 10, "MINS"),
        (COL_STATUS + 10, "STATUS"),
    ]
    for x, label in headers:
        draw.text((x, col_y + 10), label, font=font_small, fill=255)

    # Vertical dividers in header
    for x in (COL_TIME, COL_MINS, COL_STATUS):
        draw.line((x, col_y, x, col_y + COL_H), fill=255, width=1)

    # ── Departure rows ───────────────────────────────────────────────────────
    ROW_H = (H - HEADER_H - COL_H) // len(DEPARTURES)
    row_top = HEADER_H + COL_H

    for i, (dest, mins, status) in enumerate(DEPARTURES):
        y0 = row_top + i * ROW_H
        y1 = y0 + ROW_H

        # Alternating row shading (light stripe via dashed pattern — use outline rect)
        if i % 2 == 0:
            draw.rectangle((0, y0, W, y1 - 1), outline=0, width=1)
        else:
            draw.rectangle((0, y0, W, y1 - 1), fill=0)

        txt_fill   = 255 if i % 2 != 0 else 0
        delay_fill = txt_fill  # will invert for DELAYED below

        depart_time = now + timedelta(minutes=mins)
        time_str = depart_time.strftime("%-I:%M %p")
        mins_str = f"{mins} min"

        ty = y0 + (ROW_H - 26) // 2

        # Destination
        draw.text((COL_DEST + 20, ty), dest, font=font_reg, fill=txt_fill)

        # Departure time
        draw.text((COL_TIME + 10, ty), time_str, font=font_reg, fill=txt_fill)

        # Minutes
        draw.text((COL_MINS + 10, ty), mins_str, font=font_reg, fill=txt_fill)

        # Status — highlight DELAYED with inverted badge
        if status == "DELAYED":
            s_bbox = draw.textbbox((0, 0), status, font=font_small)
            s_w = s_bbox[2] - s_bbox[0]
            s_h = s_bbox[3] - s_bbox[1]
            pad = 6
            bx = COL_STATUS + 10
            by = ty - pad
            draw.rectangle((bx - pad, by, bx + s_w + pad, by + s_h + pad * 2),
                            fill=txt_fill)
            draw.text((bx, ty), status, font=font_small, fill=delay_fill ^ 255)
        else:
            draw.text((COL_STATUS + 10, ty), status, font=font_small, fill=txt_fill)

        # Vertical dividers
        for x in (COL_TIME, COL_MINS, COL_STATUS):
            draw.line((x, y0, x, y1), fill=txt_fill, width=1)

    # ── Footer ───────────────────────────────────────────────────────────────
    draw.rectangle((0, H - 28, W, H), fill=0)
    footer = "Departures from Grove St  |  NJ PATH  |  Last updated: " + now.strftime("%-I:%M:%S %p")
    draw.text((16, H - 22), footer, font=ImageFont.truetype(FONT_PATH_REG, 16), fill=255)

    return image

def main():
    print("Initializing display...")
    epd = epd13in3k.EPD()
    epd.init()
    epd.Clear()

    print("Drawing departure board...")
    image = draw_schedule(epd)
    print("Sending to display (this takes ~15-20 seconds)...")
    epd.display(epd.getbuffer(image))
    print("Done! Sleeping display...")
    time.sleep(3)
    epd.sleep()
    print("Display is asleep. All done!")

if __name__ == '__main__':
    main()
