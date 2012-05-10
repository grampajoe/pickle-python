#!/usr/bin/env python

"""
Copyright 2012 Joe Friedl
See LICENSE for licensing details.
"""

import pyglet

pyglet.resource.path = ['images', 'fonts']
pyglet.resource.reindex()

from engine import Engine

if __name__ == '__main__':
    window = pyglet.window.Window(caption="Pick the Pickle!", width=640,
            height=480)

    engine = Engine(window)

    pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
    pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA, pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)

    pyglet.app.run()
