import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display import ili9341

BORDER = 10
FONTSIZE = 14

BAUDRATE = 24000000
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = digitalio.DigitalInOut(board.D24)
spi = board.SPI()

FOREFROUND_FONT_COLOR = (0, 0, 0)

disp = ili9341.ILI9341(
    spi,
    rotation=90,  # 2.2", 2.4", 2.8", 3.2" ILI9341
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
)

if disp.rotation % 180 == 90:
    height = disp.width  # we swap height/width to rotate it to landscape!
    width = disp.height
else:
    width = disp.width  # we swap height/width to rotate it to landscape!
    height = disp.height

image = Image.new("RGB", (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a green filled box as the background
draw.rectangle((0, 0, width, height), fill=FOREFROUND_FONT_COLOR)
disp.image(image)

# Draw a smaller inner purple rectangle
# draw.rectangle(
#     (BORDER, BORDER, width - BORDER - 1, height - BORDER - 1), fill=(170, 0, 136)
# )

font = ImageFont.load_default()

text = "A quick brown fox jumped over"
(x, y, font_width, font_height) = font.getbbox(text)

draw.text(
    (width // 2 - font_width // 2, height // 2 - font_height // 2),
    text,
    fill=(255, 255, 0),
)

print(f"Line 58 : {font.getlength(text)}")

# y += font.getlength(text)[1]
# print("Line 52 : ${52}")

# Display image.
disp.image(image)