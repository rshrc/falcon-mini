import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display import ili9341
import threading

FONT_PATH = './DejaVuSans.ttf'

class DisplayController:
    def __init__(self):
        self.BORDER = 10
        self.BAUDRATE = 24000000
        self.FOREGROUND_FONT_COLOR = (0, 0, 0)
        self.rotation = 90  # Modify this if needed
        self.initialize_display()
        self.initialize_image()
        self.font = ImageFont.truetype(FONT_PATH, size=18)


    def initialize_display(self):
        cs_pin = digitalio.DigitalInOut(board.CE0)
        dc_pin = digitalio.DigitalInOut(board.D25)
        reset_pin = digitalio.DigitalInOut(board.D24)
        spi = board.SPI()

        self.disp = ili9341.ILI9341(
            spi,
            rotation=self.rotation,
            cs=cs_pin,
            dc=dc_pin,
            rst=reset_pin,
            baudrate=self.BAUDRATE,
        )

        if self.disp.rotation % 180 == 90:
            self.height = self.disp.width
            self.width = self.disp.height
        else:
            self.width = self.disp.width
            self.height = self.disp.height

    def initialize_image(self):
        self.image = Image.new("RGB", (self.width, self.height))
        self.draw = ImageDraw.Draw(self.image)

        self.draw.rectangle((0, 0, self.width, self.height), fill=self.FOREGROUND_FONT_COLOR)
        self.disp.image(self.image)

    def render_text(self, text):
        (x, y, font_width, font_height) = self.font.getbbox(text)
        x_pos = self.BORDER
        y_pos = self.BORDER

        self.clear_screen()
        self.draw_text(text, (x_pos, y_pos), (255, 255, 255))
        self.display_image()
    
    def render_text_threaded(self, text):
        thread = threading.Thread(target=self.render_text, args=(text,))
        thread.start()

    
    def add_newlines(self, text):
        lines = []
        while text:
            if len(text) <= 25:
                lines.append(text)
                break
            else:
                # Find the last space within the first 25 characters
                last_space = text[:25].rfind(' ')
                if last_space == -1:
                    # If no space is found, split at exactly 25 characters
                    lines.append(text[:25])
                    text = text[25:]
                else:
                    # Split at the last space within the first 25 characters
                    lines.append(text[:last_space])
                    text = text[last_space+1:]
        return '\n'.join(lines)

    def draw_text(self, text, position, fill):
        # print(f"Line 78 {self.add_newlines(text)}")
        lines = self.add_newlines(text).split("\n")
        y = position[1]
        for line in lines:
            self.draw.text((position[0], y), line, font=self.font, fill=fill)
            # y += self.font.getbbox(line)[1]
            y = y+20

    def clear_screen(self):
        self.draw.rectangle((0, 0, self.width, self.height), fill=self.FOREGROUND_FONT_COLOR)
        self.disp.image(self.image)

    def display_image(self):
        self.disp.image(self.image)
