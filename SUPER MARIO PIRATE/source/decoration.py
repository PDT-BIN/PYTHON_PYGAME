from random import choice, choices, randint

import pygame as pg
from settings import *
from support import load_image_folder
from tiles import AnimatingTile, StaticTile


class Sky:

    def __init__(self, style: str = 'LEVEL'):
        # CORE.
        self.screen = pg.display.get_surface()
        self.SKYLINE = 8
        self.images = load_image_folder('image/decoration/sky')
        self.style = style
        # STRETCH.
        self.images = [pg.transform.scale(
            image, (SCREEN_WIDTH, TILE_SIZE)) for image in self.images]
        # OVERWORLD SETUP.
        if style == 'OVERWORLD':
            # CLOUD.
            self.clouds: list[tuple(pg.Surface, pg.Rect)] = []
            cloud_images = load_image_folder('image/overworld/clouds')
            for cloud_image in choices(cloud_images, k=11):
                x = randint(0, SCREEN_WIDTH)
                y = randint(0, self.SKYLINE * TILE_SIZE)
                cloud_rect = cloud_image.get_rect(center=(x, y))
                self.clouds.append((cloud_image, cloud_rect))
            # PALM.
            self.palms: list[tuple(pg.Surface, pg.Rect)] = []
            palm_images = load_image_folder('image/overworld/palms')
            for palm_image in choices(palm_images, k=11):
                x = randint(0, SCREEN_WIDTH)
                y = self.SKYLINE * TILE_SIZE + randint(50, 75)
                palm_rect = palm_image.get_rect(midbottom=(x, y))
                self.palms.append((palm_image, palm_rect))

    def draw(self):
        for row in range(VERTICAL_TILE_NUMBER):
            index = 0 if row > self.SKYLINE else 1 if row == self.SKYLINE else 2
            self.screen.blit(self.images[index], (0, row * TILE_SIZE))
        # OVERWORLD SETUP.
        if self.style == 'OVERWORLD':
            self.screen.blits(self.clouds)
            self.screen.blits(self.palms)


class Water:

    def __init__(self, level_width: int):
        # CORE.
        self.screen = pg.display.get_surface()
        # GROUP.
        self.waters = pg.sprite.Group()
        # LOAD.
        WATER_LEVEL, TILE_WIDTH = SCREEN_HEIGHT - 20, 192
        for index in range((level_width + SCREEN_WIDTH) // TILE_WIDTH):
            place = index * TILE_WIDTH - SCREEN_WIDTH / 2, WATER_LEVEL
            self.waters.add(AnimatingTile(
                TILE_WIDTH, place, 'image/decoration/water'))

    def draw(self, x_shift: int):
        self.waters.update(x_shift)
        self.waters.draw(self.screen)


class Cloud:

    def __init__(self, level_width: int, quantity: int):
        # CORE.
        self.screen = pg.display.get_surface()
        self.images = load_image_folder('image/decoration/clouds')
        # GROUP.
        self.clouds = pg.sprite.Group()
        # LOAD.
        MIN_X, MAX_X = -SCREEN_WIDTH / 2, level_width + SCREEN_WIDTH / 2
        MIN_Y, MAX_Y = 0, 400
        for _ in range(quantity):
            place = randint(MIN_X, MAX_X), randint(MIN_Y, MAX_Y)
            self.clouds.add(StaticTile(0, place, choice(self.images)))

    def draw(self, x_shift: int):
        self.clouds.update(x_shift)
        self.clouds.draw(self.screen)
