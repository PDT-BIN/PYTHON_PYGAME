import pygame as pg
from player import Player


class Weapon(pg.sprite.Sprite):

    def __init__(self, player: Player, groups: tuple[pg.sprite.Group]):
        super().__init__(groups)
        self.form = 'weapon'
        # INFORMATION.
        direction = player.status.split('_')[0]

        # GRAPHIC.
        path = f'image/weapons/{player.weapon}/{direction}.png'
        self.image = pg.image.load(path).convert_alpha()

        # PLACE.
        match direction:
            case 'left':
                self.rect = self.image.get_rect(
                    midright=player.rect.midleft + pg.math.Vector2(0, 16))
            case 'right':
                self.rect = self.image.get_rect(
                    midleft=player.rect.midright + pg.math.Vector2(0, 16))
            case 'up':
                self.rect = self.image.get_rect(
                    midbottom=player.rect.midtop + pg.math.Vector2(-10, 0))
            case 'down':
                self.rect = self.image.get_rect(
                    midtop=player.rect.midbottom + pg.math.Vector2(-10, 0))
