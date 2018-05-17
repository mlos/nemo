#!/usr/bin/env python
#
# (c) 2018 Maarten Los. All rights reserved.
# 
#
import os
from PIL import ImageFont, Image 

def make_font(name, size):
    font_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), 'fonts', name))
    return ImageFont.truetype(font_path, size)


def make_bitmap(name):
    bitmap_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), 'bitmaps', name))
    return Image.open(bitmap_path)
