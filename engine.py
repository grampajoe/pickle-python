"""
Copyright 2012 Joe Friedl
See LICENSE for licensing details.
"""

import pyglet
from things import pick_thing, Jar
from background import Background
from cursor import Cursor
import random

class Engine(object):
    state = {'jar_capacity': 10}

    def __init__(self, window):
        self.window = window

        self.sprites = pyglet.graphics.Batch()
        self.full_jars = pyglet.graphics.Batch()
        self.background_group = pyglet.graphics.OrderedGroup(0)
        self.things_group = pyglet.graphics.OrderedGroup(1)
        self.cursor_group = pyglet.graphics.OrderedGroup(2)
        self.interface_group = pyglet.graphics.OrderedGroup(3)

        self.score_sprite = pyglet.sprite.Sprite(pyglet.resource.image(
                'jar_full.png'), batch=self.sprites, group=self.interface_group)
        self.score_sprite.x = 20
        self.score_sprite.y = window.height - 20 - self.score_sprite.height

        pyglet.resource.add_font('FredokaOne-Regular.ttf')
        fredoka_one = pyglet.font.load('Fredoka One')

        self.score_label = pyglet.text.Label('0', x=80,
                y=self.score_sprite.y + self.score_sprite.height/2,
                anchor_y='center', font_name='Fredoka One', font_size=16,
                batch=self.sprites, group=self.interface_group)

        self.final_score_label = pyglet.text.Label('0', x=window.width/2,
                y=window.height/2, anchor_x='center', anchor_y='center',
                font_size=32)

        heart_image = pyglet.resource.image('heart.png')
        self.hearts = []
        for i in range(3):
            x = i * 35 + 20
            sprite = pyglet.sprite.Sprite(heart_image, batch=self.sprites,
                    group=self.interface_group)
            sprite.x = x
            sprite.y = 20
            self.hearts.append(sprite)

        self.start_label = pyglet.text.Label('Click to Start', x=window.width/2,
                y=window.height/2 - 40, anchor_x='center', anchor_y='top',
                font_name='Fredoka One', font_size=20)

        self.title = pyglet.resource.image('title.png')
        self.title.anchor_x = self.title.width/2

        splat_image = pyglet.resource.image('splat.png')
        self.splat = pyglet.sprite.Sprite(splat_image)

        self.bg = Background(self)
        self.cursor = Cursor(self)

        @window.event
        def on_draw():
            self.window.clear()
            if self.state['mode'] == 'title':
                self.bg.draw()
                self.start_label.draw()
                self.title.blit(window.width/2, window.height/2)
            elif self.state['mode'] == 'game':
                self.bg.draw()
                self.sprites.draw()
            elif self.state['mode'] == 'lose':
                self.bg.draw()
                self.full_jars.draw()
                self.final_score_label.draw()
                if self.splat.opacity:
                    self.splat.draw()

        @window.event
        def on_mouse_press(x, y, button, modifiers):
            if self.state['mode'] == 'lose':
                self.change_mode('title')
            elif self.state['mode'] == 'title':
                self.change_mode('game')

        @window.event
        def on_mouse_motion(x, y, dx, dy):
            if self.state['mode'] == 'game':
                self.cursor.set_position(dx)

        @window.event
        def on_key_press(symbol, modifiers):
            if symbol == pyglet.window.key.P:
                self.toggle_pause()

        self.change_mode('title')

    def init_game(self):
        pyglet.clock.unschedule(self.update)
        pyglet.clock.unschedule(self.speed_up)
        self.state['things'] = []
        self.state['explode'] = []
        self.state['score'] = 0
        self.state['lives'] = 3
        self.state['add_thing_interval'] = 1.0
        self.state['pickle_probability'] = 1
        self.cursor.set_position(self.window.width/2)
        self.add_thing()
        pyglet.clock.schedule_interval(self.update, 1/60.0)
        pyglet.clock.schedule_interval(self.speed_up, 10)

    def change_mode(self, mode):
        self.state['mode'] = mode
        if mode == 'title':
            self.window.set_mouse_visible(True)
            self.window.set_exclusive_mouse(False)
        elif mode == 'game':
            self.window.set_mouse_visible(False)
            self.window.set_exclusive_mouse(True)
            self.init_game()
        elif mode == 'lose':
            pyglet.clock.unschedule(self.add_thing)
            self.bg.mode = 'normal'
            self.splat.y = 0
            self.splat.opacity = 255
            self.final_score_label.text = 'You filled {0} jar{1}!'.format(
                    self.state['score']/10, 's' if self.state['score']/10 > 1
                    else '')
            self.window.set_mouse_visible(True)
            self.window.set_exclusive_mouse(False)
            self.state['things'] = [Jar(self, batch=self.full_jars) for i in
                    range(self.state['score']/10)]

    def toggle_pause(self):
        self.state['paused'] = True

    def add_thing(self, dt=None):
        self.state['things'].append(pick_thing(self))
        pyglet.clock.schedule_once(self.add_thing,
                random.random() * self.state['add_thing_interval'] * 1.5 +
                self.state['add_thing_interval'])

    def speed_up(self, dt):
        self.state['add_thing_interval'] *= 0.95
        self.state['pickle_probability'] = max(self.state['pickle_probability']
                * 0.9, 0.2)

    def update(self, dt):
        if self.state['mode'] == 'game':
            for thing in self.state['things']:
                thing.update(dt)
            for i in range(len(self.hearts)):
                if self.state['lives'] > i:
                    self.hearts[i].opacity = 255
                else:
                    self.hearts[i].opacity = 0
            self.bg.update(dt)
            self.cursor.update(dt)
            self.score_label.text = str(self.state['score']/10)
        elif self.state['mode'] == 'lose':
            for thing in self.state['things']:
                thing.update(dt)
            if self.splat.opacity > 0:
                self.splat.y -= 100 * dt
                self.splat.opacity = max(0, self.splat.opacity - 255 * dt)
