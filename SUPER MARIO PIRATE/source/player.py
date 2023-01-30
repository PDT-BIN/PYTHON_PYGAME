from collections.abc import Callable
from math import sin

import pygame as pg
from support import load_image_folder


class Player(pg.sprite.Sprite):

    def __init__(self, place, particle_method: Callable[[], None], update_health: Callable[[int], None]):
        super().__init__()
        # ANIMATION.
        self.animations = {folder: load_image_folder(f'image/character/{folder}')
                           for folder in ('idle', 'run', 'jump', 'fall')}
        self.status = 'idle'
        self.frame_index, self.ANIMATION_SPEEP = 0, 0.15
        # CORE.
        self.screen = pg.display.get_surface()
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(topleft=place)
        self.hitbox = pg.Rect(self.rect.topleft, (50, self.rect.height))
        # MOVEMENT.
        self.direction, self.MOVE_SPEED = pg.math.Vector2(), 8
        self.GRAVITY, self.JUMP_SPEED = 0.8, -16
        # STATUS.
        self.facing_right = True
        self.on_ground = False
        # RUN PARTICLE ANIMATION.
        self.dust_animations = load_image_folder(
            'image/dust_particles/run')
        self.dust_frame_index, self.DUST_ANIMATION_SPEEP = 0, 0.15
        # JUMP PARTICLE METHOD.
        self.load_jump_particle = particle_method
        # UPDATE HEALTH METHOD.
        self.update_health = update_health
        # HEALTH MANAGEMENT.
        self.invincible, self.hurt_time = False, None
        self.INVINCIBLE_DURATION = 500
        # SOUND EFFECT.
        self.sound_jump = pg.mixer.Sound('audio/effects/jump.wav')
        self.sound_jump.set_volume(0.5)
        self.sound_hit = pg.mixer.Sound('audio/effects/hit.wav')

    def input(self):
        # INFORMATION.
        keys = pg.key.get_pressed()
        # MOVE.
        if keys[pg.K_LEFT]:
            self.direction.x = -1
            self.facing_right = False
        elif keys[pg.K_RIGHT]:
            self.direction.x = 1
            self.facing_right = True
        else:
            self.direction.x = 0
        # JUMP.
        if keys[pg.K_SPACE] and self.on_ground:
            self.jump()
            self.load_jump_particle()

    def move(self):
        self.hitbox.x += self.direction.x * self.MOVE_SPEED

    def jump(self):
        self.sound_jump.play()
        self.direction.y = self.JUMP_SPEED

    def fall(self):
        self.direction.y += self.GRAVITY
        self.hitbox.y += self.direction.y

    def get_staus(self):
        if self.direction.y < 0:
            self.status = 'jump'
        elif self.direction.y > 1:
            self.status = 'fall'
        else:
            if self.direction.x != 0:
                self.status = 'run'
            else:
                self.status = 'idle'

    def animate(self):
        # INCREASE.
        animation = self.animations[self.status]
        self.frame_index += self.ANIMATION_SPEEP
        # CHECK RESTART.
        if self.frame_index >= len(animation):
            self.frame_index = 0
        # UPDATE.
        image = animation[int(self.frame_index)]
        if self.facing_right:
            self.image = image
            self.rect.bottomleft = self.hitbox.bottomleft
        else:
            self.image = pg.transform.flip(image, True, False)
            self.rect.bottomright = self.hitbox.bottomright
        # INVINCIBLE EFFECT.
        if self.invincible:
            self.image.set_alpha(self.get_alpha_value())
        else:
            self.image.set_alpha(255)
        self.rect = self.image.get_rect(midbottom=self.rect.midbottom)

    def animate_dust(self):
        if self.on_ground and self.status == 'run':
            self.dust_frame_index += self.DUST_ANIMATION_SPEEP
            if self.dust_frame_index >= len(self.dust_animations):
                self.dust_frame_index = 0
            image = self.dust_animations[int(self.dust_frame_index)]
            if self.facing_right:
                place = self.rect.bottomleft - pg.math.Vector2(6, 10)
                self.screen.blit(image, place)
            else:
                place = self.rect.bottomright - pg.math.Vector2(6, 10)
                flipped_image = pg.transform.flip(image, True, False)
                self.screen.blit(flipped_image, place)

    def invincible_timer(self):
        if self.invincible and pg.time.get_ticks() - self.hurt_time > self.INVINCIBLE_DURATION:
            self.invincible = False

    def get_damage(self):
        if not self.invincible:
            self.sound_hit.play()
            self.update_health(-10)
            # INVINCIBLE TIME.
            self.invincible = True
            self.hurt_time = pg.time.get_ticks()

    def get_alpha_value(self):
        return 0 if sin(pg.time.get_ticks()) < 0 else 255

    def update(self):
        # INPUT.
        self.input()
        self.get_staus()
        # ANIMATION & PARTICLE.
        self.animate()
        self.animate_dust()
        # TIMER.
        self.invincible_timer()
