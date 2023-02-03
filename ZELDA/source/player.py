from collections.abc import Callable

import pygame as pg
from entity import Entity
from settings import *
from support import load_image_folder


class Player(Entity):

    def __init__(self, place: tuple[int, int], groups: tuple[pg.sprite.Group], group_obstacle: pg.sprite.Group,
                 create_attack: Callable[[], None], destroy_attack: Callable[[], None],
                 create_magic):
        super().__init__(groups, group_obstacle)
        # ASSET.
        self.load_asset()
        self.status = 'down'
        # CORE.
        self.image = pg.image.load('image/test/player.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=place)
        self.hitbox = self.rect.inflate(-6, HITBOX_OFFSET['Player'])
        # ATTACK.
        self.is_attacking, self.ATTACK_COOLDOWN = False, 400
        self.attack_time = None
        # WEAPON.
        self.create_attack = create_attack
        self.destroy_attack = destroy_attack
        self.weapon_index = 0
        self.weapon = tuple(WEAPON_DATA.keys())[self.weapon_index]
        self.can_switch_weapon, self.SWITCH_COOLDOWN = True, 200
        self.switch_weapon_time = None
        # MAGIC.
        self.create_magic = create_magic
        self.magic_index = 0
        self.magic = tuple(MAGIC_DATA.keys())[self.magic_index]
        self.can_switch_magic = True
        self.switch_magic_time = None
        # STATS.
        self.stats = {'Health': 100, 'Energy': 100,
                      'Attack': 10, 'Magic': 4, 'Speed': 5}
        self.MAX_STATS = {'Health': 300, 'Energy': 140,
                          'Attack': 20, 'Magic': 10, 'Speed': 10}
        self.upgrade_cost = {'Health': 100, 'Energy': 100,
                             'Attack': 100, 'Magic': 100, 'Speed': 100}
        self.health, self.energy = self.stats['Health'], self.stats['Energy']
        self.exp = 0
        # VULNERABLE TIMER.
        self.is_vulnerable, self.VULNERABLE_COOLDOWN = True, 500
        self.hurt_time = None
        # AUDIO.
        self.sound_attack = pg.mixer.Sound('audio/sword.wav')
        self.sound_attack.set_volume(0.5)

    def load_asset(self):
        self.animations: dict[str, list[pg.Surface]] = {
            'left': None, 'right': None, 'up': None, 'down': None,
            'left_idle': None, 'right_idle': None, 'up_idle': None, 'down_idle': None,
            'left_attack': None, 'right_attack': None, 'up_attack': None, 'down_attack': None
        }

        for status in self.animations.keys():
            self.animations[status] = load_image_folder(
                f'image/player/{status}')

    def input(self):
        keys = pg.key.get_pressed()

        # MOVEMENT INPUT.
        if not self.is_attacking:
            if keys[pg.K_LEFT]:
                self.direction.x = -1
                self.status = 'left'
            elif keys[pg.K_RIGHT]:
                self.direction.x = 1
                self.status = 'right'
            else:
                self.direction.x = 0

            if keys[pg.K_UP]:
                self.direction.y = -1
                self.status = 'up'
            elif keys[pg.K_DOWN]:
                self.direction.y = 1
                self.status = 'down'
            else:
                self.direction.y = 0

            # ATTACK INPUT.
            if keys[pg.K_SPACE]:
                self.is_attacking = True
                self.attack_time = pg.time.get_ticks()
                self.create_attack()
                self.sound_attack.play()

            if keys[pg.K_LCTRL]:
                self.is_attacking = True
                self.attack_time = pg.time.get_ticks()
                form = tuple(MAGIC_DATA.keys())[self.magic_index]
                strength = tuple(MAGIC_DATA.values())[
                    self.magic_index]['Strength'] + self.stats['Magic']
                cost = tuple(MAGIC_DATA.values())[self.magic_index]['Cost']
                self.create_magic(form, strength, cost)

            # SWITCH INPUT.
            if keys[pg.K_q] and self.can_switch_weapon:
                self.can_switch_weapon = False
                self.switch_weapon_time = pg.time.get_ticks()
                self.weapon_index += 1
                if self.weapon_index > len(WEAPON_DATA) - 1:
                    self.weapon_index = 0
                self.weapon = tuple(WEAPON_DATA.keys())[self.weapon_index]

            if keys[pg.K_e] and self.can_switch_magic:
                self.can_switch_magic = False
                self.switch_magic_time = pg.time.get_ticks()
                self.magic_index += 1
                if self.magic_index > len(MAGIC_DATA) - 1:
                    self.magic_index = 0
                self.magic = tuple(MAGIC_DATA.keys())[self.magic_index]

    def get_status(self):
        # IDLE.
        if self.direction == (0, 0):
            self.status = self.status.split('_')[0] + '_idle'

        # ATTACK.
        if self.is_attacking:
            self.direction.update()
            self.status = self.status.split('_')[0] + '_attack'
        else:
            if '_attack' in self.status:
                self.status = self.status.split('_')[0]

    def animate(self):
        animation = self.animations[self.status]

        # LOOP OVER.
        self.frame_index += self.ANIMATION_SPEED
        if self.frame_index >= len(animation):
            self.frame_index = 0

        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center=self.hitbox.center)

        if not self.is_vulnerable:
            self.image.set_alpha(self.get_alpha_value())
        else:
            self.image.set_alpha(255)

    def cooldown(self):
        current_time = pg.time.get_ticks()
        if self.is_attacking:
            if current_time - self.attack_time > self.ATTACK_COOLDOWN + WEAPON_DATA[self.weapon]['Cooldown']:
                self.is_attacking = False
                self.destroy_attack()

        if not self.can_switch_weapon:
            if current_time - self.switch_weapon_time > self.SWITCH_COOLDOWN:
                self.can_switch_weapon = True

        if not self.can_switch_magic:
            if current_time - self.switch_magic_time > self.SWITCH_COOLDOWN:
                self.can_switch_magic = True

        if not self.is_vulnerable:
            if current_time - self.hurt_time > self.VULNERABLE_COOLDOWN:
                self.is_vulnerable = True

    def get_full_weapon_damage(self):
        base_damage = self.stats['Attack']
        weapon_damage = WEAPON_DATA[self.weapon]['Damage']

        return base_damage + weapon_damage

    def get_full_magic_damage(self):
        base_damage = self.stats['Magic']
        magic_damage = MAGIC_DATA[self.magic]['Strength']

        return base_damage + magic_damage

    def energy_recovery(self):
        if self.energy < self.stats['Energy']:
            self.energy += 0.01 * self.stats['Magic']
        else:
            self.energy = self.stats['Energy']

    def get_value_by_index(self, index: int):
        return tuple(self.stats.values())[index]

    def get_cost_by_index(self, index: int):
        return tuple(self.upgrade_cost.values())[index]

    def update(self):
        self.input()
        self.get_status()
        self.animate()
        self.move(self.stats['Speed'])
        self.cooldown()
        self.energy_recovery()
