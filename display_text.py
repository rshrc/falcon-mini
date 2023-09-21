import board
import busio
import digitalio
import adafruit_rgb_display.ili9341 as ili9341
from PIL import Image, ImageDraw, ImageFont
import time

# Set up the display
spi = busio.SPI(clock=board.SCK, MOSI=board.MOSI, MISO=board.MISO)
dc = digitalio.DigitalInOut(board.D22)
cs = digitalio.DigitalInOut(board.D24)
reset = digitalio.DigitalInOut(board.D18)

display = ili9341.ILI9341(spi, cs=cs, dc=dc, rst=reset)

# Create a PIL image and draw on it
image = Image.new("RGB", (display.width, display.height))
draw = ImageDraw.Draw(image)
draw.rectangle((0, 0, display.width, display.height), fill=(0, 0, 0))

# Load a font
font = ImageFont.load_default()

# Draw text
draw.text((40, 40), "Hello, World!", font=font, fill=(0, 0, 0))

# Display image
display.image(image)

time.sleep(10)
