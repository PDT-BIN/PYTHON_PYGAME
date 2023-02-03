from random import choice

import pygame as pg
from support import load_image_folder


class AnimationController:
    def __init__(self):
        self.animations = {
            # MAGIC.
            'flame': load_image_folder('image/particles/flame/frames'),
            'aura': load_image_folder('image/particles/aura'),
            'heal': load_image_folder('image/particles/heal/frames'),

            # ATTACK.
            'claw': load_image_folder('image/particles/claw'),
            'slash': load_image_folder('image/particles/slash'),
            'sparkle': load_image_folder('image/particles/sparkle'),
            'leaf_attack': load_image_folder('image/particles/leaf_attack'),
            'thunder': load_image_folder('image/particles/thunder'),

            # MONSTER DEATH.
            'squid': load_image_folder('image/particles/smoke_orange'),
            'raccoon': load_image_folder('image/particles/raccoon'),
            'spirit': load_image_folder('image/particles/nova'),
            'bamboo': load_image_folder('image/particles/bamboo'),

            # LEAFS.
            'leaf': (
                load_image_folder('image/particles/leaf1'),
                load_image_folder('image/particles/leaf2'),
                load_image_folder('image/particles/leaf3'),
                load_image_folder('image/particles/leaf4'),
                load_image_folder('image/particles/leaf5'),
                load_image_folder('image/particles/leaf6'),
                self.reflect_images(
                    load_image_folder('image/particles/leaf1')),
                self.reflect_images(
                    load_image_folder('image/particles/leaf2')),
                self.reflect_images(
                    load_image_folder('image/particles/leaf3')),
                self.reflect_images(
                    load_image_folder('image/particles/leaf4')),
                self.reflect_images(
                    load_image_folder('image/particles/leaf5')),
                self.reflect_images(
                    load_image_folder('image/particles/leaf6'))
            )
        }

    def reflect_images(self, images: list[pg.Surface]):
        return [pg.transform.flip(image, True, False) for image in images]

    def create_grass_particle(self, place: tuple[int, int], groups: tuple[pg.sprite.Group]):
        ParticleEffect(place, choice(self.animations['leaf']), groups)

    def create_particles(self, place: tuple[int, int], form: str, groups: tuple[pg.sprite.Group]):
        ParticleEffect(place, self.animations[form], groups)


class ParticleEffect(pg.sprite.Sprite):

    def __init__(self, place: tuple[int, int], images: list[pg.Surface], groups: tuple[pg.sprite.Group]):
        super().__init__(groups)
        # ANIMATION.
        self.animations = images
        self.frame_index, self.ANIMATION_SPEED = 0, 0.15
        # CORE.
        self.image = self.animations[self.frame_index]
        self.rect = self.image.get_rect(center=place)
        self.form = 'magic'

    def animate(self):
        self.frame_index += self.ANIMATION_SPEED

        if self.frame_index >= len(self.animations):
            self.kill()
        else:
            self.image = self.animations[int(self.frame_index)]

    def update(self):
        self.animate()
