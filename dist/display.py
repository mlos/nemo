#!/usr/bin/env python
#
# (c) 2018 Maarten Los. All rights reserved.
# 
#
import os
import time
import sys
from PIL import ImageFont, Image, ImageDraw
from luma.core import cmdline
from luma.core.render import canvas
from luma.core.image_composition import ImageComposition, ComposableImage

titles = [
    ("Bridge over troubled water", "Simon & Garfunkel"),
    ("Up", "R.E.M."),
    ("Wild Child", "Lou Reed & The Velvet Underground"),
    ("(Shake Shake Shake) Shake your body", "KC & The Sunshine Band"),
]


class TextImage():
    def __init__(self, device, text, font):
        with canvas(device) as draw:
            w, h = draw.textsize(text, font)
        self.image = Image.new(device.mode, (w, h))
        draw = ImageDraw.Draw(self.image)
        draw.text((0, 0), text, font=font, fill="white")
        del draw
        self.width = w
        self.height = h


class Synchroniser():
    def __init__(self):
        self.synchronised = {}

    def busy(self, task):
        self.synchronised[id(task)] = False

    def ready(self, task):
        self.synchronised[id(task)] = True

    def is_synchronised(self):
        for task in self.synchronised.iteritems():
            if task[1] is False:
                return False
        return True


class Scroller():
    WAIT_SCROLL = 1
    SCROLLING = 2
    WAIT_REWIND = 3
    WAIT_SYNC = 4

    def __init__(self, image_composition, rendered_image, scroll_delay, synchroniser):
        self.image_composition = image_composition
        self.speed = 1
        self.image_x_pos = 0
        self.rendered_image = rendered_image
        self.image_composition.add_image(rendered_image)
        self.max_pos = rendered_image.width - image_composition().width
        self.delay = scroll_delay
        self.ticks = 0
        self.state = self.WAIT_SCROLL
        self.synchroniser = synchroniser
        self.render()
        self.synchroniser.busy(self)
        self.cycles = 0
        self.must_scroll = self.max_pos > 0

    def __del__(self):
        self.image_composition.remove_image(self.rendered_image)

    def tick(self):

        # Repeats the following sequence:
        #  wait - scroll - wait - rewind -> sync with other scrollers -> wait
        if self.state == self.WAIT_SCROLL:
            if not self.is_waiting():
                self.cycles += 1
                self.state = self.SCROLLING
                self.synchroniser.busy(self)

        elif self.state == self.WAIT_REWIND:
            if not self.is_waiting():
                self.synchroniser.ready(self)
                self.state = self.WAIT_SYNC

        elif self.state == self.WAIT_SYNC:
            if self.synchroniser.is_synchronised():
                if self.must_scroll:
                    self.image_x_pos = 0
                    self.render()
                self.state = self.WAIT_SCROLL

        elif self.state == self.SCROLLING:
            if self.image_x_pos < self.max_pos:
                if self.must_scroll:
                    self.render()
                    self.image_x_pos += self.speed
            else:
                self.state = self.WAIT_REWIND

    def render(self):
        self.rendered_image.offset = (self.image_x_pos, 0)

    def is_waiting(self):
        self.ticks += 1
        if self.ticks > self.delay:
            self.ticks = 0
            return False
        return True

    def get_cycles(self):
        return self.cycles


def make_font(name, size):
    font_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), 'fonts', name))
    return ImageFont.truetype(font_path, size)


def make_bitmap(name):
    bitmap_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), 'bitmaps', name))
    return Image.open(bitmap_path)


def get_device():
    parser = cmdline.create_parser(description='nemo')
    args = parser.parse_args(sys.argv[1:])
    return cmdline.create_device(args)

# ------- main

device = get_device()
fnt = make_font("PixelOperator.ttf", 16)

bounds = device.bounding_box # [ left, top, right, bottom ]
top_line = [0, 0, bounds[2], 0]
bottom_line = [0, bounds[3],  bounds[2], bounds[3] ]
play = make_bitmap("play.png")


# Modes:
# 1 - Showing boot message
# 2 - Showing goodbye message
# 3 - Showing copyright + info
# 4 - Rendering artist + song + status
mode = 1

def draw_marker(d):
    d.rectangle(top_line, outline="white")
    d.rectangle(bottom_line, outline="white")
    
    
def showing_boot_message():
    message = "Welcome to Nemo"
    with canvas(device) as draw:
        draw_marker(draw)
        size = draw.textsize(message, font=fnt)
        left = device.width//2 - size[0]//2
        top = device.height//2 - size[1]//2 - 5
        draw.text((left, top), message, fill="white", font=fnt)


showing_boot_message()
while True:
    time.sleep(1)
    

image_composition = ImageComposition(device)

try:
    ci_play = ComposableImage(make_bitmap("play.png"), position=(0, 50))
    ci_pause = ComposableImage(make_bitmap("pause.png"), position=(0, 50))
    image_composition.add_image(ci_play)
    image_composition.remove_image(ci_play)
    image_composition.add_image(ci_pause)
    while True:
        for title in titles:
            synchroniser = Synchroniser()
            ci_song = ComposableImage(TextImage(device, title[0], fnt).image, position=(0, 1))
            ci_artist = ComposableImage(TextImage(device, title[1], fnt).image, position=(0, 20))
            song = Scroller(image_composition, ci_song, 100, synchroniser)
            artist = Scroller(image_composition, ci_artist, 100, synchroniser)
            cycles = 0

            while cycles < 3:
                artist.tick()
                song.tick()
                time.sleep(0.025)
                cycles = song.get_cycles()

                with canvas(device, background=image_composition()) as draw:
                    image_composition.refresh()
                    #draw.rectangle(device.bounding_box, outline="white")
                    draw_marker(draw)
                    #draw.rectangle(top_line, outline="white")
                    #draw.rectangle(bottom_line, outline="white")

            del artist
            del song

except KeyboardInterrupt:
    pass

