from collections.abc import Iterable
from random import choice, randint

import pygame as pg
from settings import *
from sprites import Generic
from supports import load_image_list


class Drop(Generic):

    def __init__(self, place: tuple[int, int], surface: pg.Surface,
                 groups: Iterable[pg.sprite.Group], layer_ordinal: int, can_move: bool):
        # CORE.
        super().__init__(place, surface, groups, layer_ordinal)
        # TIMER.
        self.start_time = pg.time.get_ticks()
        self.lifetime = randint(400, 500)
        # MOVEMENT.
        self.can_move = can_move
        if can_move:
            self.pos = pg.math.Vector2(self.rect.topleft)
            self.direction = pg.math.Vector2(-2, 4)
            self.speed = randint(200, 250)

    def update(self, delta_time: float):
        # MOVEMENT.
        if self.can_move:
            self.pos += self.direction * self.speed * delta_time
            self.rect.topleft = round(self.pos.x), round(self.pos.y)
        # TIMER.
        if pg.time.get_ticks() - self.start_time >= self.lifetime:
            self.kill()


class Rain:

    def __init__(self, all_sprites: pg.sprite.Group):
        # CORE.
        self.all_sprites = all_sprites
        # GRAPHICS.
        self.surf_rains_drops = load_image_list('image/rain/drops')
        self.surf_rains_floor = load_image_list('image/rain/floor')
        # SIZE OF MAP.
        self.map_size = pg.image.load('image/world/ground.png').get_size()

    def create_rain_floor(self):
        place = randint(0, self.map_size[0]), randint(0, self.map_size[1])
        surface = choice(self.surf_rains_floor)
        Drop(place, surface, self.all_sprites, LAYERS['rain floor'], False)

    def create_rain_drops(self):
        place = randint(0, self.map_size[0]), randint(0, self.map_size[1])
        surface = choice(self.surf_rains_drops)
        Drop(place, surface, self.all_sprites, LAYERS['rain drops'], True)

    def update(self):
        self.create_rain_drops()
        self.create_rain_floor()


class Sky:

    def __init__(self):
        # CORE.
        self.screen = pg.display.get_surface()
        self.image = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.color_day = [255, 255, 255]
        self.color_night = (38, 101, 189)

    def display(self, delta_time: float):
        for index, value in enumerate(self.color_night):
            if self.color_day[index] > value:
                self.color_day[index] -= 2 * delta_time
        # DRAW.
        self.image.fill(self.color_day)
        self.screen.blit(self.image, (0, 0), special_flags=pg.BLEND_RGBA_MULT)
