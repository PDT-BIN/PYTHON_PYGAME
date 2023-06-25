import pygame as pg
from pygame import Surface
from pygame.math import Vector2 as Vector
from pygame.mouse import get_pos as mouse_pos
from pygame.sprite import AbstractGroup
from settings import *


class CanvasTile:
    def __init__(self, tile_id: int, offset: Vector = Vector()):
        # EMPTY STATE.
        self.is_empty = False
        # CONTROL TERRAIN.
        self.has_terrain = False
        self.terrain_neighbors = []
        # CONTROL WATER.
        self.has_water = False
        self.water_on_top = False
        # CONTROL COIN.
        self.coin = None
        # CONTROL ENEMY.
        self.enemy = None
        # CONTROL OBJECTS.
        self.objects: list[tuple[int, Vector]] = []
        # START-UP.
        self.add_id(tile_id, offset)

    def add_id(self, tile_id: int, offset: Vector = Vector()):
        match EDITOR_DATA[tile_id]['style']:
            case 'terrain':
                self.has_terrain = True
            case 'water':
                self.has_water = True
            case 'coin':
                self.coin = tile_id
            case 'enemy':
                self.enemy = tile_id
            case _:
                if (tile_id, offset) not in self.objects:
                    self.objects.append((tile_id, offset))

    def del_id(self, tile_id: int):
        match EDITOR_DATA[tile_id]['style']:
            case 'terrain':
                self.has_terrain = False
            case 'water':
                self.has_water = False
            case 'coin':
                self.coin = None
            case 'enemy':
                self.enemy = None
        # CHECK EMPTY STATE.
        self.check_empty()

    def check_empty(self):
        if not self.has_terrain and not self.has_water and not self.coin and not self.enemy:
            self.is_empty = True

    def get_water_type(self) -> str:
        return 'bottom' if self.water_on_top else 'top'

    def get_terrain_type(self, land_tiles: list[str]) -> str:
        return name if (name := ''.join(self.terrain_neighbors)) in land_tiles else 'X'


class CanvasObject(pg.sprite.Sprite):
    def __init__(self, groups: AbstractGroup, tile_id: int, frames: list[Surface],
                 origin_point: Vector, position: tuple[int, int]):
        super().__init__(groups)
        # RESOURCES.
        self.frames, self.frame_index = frames, 0
        # ORIGINAL.
        self.tile_id = tile_id
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=position)
        # PAN MOVEMENT.
        self.distance_to_origin = Vector(self.rect.topleft) - origin_point
        # DRAG MOVEMENT.
        self.is_selected = False
        self.mouse_offset = Vector()

    def pan(self, origin_point: Vector):
        # TOPLEFT BASES ON ORIGIN POINT.
        self.rect.topleft = origin_point + self.distance_to_origin

    def start_drag(self):
        self.is_selected = True
        self.mouse_offset = Vector(mouse_pos()) - Vector(self.rect.topleft)

    def drag(self):
        if self.is_selected:
            self.rect.topleft = Vector(mouse_pos()) - self.mouse_offset

    def end_drag(self, origin_point: Vector):
        self.is_selected = False
        # CALCULATE NEW DISTANCE TO ORIGIN.
        self.distance_to_origin = Vector(self.rect.topleft) - origin_point

    def animate(self, delta_time: float):
        self.frame_index += ANIMATION_SPEED * delta_time
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]
        self.rect = self.image.get_rect(midbottom=self.rect.midbottom)

    def update(self, delta_time: float):
        self.animate(delta_time)
        self.drag()
