import board
import digitalio
from adafruit_rgb_display import ili9341
from PIL import Image, ImageDraw, ImageFont

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

# text = "A quick brown fox jumped over on a lazy sunday ofcourse."
(x, y, font_width, font_height) = font.getbbox(text)

x_pos = BORDER  # Align to top-right corner
y_pos = BORDER

# Function to draw multiline text
def draw_text(draw, text, position, font, fill):
    draw.rectangle((0, 0, width, height), fill=FOREFROUND_FONT_COLOR)
    disp.image(image)

    lines = text.split("\n")
    print(f"Line 53 {position}")
    y = position[1]
    for line in lines:
        draw.text((position[1], y), line, font=font, fill=fill)
        y += font.getbbox(line)[1]
    draw_text(draw, text, (x_pos, y_pos), font, fill=(255, 255, 255))


    disp.image(image)


def draw_text2(draw, text, position, font, fill):
    words = text.split()  # Split text into words
    lines = ['']  # Initialize lines list with an empty string
    
    for word in words:
        # Check if adding the next word exceeds the width
        if font.getbbox(lines[0] + word)[0] <= (width - 2 * BORDER):
            print("Exceeding Width")
            lines[0] += word + ' '
        else:
            print("Not exceeding width")
            lines.append(word + ' ')

    y = position[1]
    for line in lines:
        draw.text((position[0], y), line, font=font, fill=fill)
        y += font.getbbox(line)[1]


