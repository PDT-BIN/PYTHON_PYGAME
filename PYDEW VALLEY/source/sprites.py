from collections.abc import Iterable, Callable
from random import choice, randint

import pygame as pg
from settings import *


class Generic(pg.sprite.Sprite):

    def __init__(self, place: tuple[int, int], surface: pg.Surface,
                 groups: Iterable[pg.sprite.Group], layer_ordinal: int = LAYERS['main']):
        super().__init__(groups)
        # CORE.
        self.image = surface
        self.rect = surface.get_rect(topleft=place)
        self.hitbox = self.rect.inflate(
            -self.rect.width * 0.2, -self.rect.height * 0.75)
        self.z = layer_ordinal


class Particle(Generic):

    def __init__(self, place: tuple[int, int], surface: pg.Surface,
                 groups: Iterable[pg.sprite.Group], layer_orinal: int, duration: int = 200):
        super().__init__(place, surface, groups, layer_orinal)
        # CORE.
        self.start_time = pg.time.get_ticks()
        self.duration = duration
        # EFFECT.
        self.image = pg.mask.from_surface(surface).to_surface()
        self.image.set_colorkey('BLACK')

    def update(self, delta_time: float):
        if pg.time.get_ticks() - self.start_time >= self.duration:
            self.kill()


class Interaction(Generic):

    def __init__(self, place: tuple[int, int], surface: pg.Surface,
                 groups: Iterable[pg.sprite.Group], name: str):
        # CORE.
        super().__init__(place, surface, groups)
        self.name = name


class Water(Generic):

    def __init__(self, place: tuple[int, int], animations: list[pg.Surface],
                 groups: Iterable[pg.sprite.Group]):
        # ANIMATION.
        self.animations = animations
        self.frame_index = 0
        # CORE.
        super().__init__(
            place, self.animations[self.frame_index], groups, LAYERS['water'])

    def animate(self, delta_time: float):
        self.frame_index += 4 * delta_time

        if self.frame_index >= len(self.animations):
            self.frame_index = 0

        self.image = self.animations[int(self.frame_index)]

    def update(self, delta_time: float):
        self.animate(delta_time)


class WildFlower(Generic):

    def __init__(self, place: tuple[int, int], surface: pg.Surface,
                 groups: Iterable[pg.sprite.Group]):
        # CORE.
        super().__init__(place, surface, groups)
        self.hitbox = self.rect.inflate(-20, -self.rect.height * 0.9)


class Tree(Generic):

    def __init__(self, place: tuple[int, int], surface: pg.Surface,
                 groups: Iterable[pg.sprite.Group], name: str, add_item: Callable[[str], None]):
        super().__init__(place, surface, groups)
        # TREE.
        self.health, self.is_alive = 5, True
        self.surf_stump = pg.image.load(
            f'image/stumps/{name.lower()}.png').convert_alpha()
        # FRUIT.
        self.surf_apple = pg.image.load(
            'image/fruit/apple.png').convert_alpha()
        self.apple_pos = APPLE_POS[name]
        self.group_apple = pg.sprite.Group()
        self.spawn_apples()
        # INTERACTION.
        self.add_item = add_item
        # AUDIO.
        self.sound_axe = pg.mixer.Sound('audio/axe.mp3')

    def spawn_apples(self):
        for pos in self.apple_pos:
            if randint(0, 10) < 2:
                place = self.rect.left + pos[0], self.rect.top + pos[1]
                Generic(place, self.surf_apple, (self.group_apple,
                        self.groups()[0]), LAYERS['fruit'])

    def damage(self):
        if self.is_alive:
            self.sound_axe.play()
            self.health -= 1
            # PICK THE APPLE.
            if self.group_apple:
                apple = choice(self.group_apple.sprites())
                Particle(apple.rect.topleft, apple.image,
                         self.groups()[0], LAYERS['fruit'])
                apple.kill()
                self.add_item('apple')
            # CHECK DEATH.
            self.check_death()

    def check_death(self):
        if self.health <= 0:
            Particle(self.rect.topleft, self.image,
                     self.groups()[0], LAYERS['fruit'], 300)
            self.image = self.surf_stump
            self.rect = self.image.get_rect(midbottom=self.rect.midbottom)
            self.hitbox = self.rect.inflate(-10, self.rect.height * 0.6)
            self.is_alive = False
            self.add_item('wood')
