import pygame as pg
from player import Player
from settings import *
from tile import Tile


class YSortCameraGroup(pg.sprite.Group):

    def __init__(self):
        super().__init__()
        # CORE.
        self.display = pg.display.get_surface()
        self.offset = pg.math.Vector2()

    def draws(self, player: Player):
        self.offset.update(player.rect.centerx - WIDTH / 2,
                           player.rect.centery - HEIGTH / 2)
        for sprite in sorted(self.sprites(), key=lambda e: e.rect.centery):
            offset_place = sprite.rect.topleft - self.offset
            self.display.blit(sprite.image, offset_place)


class Level:

    def __init__(self):
        # CORE.
        self.display = pg.display.get_surface()
        # GROUP SETUP.
        self.group_visible = YSortCameraGroup()
        self.group_obstacle = pg.sprite.Group()
        # LOAD DATA.
        self.load_map()

    def load_map(self):
        for row_idx, row in enumerate(WORLD_MAP):
            for col_idx, col in enumerate(row):
                place = col_idx * TILESIZE, row_idx * TILESIZE
                match col:
                    case 'X':
                        Tile(place, (self.group_visible, self.group_obstacle))
                    case 'P':
                        self.player = Player(
                            place, (self.group_visible), self.group_obstacle)

    def run(self):
        self.group_visible.update()
        self.group_visible.draws(self.player)
