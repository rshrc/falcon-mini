# sudo -H pip3 install luma.oled
# sudo apt-get install python3-pil
# sudo usermod -a -G spi,gpio,i2c rishi

from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306, ssd1325, ssd1331, sh1106
from time import sleep
import random

serial = i2c(port=1, address=0x3C)
device = sh1106(serial, rotate=0)

random_sentences = [
    "The quick brown fox\njumps over the lazy\ndog.",
    "The sun sets behind the mountains in a blaze of colors.",
    "She walked along the beach, feeling the sand between her toes.",
    "The old library was filled with the scent of aging books.",
    "After the rain, a rainbow stretched across the sky.",
    "He sipped his coffee and gazed out the window at the bustling city.",
    "The stars glittered like diamonds in the night sky.",
    "The smell of fresh-baked bread filled the air.",
    "She danced through life with a heart full of dreams.",
    "The ancient castle stood in silent grandeur, overlooking the village."
]

def add_newlines(sentence, max_line_length=16):
    words = sentence.split()
    lines = []
    current_line = ''

    for word in words:
        if len(current_line) + len(word) <= max_line_length:
            current_line += ("" if current_line == '' else ' ') + word
        else:
            lines.append(current_line)
            current_line = word

    lines.append(current_line)  # Append the last line

    return '\n'.join(lines)


# Box and text rendered in portrait mode
while True:
    with canvas(device) as draw:
        draw.rectangle(device.bounding_box, outline="white", fill="black")
        draw.text((4, 4), add_newlines(random.choice(random_sentences)), fill="white")
    sleep(3)



