"""
Copyright 2012 Joe Friedl
See LICENSE for licensing details.
"""

import pyglet
import math

class Background(object):
    color_1 = (47, 9, 35)
    color_2 = (67, 13, 50)

    hurt_color_1 = (128, 0, 0)
    hurt_color_2 = (64, 0, 0)

    theta = 0.0
    angular_interval = 20
    rays = None

    mode = 'normal'

    def __init__(self, game):

        # Rays extend from the middle of the screen, just below the bottom
        self.ray_length = math.sqrt((float(game.window.width)/2)**2 +
                float(game.window.height+100)**2)
        self.ray_origin = (game.window.width/2.0, -50.0)

        self.background = pyglet.graphics.vertex_list(4,
                ('v2i', (0, game.window.height, game.window.width,
                    game.window.height, game.window.width, 0, 0, 0)),
                ('c3B', self.color_1*4))

        self.update()

    def update(self, dt=1.0/60):
        """Cycle colors and move rays."""
        if self.mode == 'hurt':
            bg_color = self.hurt_color_1
            fg_color = self.hurt_color_2
        else:
            bg_color = self.color_1
            fg_color = self.color_2

        self.theta += 1 * dt
        angle = 0
        count = 0
        vertices = self.ray_origin
        while angle <= 360:
            count += 1
            angle += self.angular_interval
            vertices += (self.ray_origin[0] + self.ray_length *
                    math.cos(math.radians(angle + self.theta)),
                    self.ray_origin[1] + self.ray_length *
                    math.sin(math.radians(angle + self.theta)))
            if not count % 2:
                vertices += self.ray_origin
        if self.rays is None:
            self.rays = pyglet.graphics.vertex_list(len(vertices)/2,
                    'v2f', 'c3B')
        self.rays.vertices = vertices
        self.rays.colors = fg_color * (len(vertices)/2)

        self.background.colors = bg_color * 4

    def alternate_colors(self, dt):
        temp = self.color_1
        self.color_1 = self.color_2
        self.color_2 = temp

    def score(self):
        pyglet.clock.unschedule(self.score_done)
        pyglet.clock.unschedule(self.alternate_colors)
        if self.mode != 'normal':
            pyglet.clock.unschedule(self.hurt_done)
            self.hurt_done(0)
        self.alternate_colors(0)
        pyglet.clock.schedule_interval(self.alternate_colors, 1.0/20)
        pyglet.clock.schedule_once(self.score_done, 0.2)

    def score_done(self, dt):
        pyglet.clock.unschedule(self.alternate_colors)

    def hurt(self):
        self.mode = 'hurt'
        pyglet.clock.schedule_once(self.hurt_done, 0.1)

    def hurt_done(self, dt):
        self.mode = 'normal'

    def draw(self):
        self.background.draw(pyglet.gl.GL_QUADS)
        if self.rays is not None:
            self.rays.draw(pyglet.gl.GL_TRIANGLES)
