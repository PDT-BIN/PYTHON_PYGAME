from collections.abc import Iterable, Callable
from random import choice

import pygame as pg
from pytmx.util_pygame import load_pygame
from settings import *
from supports import *


class SoilTile(pg.sprite.Sprite):

    def __init__(self, place: tuple[int, int], surface: pg.Surface,
                 groups: Iterable[pg.sprite.Group]):
        super().__init__(groups)
        # CORE.
        self.image = surface
        self.rect = self.image.get_rect(topleft=place)
        self.z = LAYERS['soil']


class WaterTile(pg.sprite.Sprite):

    def __init__(self, place: tuple[int, int], surface: pg.Surface,
                 groups: Iterable[pg.sprite.Group]):
        super().__init__(groups)
        # CORE.
        self.image = surface
        self.rect = self.image.get_rect(topleft=place)
        self.z = LAYERS['soil water']


class Plant(pg.sprite.Sprite):

    def __init__(self, seed_type: str, soil: SoilTile, groups: Iterable[pg.sprite.Group],
                 check_watered: Callable[[tuple[int, int]], bool]):
        super().__init__(groups)
        # ANIMATIONS.
        self.seed_type = seed_type
        self.animations = load_image_list(f'image/fruit/{seed_type}')
        self.soil = soil
        # GROWTH.
        self.max_age = len(self.animations) - 1
        self.age, self.speed = 0, GROW_SPEED[seed_type]
        self.is_harvestable = False
        # CORE.
        self.image = self.animations[self.age]
        self.offset_y = pg.math.Vector2(0, -16 if seed_type == 'corn' else -8)
        self.rect = self.image.get_rect(
            midbottom=soil.rect.midbottom + self.offset_y)
        self.z = LAYERS['ground plant']
        # INTERACTION.
        self.check_watered = check_watered

    def grow(self):
        if self.check_watered(self.rect.center):
            self.age += self.speed
            # BECOME OBSTACLE.
            if self.age >= 1:
                self.z = LAYERS['main']
                self.hitbox = self.rect.inflate(-26, -self.rect.height * 0.4)
            # CHECK GROWTH.
            if self.age >= self.max_age:
                self.age = self.max_age
                self.is_harvestable = True
            # UPDATE.
            self.image = self.animations[int(self.age)]
            self.rect = self.image.get_rect(
                midbottom=self.soil.rect.midbottom + self.offset_y)


class SoilLayer:

    def __init__(self, group: pg.sprite.Group, group_obstacle: pg.sprite.Group):
        # CORE.
        self.all_sprites = group
        self.group_obstacle = group_obstacle
        # GROUP.
        self.group_soil = pg.sprite.Group()
        self.group_water = pg.sprite.Group()
        self.group_plant = pg.sprite.Group()
        # GRAPHICS.
        self.surf_soils = load_image_dictionary('image/soil')
        self.surf_waters = load_image_list('image/soil_water')
        # SETUP.
        self.load_grid()
        self.load_rects()
        # AUDIO.
        self.sound_hoe = pg.mixer.Sound('audio/hoe.wav')
        self.sound_hoe.set_volume(0.1)
        self.sound_plant = pg.mixer.Sound('audio/plant.wav')
        self.sound_plant.set_volume(0.2)

    def load_grid(self):
        ground = pg.image.load('image/world/ground.png')
        # CREATE GRID.
        self.grid = [[[] for _ in range(ground.get_width() // TILE_SIZE)]
                     for _ in range(ground.get_height() // TILE_SIZE)]
        # MARK THE FARMABLE CELL.
        for x, y, _ in load_pygame('data/map.tmx').get_layer_by_name('Farmable').tiles():
            self.grid[y][x].append('F')

    def load_rects(self):
        self.rects: list[pg.Rect] = []
        # CREATE HIT RECTS.
        for row_index, row in enumerate(self.grid):
            for col_index, col in enumerate(row):
                if 'F' in col:
                    x, y = col_index * TILE_SIZE, row_index * TILE_SIZE
                    self.rects.append(pg.Rect(x, y, TILE_SIZE, TILE_SIZE))

    def auto_formatting_tile(self, row_index: int, col_index: int):
        # INFORMATION.
        l = 'X' in self.grid[row_index][col_index - 1]
        r = 'X' in self.grid[row_index][col_index + 1]
        t = 'X' in self.grid[row_index - 1][col_index]
        b = 'X' in self.grid[row_index + 1][col_index]
        # AUTO FORMATTING.
        # ALL SIDES.
        if all((l, r, t, b)):
            return 'x'
        # HORIZONTAL SIDES.
        if l and not any((r, t, b)):
            return 'r'
        if r and not any((l, t, b)):
            return 'l'
        if all((l, r)) and not any((t, b)):
            return 'lr'
        # VERTICAL SIDES.
        if t and not any((l, r, b)):
            return 'b'
        if b and not any((l, r, t)):
            return 't'
        if all((t, b)) and not any((l, r)):
            return 'tb'
        # CORNERS.
        if all((l, b)) and not any((r, t)):
            return 'tr'
        if all((l, t)) and not any((r, b)):
            return 'br'
        if all((r, b)) and not any((l, t)):
            return 'tl'
        if all((r, t)) and not any((l, b)):
            return 'bl'
        # T-SHAPES.
        if all((l, r, b)) and not t:
            return 'lrt'
        if all((l, r, t)) and not b:
            return 'lrb'
        if all((l, t, b)) and not r:
            return 'tbl'
        if all((r, t, b)) and not l:
            return 'tbr'
        # DEFAULT.
        return 'o'

    def excavate(self, point: tuple[int, int]):
        for rect in self.rects:
            if rect.collidepoint(point):
                self.sound_hoe.play()
                area = self.grid[rect.y // TILE_SIZE][rect.x // TILE_SIZE]
                if 'F' in area and 'X' not in area:
                    area.append('X')
                    self.create_soil_tile()
                    break

    def create_soil_tile(self):
        # THIS LINE HELPS TO RENEW THE SOIL GROUP WHICH CHANGED BY AUTO TILE.
        self.group_soil.empty()
        # LOAD 'X'.
        for row_index, row in enumerate(self.grid):
            for col_index, col in enumerate(row):
                if 'X' in col:
                    tile_type = self.auto_formatting_tile(row_index, col_index)
                    # CREATE.
                    SoilTile((col_index * TILE_SIZE, row_index * TILE_SIZE), self.surf_soils[tile_type],
                             (self.all_sprites, self.group_soil))

    def irrigate(self, point: tuple[int, int]):
        for rect in self.rects:
            if rect.collidepoint(point):
                area = self.grid[rect.y // TILE_SIZE][rect.x // TILE_SIZE]
                if 'X' in area and 'W' not in area:
                    area.append('W')
                    WaterTile(rect.topleft, choice(self.surf_waters),
                              (self.all_sprites, self.group_water))
                    break

    def remove_water_tile(self):
        # REMOVE WATER TILES.
        for water in self.group_water.sprites():
            water.kill()
        # REMOVE 'W' OUT OF THE GRID.
        for row in self.grid:
            for col in row:
                if 'W' in col:
                    col.remove('W')

    def irrigate_by_rain(self):
        for row_index, row in enumerate(self.grid):
            for col_index, col in enumerate(row):
                if 'X' in col and 'W' not in col:
                    col.append('W')
                    WaterTile((col_index * TILE_SIZE, row_index * TILE_SIZE),
                              choice(self.surf_waters), (self.all_sprites, self.group_water))

    def check_watered(self, place: tuple[int, int]):
        return 'W' in self.grid[place[1] // TILE_SIZE][place[0] // TILE_SIZE]

    def plant_seed(self, point: tuple[int, int], seed_type: str):
        for soil in self.group_soil.sprites():
            if soil.rect.collidepoint(point):
                self.sound_plant.play()
                area = self.grid[soil.rect.y //
                                 TILE_SIZE][soil.rect.x // TILE_SIZE]
                if 'X' in area and 'P' not in area:
                    area.append('P')
                    Plant(seed_type, soil, (self.all_sprites, self.group_plant,
                          self.group_obstacle), self.check_watered)
                    break

    def update_plants(self):
        for plant in self.group_plant.sprites():
            plant.grow()
