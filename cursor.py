"""
Copyright 2012 Joe Friedl
See LICENSE for licensing details.
"""

import pyglet

class Cursor(object):
    def __init__(self, game):
        self.game = game

        self.batch = game.sprites
        self.group = game.cursor_group

        self.x = 0
        self.y = 90
        self.width = 70
        self.height = 20
        self.limits = (0, game.window.width - self.width)

        self.images = []
        jar_sheet = pyglet.resource.image('jar_cracks.png')
        for i in range(3):
            x = i * 100
            image = jar_sheet.get_region(x, 0, 90, 135)
            image.anchor_x = 10
            image.anchor_y = image.height
            self.images.append(image)

        self.jar_group = pyglet.graphics.OrderedGroup(1, parent=self.group)
        self.sprite = pyglet.sprite.Sprite(self.images[0], batch=game.sprites,
                group=self.jar_group)
        self.sprite.x = self.x
        self.sprite.y = self.y

        self.pickle_images = []
        self.pickle_sheet = pyglet.resource.image('jar_pickles.png')
        for i in range(11):
            x = i * 100
            image = self.pickle_sheet.get_region(x, 0, 90, 135)
            image.anchor_x = 10
            image.anchor_y = image.height
            self.pickle_images.append(image)

        self.pickle_group = pyglet.graphics.OrderedGroup(0, parent=self.group)
        self.pickle_sprite = pyglet.sprite.Sprite(self.pickle_images[0],
                batch=game.sprites, group=self.pickle_group)
        self.pickle_sprite.x = self.x
        self.pickle_sprite.y = self.y

    def set_position(self, dx):
        x = self.x + dx
        x = max(self.limits[0], x)
        x = min(self.limits[1], x)
        self.x = x
        self.sprite.x = x
        self.pickle_sprite.x = x

    def bounds(self):
        return ((self.x, self.y), (self.x + self.width, self.y), (self.x +
                self.width, self.y - self.height), (self.x, self.y -
                    self.height))

    def update(self, dt):
        image = self.pickle_images[self.game.state['score'] % 10]
        if self.pickle_sprite.image != image:
            self.pickle_sprite.image = image
        if self.game.state['lives'] > 0:
            image = self.images[3 - self.game.state['lives']]
            if self.sprite.image != image:
                self.sprite.image = image

    def draw(self):
        self.batch.draw()
