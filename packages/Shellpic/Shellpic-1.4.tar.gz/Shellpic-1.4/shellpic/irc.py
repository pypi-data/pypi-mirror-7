#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#
# Lars Jørgen Solberg <supersolberg@gmail.com> 2014
#

from shellpic.formatter import Formatter

import StringIO

class Irc(Formatter):
    """
    A formatter for irc-clients.
    """

    # mIRC palette according to http://forum.xchat.org/viewtopic.php?f=6&t=7719
    palette = (
        (0xff, 0xff, 0xff), #white
        (0x0, 0x0, 0x0),    #black
        (0x0, 0x0, 0x7f),   #blue (navy)
        (0x0, 0x93, 0x0),   #green
        (0xff, 0x0, 0x0),   #red
        (0x7f, 0x0, 0x0),   #brown (maroon)
        (0x9c, 0x0, 0x9c),  #purple
        (0xfc, 0x7f, 0x0),  #orange (olive)
        (0xff, 0xff, 0x0),  #yellow
        (0x0, 0xfc, 0x0),   #light green (lime)
        (0x0, 0x93, 0x93),  #teal
        (0x0, 0xff, 0xff),  #light cyan
        (0x0, 0x0, 0xfc),   #light blue
        (0xff, 0x0, 0xff),  #pink
        (0x7f, 0x7f, 0x7f), #grey
        (0xd2, 0xd2, 0xd2)  #light gray
        )

    # colors with a higher weight will be used more often
    # i should probably figure out a better way to map colors...
    weights = (
    0.5, #white
    1,   #black
    1,   #blue (navy)
    2,   #green
    0.5, #red
    0.5, #brown (maroon)
    0.5, #purple
    0.5, #orange (olive)
    2,   #yellow
    2,   #light green (lime)
    2,   #teal
    0.5, #light cyan
    0.5, #light blue
    2,   #ping
    0.5, #grey
    0.5  #light gray
    )


    def __init__(self):
        super(Irc, self).__init__()

    @staticmethod
    def dimentions():
        return (50, 50) # guesstimation of how much room is normally available in a chatwindow

    def format(self, image, dispose=None):
        def off(x, y):
            """ the string offset for a coordinate """
            return (y * width) + x

        assert image.mode == 'RGBA'

        width, height = image.size
        pixels = [self.color(*p) for p in image.getdata()]

        file_str = StringIO.StringIO()

        yrange = height if height % 2 == 0 else height - 1
        for y in range(0, yrange, 2):
            for x in range(0, width):
                file_str.write(chr(3) + str(pixels[off(x, y + 1)]) + u"," + str(pixels[off(x, y)]) + u"▄")
            file_str.write(chr(3) + u"\n")
        if height % 2 != 0:
            for x in range(0, width):
                file_str.write(chr(3) + "1," + str(pixels[off(x, height - 1)]) + u"▄")
            file_str.write(chr(3) + u"\n")
        return file_str.getvalue()

    @classmethod
    def color(cls, r, g, b, a):
        # ugh, there is probably better way of doing this, but i can't make heads or tails of
        # the PIL documentation
        def distance(a, b):
            return sum([pow(x - y, 2) for x, y in zip(a, b)])
        distances = [[distance(p, [r, g, b]), i] for i, p in enumerate(cls.palette)]
        for d in distances:
            d[0] /= cls.weights[d[1]]
        distances.sort(key=lambda x: x[0])
        return distances[0][1]
