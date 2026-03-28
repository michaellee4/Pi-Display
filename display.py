"""
display.py — Draw the split calendar + PATH departure board directly with PIL
and send to the e-ink display.

Run normally:   python3 display.py
Preview to PNG: python3 display.py --preview
"""

import sys
import os
import time
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont

EPAPER_LIB = os.path.join(os.path.dirname(__file__), 'e-Paper/RaspberryPi_JetsonNano/python/lib')
sys.path.append(EPAPER_LIB)

# ── Canvas ───────────────────────────────────────────────────────────────────
W, H    = 960, 680
PAD     = 8
GAP     = 8
CAL_W   = 560
DEP_W   = W - PAD * 2 - GAP - CAL_W   # 376
PANEL_H = H - PAD * 2                  # 664

# ── Grayscale tones ──────────────────────────────────────────────────────────
WHITE      = 255
BG         = 228   # outer background
OFF_WHITE  = 245   # alternating row tint
LIGHT_GRAY = 210   # cell/row borders
GRAY       = 140   # secondary text, event pills
MID        = 80    # day-name bar
DARK       = 40    # header backgrounds, primary text
BLACK      = 0

# ── Fonts ────────────────────────────────────────────────────────────────────
_BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
_REG  = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'

def F(bold, size):
    return ImageFont.truetype(_BOLD if bold else _REG, size)

# ── Calendar data ─────────────────────────────────────────────────────────────
MONTH     = "March"
YEAR      = "2026"
START_DOW = 0       # March 1, 2026 = Sunday
DAYS      = 31
TODAY     = 27
DAY_NAMES = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

EVENTS = {
    3:  ["Standup 9am"],
    7:  ["Birthday 6pm"],
    10: ["Doctor 2pm"],
    14: ["Pi Day!"],
    17: ["St. Pat's Day", "Lunch w/ Sarah"],
    20: ["Spring Equinox"],
    25: ["Deadline"],
    27: ["Coffee 10am"],
    28: ["Movie Night"],
}

# ── Departure data ─────────────────────────────────────────────────────────────
NOW = datetime.now()

DEPARTURES = [
    ("WTC",    2,  "ON TIME"),
    ("33rd",   6,  "ON TIME"),
    ("JSQ",    9,  "ON TIME"),
    ("WTC",    13, "DELAYED"),
    ("Newark", 17, "ON TIME"),
    ("HOB",    21, "ON TIME"),
    ("33rd",   25, "ON TIME"),
    ("WTC",    31, "ON TIME"),
]


# ── Helpers ──────────────────────────────────────────────────────────────────
def text_size(draw, text, font):
    b = draw.textbbox((0, 0), text, font=font)
    return b[2] - b[0], b[3] - b[1]

def draw_text_centered(draw, text, font, fill, cx, cy):
    tw, th = text_size(draw, text, font)
    draw.text((cx - tw // 2, cy - th // 2), text, font=font, fill=fill)

def cap_rect(draw, x, y, w, h, fill):
    """Rectangle that squares off the top corners of a rounded rect."""
    draw.rectangle([x, y, x + w, y + h], fill=fill)


# ── Calendar panel ────────────────────────────────────────────────────────────
def draw_calendar(draw, ox, oy):
    HEADER_H  = 68
    DAYNAME_H = 22
    GRID_TOP  = HEADER_H + DAYNAME_H
    CELL_W    = CAL_W // 7           # 80
    CELL_H    = (PANEL_H - GRID_TOP) // 6  # 95

    f_month = F(True,  24)
    f_year  = F(False, 11)
    f_day   = F(True,  11)
    f_date  = F(True,  14)
    f_event = F(True,  10)

    # Panel
    draw.rounded_rectangle([ox, oy, ox+CAL_W, oy+PANEL_H], radius=16, fill=WHITE)

    # Header
    draw.rounded_rectangle([ox, oy, ox+CAL_W, oy+HEADER_H], radius=16, fill=DARK)
    cap_rect(draw, ox, oy+HEADER_H-16, CAL_W, 16, DARK)

    mw, mh = text_size(draw, MONTH, f_month)
    yw, yh = text_size(draw, YEAR,  f_year)
    total  = mh + 4 + yh
    sy     = oy + (HEADER_H - total) // 2
    draw.text((ox + (CAL_W - mw) // 2, sy),          MONTH, font=f_month, fill=WHITE)
    draw.text((ox + (CAL_W - yw) // 2, sy + mh + 4), YEAR,  font=f_year,  fill=WHITE)

    # Day names bar
    draw.rectangle([ox, oy+HEADER_H, ox+CAL_W, oy+HEADER_H+DAYNAME_H], fill=MID)
    for i, name in enumerate(DAY_NAMES):
        cx = ox + i * CELL_W + CELL_W // 2
        cy = oy + HEADER_H + DAYNAME_H // 2
        draw_text_centered(draw, name, f_day, WHITE, cx, cy)

    # Grid
    day = 1
    for row in range(6):
        for col in range(7):
            if row * 7 + col < START_DOW or day > DAYS:
                # Empty cell
                cx0 = ox + col * CELL_W
                cy0 = oy + GRID_TOP + row * CELL_H
                draw.rectangle([cx0, cy0, cx0+CELL_W, cy0+CELL_H], fill=OFF_WHITE, outline=LIGHT_GRAY)
                continue

            cx0 = ox + col * CELL_W
            cy0 = oy + GRID_TOP + row * CELL_H
            cx1, cy1 = cx0 + CELL_W, cy0 + CELL_H

            draw.rectangle([cx0, cy0, cx1, cy1], fill=WHITE, outline=LIGHT_GRAY)

            if day == TODAY:
                draw.rectangle([cx0+1, cy0+1, cx1-1, cy1-1], outline=MID, width=2)

            draw.text((cx0+5, cy0+4), str(day), font=f_date, fill=DARK)

            if day in EVENTS:
                _, dh = text_size(draw, str(day), f_date)
                ey = cy0 + 4 + dh + 3
                for evt in EVENTS[day][:2]:
                    ew, eh = text_size(draw, evt, f_event)
                    pill_w = min(ew + 6, CELL_W - 8)
                    if ey + eh + 4 <= cy1 - 2:
                        draw.rounded_rectangle([cx0+3, ey, cx0+3+pill_w, ey+eh+4], radius=3, fill=GRAY)
                        draw.text((cx0+6, ey+2), evt, font=f_event, fill=WHITE)
                        ey += eh + 6

            day += 1


# ── Departures panel ──────────────────────────────────────────────────────────
def draw_departures(draw, ox, oy):
    HEADER_H = 90
    NEXT_H   = 72
    COL_H    = 24
    FOOTER_H = 28
    n_rows   = len(DEPARTURES) - 1
    ROW_H    = (PANEL_H - HEADER_H - NEXT_H - COL_H - FOOTER_H) // n_rows

    f_label  = F(False, 10)
    f_name   = F(True,  22)
    f_time   = F(False, 18)
    f_badge  = F(True,  12)
    f_col    = F(True,   9)
    f_next_d = F(True,  20)
    f_dest   = F(True,  14)
    f_row_t  = F(False, 13)
    f_mins   = F(True,  14)
    f_status = F(True,  10)
    f_footer = F(False, 11)

    # Panel
    draw.rounded_rectangle([ox, oy, ox+DEP_W, oy+PANEL_H], radius=16, fill=WHITE)

    # Header
    draw.rounded_rectangle([ox, oy, ox+DEP_W, oy+HEADER_H], radius=16, fill=DARK)
    cap_rect(draw, ox, oy+HEADER_H-16, DEP_W, 16, DARK)

    draw.text((ox+16, oy+12), "NJ Transit — PATH", font=f_label, fill=GRAY)
    draw.text((ox+16, oy+28), "Grove Street",      font=f_name,  fill=WHITE)

    time_str = NOW.strftime("%-I:%M %p")
    tw, _ = text_size(draw, time_str, f_time)
    draw.text((ox+DEP_W-16-tw, oy+12), time_str, font=f_time, fill=WHITE)

    badge = "PATH"
    bw, bh = text_size(draw, badge, f_badge)
    bx = ox+DEP_W-16-bw-14
    draw.rounded_rectangle([bx, oy+48, bx+bw+14, oy+70], radius=5, outline=WHITE, width=2)
    draw.text((bx+7, oy+51), badge, font=f_badge, fill=WHITE)

    # Next train
    nd, nm, _ = DEPARTURES[0]
    nt = (NOW + timedelta(minutes=nm)).strftime("%-I:%M %p")
    draw.rectangle([ox, oy+HEADER_H, ox+DEP_W, oy+HEADER_H+NEXT_H], fill=OFF_WHITE)
    draw.line([ox, oy+HEADER_H+NEXT_H, ox+DEP_W, oy+HEADER_H+NEXT_H], fill=LIGHT_GRAY)

    draw.text((ox+16, oy+HEADER_H+8),  "NEXT TRAIN", font=f_col,    fill=GRAY)
    draw.text((ox+16, oy+HEADER_H+22), nd,           font=f_next_d, fill=DARK)
    draw.text((ox+16, oy+HEADER_H+48), nt,           font=f_row_t,  fill=GRAY)

    mins_str = str(nm)
    mw, mh = text_size(draw, mins_str, f_next_d)
    uw, _  = text_size(draw, "min", f_col)
    pill_w = mw + uw + 20
    pill_x = ox+DEP_W-16-pill_w
    pill_y = oy+HEADER_H+16
    draw.rounded_rectangle([pill_x, pill_y, pill_x+pill_w, pill_y+40], radius=10, fill=DARK)
    draw.text((pill_x+10,         pill_y+8),  mins_str, font=f_next_d, fill=WHITE)
    draw.text((pill_x+10+mw+4,    pill_y+20), "min",    font=f_col,    fill=WHITE)

    # Column headers
    C_DEST = ox+16
    C_TIME = ox+DEP_W-240
    C_MINS = ox+DEP_W-148
    C_STAT = ox+DEP_W-76

    col_y = oy+HEADER_H+NEXT_H
    draw.rectangle([ox, col_y, ox+DEP_W, col_y+COL_H], fill=OFF_WHITE)
    draw.line([ox, col_y+COL_H, ox+DEP_W, col_y+COL_H], fill=LIGHT_GRAY)
    for x, label in [(C_DEST,"DEST"), (C_TIME,"TIME"), (C_MINS,"MINS"), (C_STAT,"STATUS")]:
        draw.text((x, col_y+7), label, font=f_col, fill=GRAY)

    # Rows
    for i, (dest, mins, status) in enumerate(DEPARTURES[1:]):
        ry  = col_y + COL_H + i * ROW_H
        bg  = WHITE if i % 2 == 0 else OFF_WHITE
        dep = (NOW + timedelta(minutes=mins)).strftime("%-I:%M")
        draw.rectangle([ox, ry, ox+DEP_W, ry+ROW_H], fill=bg)
        draw.line([ox, ry+ROW_H, ox+DEP_W, ry+ROW_H], fill=LIGHT_GRAY)

        ty = ry + (ROW_H - 14) // 2
        draw.text((C_DEST, ty), dest,       font=f_dest,   fill=DARK)
        draw.text((C_TIME, ty), dep,        font=f_row_t,  fill=GRAY)
        draw.text((C_MINS, ty), f"{mins}m", font=f_mins,   fill=DARK)

        if status == "DELAYED":
            sw, sh = text_size(draw, status, f_status)
            draw.rounded_rectangle([C_STAT-4, ty-3, C_STAT+sw+8, ty+sh+3], radius=3, outline=DARK, width=2)
            draw.text((C_STAT+2, ty), status, font=f_status, fill=DARK)
        else:
            draw.text((C_STAT, ty), status, font=f_status, fill=GRAY)

    # Footer
    draw.rounded_rectangle([ox, oy+PANEL_H-FOOTER_H, ox+DEP_W, oy+PANEL_H], radius=16, fill=DARK)
    cap_rect(draw, ox, oy+PANEL_H-FOOTER_H, DEP_W, 16, DARK)
    footer = f"Grove St · PATH · Updated {NOW.strftime('%-I:%M %p')}"
    draw.text((ox+16, oy+PANEL_H-FOOTER_H+8), footer, font=f_footer, fill=GRAY)


# ── Main ──────────────────────────────────────────────────────────────────────
def generate():
    img  = Image.new('L', (W, H), color=BG)
    draw = ImageDraw.Draw(img)
    draw_calendar(draw,   PAD,                  PAD)
    draw_departures(draw, PAD + CAL_W + GAP,    PAD)
    return img


def main():
    preview = '--preview' in sys.argv

    print("Generating image...")
    img = generate()

    if preview:
        out = os.path.join(os.path.dirname(__file__), 'preview.png')
        img.save(out)
        print(f"Saved preview to {out}")
        return

    from waveshare_epd import epd13in3k
    bw = img.convert('1')
    print("Initializing display...")
    epd = epd13in3k.EPD()
    epd.init()
    epd.Clear()
    print("Sending to display (~15-20s)...")
    epd.display(epd.getbuffer(bw))
    epd.sleep()
    print("Done.")


if __name__ == '__main__':
    main()
