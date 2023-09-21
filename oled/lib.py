import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display import ili9341

class DisplayController:
    def __init__(self):
        self.BORDER = 10
        self.BAUDRATE = 24000000
        self.FOREGROUND_FONT_COLOR = (0, 0, 0)
        self.rotation = 90  # Modify this if needed
        self.initialize_display()
        self.initialize_image()
        self.font = ImageFont.load_default()


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

    def draw_text(self, text, position, fill):
        lines = text.split("\n")
        y = position[1]
        for line in lines:
            self.draw.text((position[0], y), line, font=self.font, fill=fill)
            y += self.font.getbbox(line)[1]

    def clear_screen(self):
        self.draw.rectangle((0, 0, self.width, self.height), fill=self.FOREGROUND_FONT_COLOR)
        self.disp.image(self.image)

    def display_image(self):
        self.disp.image(self.image)

# Example Usage:
# controller = DisplayController()
# controller.render_text("Ramkrishna Paramahamsa Ki Jai!")
