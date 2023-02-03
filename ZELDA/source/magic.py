from random import randint

import pygame as pg
from particle import AnimationController
from player import Player
from settings import TILESIZE


class MagicController:

    def __init__(self, animation_controller: AnimationController):
        # CORE.
        self.animation_controller = animation_controller
        self.sounds = {
            'Heal': pg.mixer.Sound('audio/heal.wav'),
            'Flame': pg.mixer.Sound('audio/flame.wav')
        }

    def heal(self, player: Player, strength: int, cost: int, groups: tuple[pg.sprite.Group]):
        if player.energy >= cost:
            player.health += strength
            player.energy -= cost

            if player.health > player.stats['Health']:
                player.health = player.stats['Health']

            # PARTICLE EFFECT.
            self.animation_controller.create_particles(
                player.rect.center, 'aura', groups)
            self.animation_controller.create_particles(
                player.rect.center, 'heal', groups)

            self.sounds['Heal'].play()

    def flame(self, player: Player, cost: int, groups: tuple[pg.sprite.Group]):
        if player.energy >= cost:
            player.energy -= cost

            # PARTICLE EFFECT.
            match player.status.split('_')[0]:
                case 'left':
                    direction = pg.math.Vector2(-1, 0)
                case 'right':
                    direction = pg.math.Vector2(1, 0)
                case 'up':
                    direction = pg.math.Vector2(0, -1)
                case 'down':
                    direction = pg.math.Vector2(0, 1)

            for index in range(1, 6):
                place = player.rect.center + direction * (index * TILESIZE)
                place += (randint(-TILESIZE // 3, TILESIZE // 3),
                          randint(-TILESIZE // 3, TILESIZE // 3))
                self.animation_controller.create_particles(
                    place, 'flame', groups)

            self.sounds['Flame'].play()
