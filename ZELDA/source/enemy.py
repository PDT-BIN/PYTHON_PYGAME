from collections.abc import Callable

import pygame as pg
from entity import Entity
from player import Player
from settings import *
from support import load_image_folder


class Enemy(Entity):

    def __init__(self, name: str, place: tuple[int, int], groups: tuple[pg.sprite.Group],
                 group_obstacle: pg.sprite.GroupSingle, damage_player: Callable[[int, str], None],
                 trigger_death_particle: Callable[[tuple[int, int], str], None], add_exp: Callable[[int], None]):
        super().__init__(groups, group_obstacle)
        # ANIMATION.
        self.load_asset(name)
        self.status = 'idle'
        # CORE.
        self.form = 'Enemy'
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(topleft=place)
        self.hitbox = self.rect.inflate(0, -10)
        # ATTACK.
        self.can_attack, self.ATTACK_COOLDOWN = True, 500
        self.attack_time = None
        self.damage_player = damage_player
        self.trigger_death_particle = trigger_death_particle
        self.add_exp = add_exp
        # VULNERABLE TIMER.
        self.is_vulnerable, self.VULNERABLE_COOLDOWN = True, 300
        self.hurt_time = None
        # STATS.
        stats = MONSTER_DATA[name]
        self.name = name
        self.health = stats['Health']
        self.exp = stats['Exp']
        self.speed = stats['Speed']
        self.attack_damage = stats['Damage']
        self.attack_type = stats['Attack_type']
        self.resistance = stats['Resistance']
        self.attack_radius = stats['Attack_radius']
        self.notice_radius = stats['Notice_radius']
        # AUDIO.
        self.sound_hurt = pg.mixer.Sound('audio/hurt.wav')
        self.sound_death = pg.mixer.Sound('audio/death.wav')
        self.sound_attack = pg.mixer.Sound(stats['Attack_sound'])
        self.sound_hurt.set_volume(0.6)
        self.sound_death.set_volume(0.6)
        self.sound_attack.set_volume(0.3)

    def load_asset(self, name: str):
        self.animations: list[pg.Surface] = {
            'idle': None, 'move': None, 'attack': None}

        for status in self.animations.keys():
            self.animations[status] = load_image_folder(
                f'image/monsters/{name}/{status}')

    def get_range(self, player: Player):
        place_player = pg.math.Vector2(player.rect.center)
        place_enemy = pg.math.Vector2(self.rect.center)

        distance = (place_player - place_enemy).magnitude()
        if distance > 0:
            direction = (place_player - place_enemy).normalize()
        else:
            direction = pg.math.Vector2()

        return distance, direction

    def get_status(self, player: Player):
        distance = self.get_range(player)[0]

        if distance <= self.attack_radius and self.can_attack:
            if self.status != 'attack':
                self.frame_index = 0
            self.status = 'attack'
        elif distance <= self.notice_radius:
            self.status = 'move'
        else:
            self.status = 'idle'

    def act(self, player: Player):
        if self.status == 'attack':
            self.damage_player(self.attack_damage, self.attack_type)
            self.sound_attack.play()
        elif self.status == 'move':
            self.direction = self.get_range(player)[1]
        else:
            self.direction = pg.math.Vector2()

    def animate(self):
        animation = self.animations[self.status]

        # LOOP OVER.
        self.frame_index += self.ANIMATION_SPEED
        if self.frame_index >= len(animation):
            self.frame_index = 0
            if self.can_attack:
                self.can_attack = False
                self.attack_time = pg.time.get_ticks()

        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center=self.hitbox.center)

        if not self.is_vulnerable:
            self.image.set_alpha(self.get_alpha_value())
        else:
            self.image.set_alpha(255)

    def cooldown(self):
        current_time = pg.time.get_ticks()

        if not self.can_attack:
            if current_time - self.attack_time > self.ATTACK_COOLDOWN:
                self.can_attack = True

        if not self.is_vulnerable:
            if current_time - self.hurt_time > self.VULNERABLE_COOLDOWN:
                self.is_vulnerable = True

    def get_damage(self, player: Player, form: str):
        if self.is_vulnerable:
            self.direction = self.get_range(player)[1]
            # PHYSICAL.
            if form == 'weapon':
                self.health -= player.get_full_weapon_damage()
            else:
                self.health -= player.get_full_magic_damage()
            self.is_vulnerable = False
            self.hurt_time = pg.time.get_ticks()

            self.sound_hurt.play()

    def check_death(self):
        if self.health <= 0:
            self.kill()
            self.add_exp(self.exp)

            # PARTICLE EFFECT.
            self.trigger_death_particle(self.rect.center, self.name)

            self.sound_death.play()

    def hit_reaction(self):
        if not self.is_vulnerable:
            self.direction *= -self.resistance

    def update(self):
        self.hit_reaction()
        self.move(self.speed)
        self.animate()
        self.cooldown()
        self.check_death()

    def update_enemy(self, player: Player):
        self.get_status(player)
        self.act(player)
