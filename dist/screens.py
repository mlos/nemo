#!/usr/bin/env python
#
# (c) 2018 Maarten Los. All rights reserved.
# 
#
from PIL import Image, ImageDraw
from luma.core.render import canvas
from luma.core.image_composition import ComposableImage
import graphutils

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
        self.must_scroll = self.max_pos > 0

    def __del__(self):
        self.image_composition.remove_image(self.rendered_image)

    def tick(self):

        # Repeats the following sequence:
        #  wait - scroll - wait - rewind -> sync with other scrollers -> wait
        if self.state == self.WAIT_SCROLL:
            if not self.is_waiting():
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


class Screen(object):
    def __init__(self, device, font):
        self.device = device
        self.font = font
        bounds = device.bounding_box # [ left, top, right, bottom ]
        self.top_line = [0, 0, bounds[2], 0]
        self.bottom_line = [0, bounds[3],  bounds[2], bounds[3] ]

    def tick(self):
        raise Exception("tick() must be implemented in derived class") 
    
    def show(self):
        raise Exception("show() must be implemented in derived class") 

    def draw_marker(self, draw):
        draw.rectangle(self.top_line, outline="white")
        draw.rectangle(self.bottom_line, outline="white")
    

class MusicScreen(Screen):
    def __init__(self, device, font):
        super(MusicScreen, self).__init__(device, font)
        self.ci_play = ComposableImage(graphutils.make_bitmap("play.png"), position=(60, 48))
        self.ci_pause = ComposableImage(graphutils.make_bitmap("pause.png"), position=(60, 48))
        self.image_composition = graphutils.ImageCompositionWithHideableImage(self.device)
        self.image_composition.add_image(self.ci_play)
        self.image_composition.add_image(self.ci_pause)
        self.synchroniser = Synchroniser()
        self.has_info = False
        self.is_paused = False
        self.song_scroller = None
        self.artist_scroller = None

    def pause(self):
        self.is_paused = True
        self.image_composition.hide(self.ci_play)
        self.image_composition.unhide(self.ci_pause)

    def play(self):
        self.is_paused = False
        self.image_composition.hide(self.ci_pause)
        self.image_composition.unhide(self.ci_play)

    def set_info(self, song, artist):
        self.unset_info()
        self.ci_song = ComposableImage(TextImage(self.device, song, self.font).image, position=(0, 1))
        self.ci_artist = ComposableImage(TextImage(self.device, artist, self.font).image, position=(0, 20))
        self.song_scroller = Scroller(self.image_composition, self.ci_song, 100, self.synchroniser)
        self.artist_scroller = Scroller(self.image_composition, self.ci_artist, 100, self.synchroniser)
        self.has_info = True

    def unset_info(self):
        if self.song_scroller:
            del self.song_scroller
        if self.artist_scroller:
            del self.artist_scroller
        self.has_info = False

    def show(self):
        pass

    def tick(self):
        if self.has_info:
            self.artist_scroller.tick()
            self.song_scroller.tick()
            #time.sleep(0.025)

        with canvas(self.device, background=self.image_composition()) as draw:
            self.image_composition.refresh()
            self.draw_marker(draw)
    

class OneLineScreen(Screen):
    def __init__(self, device, font, text):
        super(OneLineScreen, self).__init__(device, font)
        self.text = text
        self.left, self.top = graphutils.text_centre(device, text, font)
        self.is_rendered = False

    def show(self):
        self.is_rendered = False

    def tick(self):
        if self.is_rendered:
            return
        self.is_rendered = True
        with canvas(self.device) as draw:
            draw.text((self.left, self.top), self.text, fill="white", font=self.font)
            self.draw_marker(draw)
