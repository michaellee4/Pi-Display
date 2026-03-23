import sys
import os
import time

sys.path.append(os.path.join(os.path.dirname(__file__), 'e-Paper/RaspberryPi_JetsonNano/python/lib'))

from waveshare_epd import epd13in3k
from PIL import Image, ImageDraw, ImageFont

FONT_PATH = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FONT_PATH_REG = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'

# March 2026 starts on Sunday
MONTH_TITLE = "March 2026"
START_DOW = 0  # 0 = Sunday
DAYS_IN_MONTH = 31
DAY_NAMES = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
TODAY = 22

EVENTS = {
    3:  ["Team Standup 9am"],
    7:  ["Birthday Party 6pm"],
    10: ["Doctor Appt 2pm"],
    14: ["Pi Day!"],
    17: ["St. Patrick's Day", "Lunch w/ Sarah"],
    20: ["Spring Equinox", "Yoga Class 7pm"],
    22: ["Project Deadline"],
    25: ["Coffee w/ Jake 10am"],
    28: ["Movie Night 8pm"],
}

def draw_calendar(epd):
    W, H = epd.width, epd.height  # 960 x 680
    image = Image.new('1', (W, H), 255)
    draw = ImageDraw.Draw(image)

    font_title = ImageFont.truetype(FONT_PATH, 48)
    font_day   = ImageFont.truetype(FONT_PATH, 22)
    font_date  = ImageFont.truetype(FONT_PATH, 26)
    font_event = ImageFont.truetype(FONT_PATH_REG, 15)

    HEADER_H = 60
    DAYNAME_H = 36
    COLS = 7
    ROWS = 6
    col_w = W // COLS
    row_h = (H - HEADER_H - DAYNAME_H) // ROWS

    # Title
    title_bbox = draw.textbbox((0, 0), MONTH_TITLE, font=font_title)
    title_w = title_bbox[2] - title_bbox[0]
    draw.text(((W - title_w) // 2, 8), MONTH_TITLE, font=font_title, fill=0)

    # Day name headers
    day_y = HEADER_H
    for i, name in enumerate(DAY_NAMES):
        x = i * col_w
        draw.rectangle((x, day_y, x + col_w, day_y + DAYNAME_H), fill=0)
        bbox = draw.textbbox((0, 0), name, font=font_day)
        tx = x + (col_w - (bbox[2] - bbox[0])) // 2
        ty = day_y + (DAYNAME_H - (bbox[3] - bbox[1])) // 2
        draw.text((tx, ty), name, font=font_day, fill=255)

    # Grid lines and dates
    grid_top = HEADER_H + DAYNAME_H
    day = 1
    for row in range(ROWS):
        for col in range(COLS):
            cell_num = row * COLS + col
            if cell_num < START_DOW or day > DAYS_IN_MONTH:
                # Empty cell
                x0 = col * col_w
                y0 = grid_top + row * row_h
                draw.rectangle((x0, y0, x0 + col_w, y0 + row_h), outline=0, width=1)
                continue

            x0 = col * col_w
            y0 = grid_top + row * row_h
            x1 = x0 + col_w
            y1 = y0 + row_h

            # Cell border — thicker for today
            if day == TODAY:
                draw.rectangle((x0, y0, x1, y1), outline=0, width=3)
            else:
                draw.rectangle((x0, y0, x1, y1), outline=0, width=1)

            # Date number
            date_str = str(day)
            if day == TODAY:
                # Black circle behind today's date
                r = 16
                draw.ellipse((x0 + 6, y0 + 4, x0 + 6 + r*2, y0 + 4 + r*2), fill=0)
                draw.text((x0 + 6 + r - draw.textbbox((0,0), date_str, font=font_date)[2]//2,
                            y0 + 4 + r - draw.textbbox((0,0), date_str, font=font_date)[3]//2),
                           date_str, font=font_date, fill=255)
            else:
                draw.text((x0 + 8, y0 + 4), date_str, font=font_date, fill=0)

            # Events
            if day in EVENTS:
                for i, event in enumerate(EVENTS[day][:2]):  # max 2 events per cell
                    ey = y0 + 34 + i * 18
                    if ey + 16 < y1:
                        # Truncate text to fit cell width
                        text = event
                        while draw.textbbox((0,0), text, font=font_event)[2] > col_w - 10 and len(text) > 3:
                            text = text[:-4] + '...'
                        draw.text((x0 + 5, ey), text, font=font_event, fill=0)

            day += 1

    return image

def main():
    print("Initializing display...")
    epd = epd13in3k.EPD()
    epd.init()
    epd.Clear()

    print("Drawing calendar...")
    image = draw_calendar(epd)
    print("Sending to display (this takes ~15-20 seconds)...")
    epd.display(epd.getbuffer(image))
    print("Done! Sleeping display...")
    time.sleep(3)
    epd.sleep()
    print("Display is asleep. All done!")

if __name__ == '__main__':
    main()
