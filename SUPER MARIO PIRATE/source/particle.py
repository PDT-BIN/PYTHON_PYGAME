import pygame as pg
from support import load_image_folder


class ParticleEffect(pg.sprite.Sprite):

    def __init__(self, place: tuple[int, int], form: str):
        super().__init__()
        # ANIMATION.
        self.load_asset(form)
        self.frame_index, self.ANIMATION_SPEED = 0, 0.5
        # CORE.
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect(center=place)

    def animate(self):
        self.frame_index += self.ANIMATION_SPEED
        if self.frame_index >= len(self.images):
            self.kill()
        else:
            self.image = self.images[int(self.frame_index)]

    def load_asset(self, form: str):
        if form == 'jump':
            path = 'image/dust_particles/jump'
        elif form == 'land':
            path = 'image/dust_particles/land'
        else:
            path = 'image/enemy/explosion'
        self.images = load_image_folder(path)

    def update(self, x_shift: int):
        self.rect.x += x_shift
        self.animate()
