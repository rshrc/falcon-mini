# sudo -H pip3 install luma.oled
# sudo apt-get install python3-pil
# sudo usermod -a -G spi,gpio,i2c rishi

import argparse
import random
import threading
from time import sleep

from luma.core.interface.serial import i2c, spi
from luma.core.render import canvas
from luma.oled.device import ili9341, sh1106, ssd1306, ssd1325, ssd1331

serial = spi(port=1, address=0x3C)
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


def display(input, duration=3):
    with canvas(device) as draw:
        draw.rectangle(device.bounding_box, outline="white", fill="black")
        draw.text((4, 4), add_newlines(input), fill="white")
    sleep(duration)

# Box and text rendered in portrait mode
while False:
    with canvas(device) as draw:
        draw.rectangle(device.bounding_box, outline="white", fill="black")
        draw.text((4, 4), add_newlines(random.choice(random_sentences)), fill="white")
    sleep(3)

def main(message, **kwargs):
    # Your code here
    # display(message)
    display_thread = threading.Thread(target=display, args=(message, kwargs['duration']))
    display_thread.start()



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Description of your script.')

    parser.add_argument('input', type=str, help='Display Text for OLED')
    parser.add_argument('time', type=int,  help='Duration for Text Display')



    args = parser.parse_args()


    main(args.input, duration=args.time)

