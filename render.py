"""
render.py — render an HTML file to the e-ink display via headless Chromium.

Usage:
    python3 render.py <path-to-html-file>
"""

import sys
import os
import subprocess
import tempfile

DISPLAY_W = 960
DISPLAY_H = 680

EPAPER_LIB = os.path.join(os.path.dirname(__file__), 'e-Paper/RaspberryPi_JetsonNano/python/lib')
sys.path.append(EPAPER_LIB)

from PIL import Image
from waveshare_epd import epd13in3k


def screenshot_html(html_path: str) -> Image.Image:
    """Use headless Chromium to render an HTML file to a PIL Image."""
    abs_path = os.path.abspath(html_path)
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
        png_path = f.name

    try:
        subprocess.run(
            [
                'chromium',
                '--headless',
                '--disable-gpu',
                '--no-sandbox',
                '--disable-software-rasterizer',
                f'--screenshot={png_path}',
                f'--window-size={DISPLAY_W},{DISPLAY_H}',
                f'file://{abs_path}',
            ],
            check=True,
            capture_output=True,
        )
        img = Image.open(png_path).convert('RGB')
    finally:
        os.unlink(png_path)

    return img


def to_bw(img: Image.Image) -> Image.Image:
    """Convert an RGB image to 1-bit black & white via threshold."""
    return img.convert('L').point(lambda x: 0 if x < 180 else 255, '1')


def send_to_display(bw_img: Image.Image):
    """Send a 1-bit PIL image to the e-ink display."""
    epd = epd13in3k.EPD()
    print("Initializing display...")
    epd.init()
    epd.Clear()
    print("Sending image (this takes ~15-20 seconds)...")
    epd.display(epd.getbuffer(bw_img))
    epd.sleep()
    print("Done.")


def render(html_path: str):
    print(f"Screenshotting {html_path}...")
    img = screenshot_html(html_path)
    bw = to_bw(img)
    send_to_display(bw)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"Usage: python3 {sys.argv[0]} <path-to-html>")
        sys.exit(1)
    render(sys.argv[1])
