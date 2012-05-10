"""
Copyright 2012 Joe Friedl
See LICENSE for licensing details.
"""

import pyglet
import random
import math
from vector import *

def pick_thing(game):
    if random.random() < game.state['pickle_probability']:
        return Pickle(game)
    else:
        return Knife(game)

class Thing(object):
    hittable = True
    moving = True

    velocity = 0.0
    acceleration = 100 # Pixels/second**2

    def __init__(self, game, *args, **kwargs):
        self.game = game

        self.image.anchor_x = self.image.width/2
        self.image.anchor_y = self.image.height/2

        batch = game.sprites if not 'batch' in kwargs else kwargs['batch']

        self.sprite = pyglet.sprite.Sprite(self.image, batch=batch,
                group=game.things_group)

        self.sprite.scale = random.random() * 0.3 + 0.7

        self.sprite.x = random.randrange(0, game.window.width -
                (self.sprite.width/2))
        self.sprite.y = game.window.height + (self.sprite.height/2)

        self.horizontal_velocity = 50 * random.random()
        # Keep things from moving off screen
        if self.sprite.x > game.window.width/2:
            self.horizontal_velocity *= -1

        self.rotation = self.horizontal_velocity
        self.sprite.rotation = random.randrange(360)

    def update(self, dt):
        """Update physics, then test for collision with cursor."""
        if not self.moving:
            return False

        self.velocity += dt * self.acceleration
        self.sprite.y -= self.velocity * dt
        self.sprite.x += self.horizontal_velocity * dt
        self.sprite.rotation += self.rotation * dt
        if self.sprite.y < -(self.sprite.height):
            self.remove()
        else:
            self.hit_test()

    def bounds(self):
        """Return coordinates of the sprite's bounding box."""
        half_width = self.sprite.width/2
        half_height = self.sprite.height/2

        bounds = [(-half_width, half_height),
                (half_width, half_height),
                (half_width, -half_height),
                (-half_width, -half_height)]
        radians = - math.radians(self.sprite.rotation)

        return map(lambda p: (self.sprite.x + p[0] * math.cos(radians) - p[1] *
            math.sin(radians), self.sprite.y + p[0] * math.sin(radians) + p[1] *
            math.cos(radians)), bounds)

    def draw_bounds(self):
        bounds = self.bounds()
        pyglet.graphics.draw(4, pyglet.gl.GL_QUADS,
                ('v2f', (
                    bounds[0][0], bounds[0][1],
                    bounds[1][0], bounds[1][1],
                    bounds[2][0], bounds[2][1],
                    bounds[3][0], bounds[3][1],
                )),
                ('c4B', (255,255,255,128)*4))

    def hit_test(self, other_bounds=None):
        if not self.hittable:
            return False

        object_bounds = self.bounds()
        if other_bounds is None:
            other_bounds = self.game.cursor.bounds()

        for bounds in (object_bounds, other_bounds):
            for i in range(len(bounds)):
                edge = (bounds[i][0] - bounds[i-1][0],
                        bounds[i][1] - bounds[i-1][1])
                object_min, object_max = projection(edge, object_bounds)
                other_min, other_max = projection(edge, other_bounds)

                if object_min < other_min:
                    if other_min > object_max:
                        return False
                else:
                    if object_min > other_max:
                        return False

        self.on_hit()

    def on_hit(self):
        self.remove()

    def remove(self, *args, **kwargs):
        try:
            self.game.state['things'].remove(self)
        except ValueError:
            pass

        self.sprite.delete()

class Pickle(Thing):
    image = pyglet.resource.image('pickle.png')

    def on_hit(self):
        self.game.state['score'] += 1
        self.hit_animation()
        if not self.game.state['score'] % self.game.state['jar_capacity']:
            self.game.state['lives'] = 3
            self.game.bg.score()

    def fade(self, dt):
        self.sprite.opacity -= 2000*dt
        if self.sprite.opacity <= 0:
            pyglet.clock.unschedule(self.fade)
            self.remove()

    def hit_animation(self):
        self.hittable = False
        self.moving = False
        pyglet.clock.schedule_interval(self.fade, 1.0/60)

class Knife(Thing):
    image = pyglet.resource.image('knife.png')

    def on_hit(self):
        self.game.state['lives'] -= 1
        self.remove()
        self.game.bg.hurt()
        if self.game.state['lives'] <= 0:
            self.game.change_mode('lose')

class Jar(Thing):
    image = pyglet.resource.image('jar_full.png')
    hittable = False

    def __init__(self, *args, **kwargs):
        super(Jar, self).__init__(*args, **kwargs)
        self.sprite.y += random.randrange(200)
        self.sprite.scale = 1
