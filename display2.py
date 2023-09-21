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

font = ImageFont.load_default()

text = "A quick brown fox jumped over on a lazy sunday ofcourse."
(x, y, font_width, font_height) = font.getbbox(text)

x_pos = width - font_width - BORDER  # Align to top-right corner
y_pos = BORDER

# Function to draw multiline text
def draw_text(draw, text, position, font, fill):
    lines = text.split("\n")
    print(f"Line 53 {position}")
    y = position[1]
    for line in lines:
        draw.text((position[1], y), line, font=font, fill=fill)
        y += font.getbbox(line)[1]

# Clear the screen
draw.rectangle((0, 0, width, height), fill=FOREFROUND_FONT_COLOR)
disp.image(image)

# Draw text
draw_text(draw, text, (x_pos, y_pos), font, fill=(255, 255, 255))

# Display the image
disp.image(image)

# draw.text(
#     (width // 2 - font_width // 2, height // 2 - font_height // 2),
#     text,
#     fill=(255, 255, 255),
# )

# print(f"Line 58 : {font.getlength(text)}")

# # y += font.getlength(text)[1]
# # print("Line 52 : ${52}")

# # Display image.
# disp.image(image)