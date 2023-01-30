from collections.abc import Callable

import pygame as pg
from asset import LEVELS
from decoration import Sky
from support import load_image_folder


class Stage(pg.sprite.Sprite):

    def __init__(self, place: tuple[int, int], is_unlocked: bool, path: str):
        super().__init__()
        # ANIMATION.
        self.animations = load_image_folder(path)
        self.frame_index, self.SPEED = 0, 0.15
        # CORE.
        self.image = self.animations[self.frame_index]
        self.rect = self.image.get_rect(center=place)
        self.status = is_unlocked
        # COLLISION.
        self.colliding_point = place

    def animate(self):
        self.frame_index += self.SPEED
        if self.frame_index >= len(self.animations):
            self.frame_index = 0
        self.image = self.animations[int(self.frame_index)]

    def update(self):
        if self.status:
            self.animate()
        else:
            self.tinted_image = self.image.copy()
            self.tinted_image.fill('BLACK', special_flags=pg.BLEND_RGBA_MULT)
            self.image.blit(self.tinted_image, (0, 0))


class Mark(pg.sprite.Sprite):

    def __init__(self, place: tuple[int, int]):
        super().__init__()
        # CORE.
        self.image = pg.image.load('image/overworld/hat.png').convert_alpha()
        self.rect = self.image.get_rect(center=place)
        # MOVEMENT.
        self.pos = place

    def update(self):
        self.rect.center = self.pos


class Overworld:

    def __init__(self, start_level: int, max_level: int, load_level: Callable[[int], None]):
        # CORE.
        self.screen = pg.display.get_surface()
        self.load_level = load_level
        self.current_level = start_level
        self.max_level = max_level
        # MARK SETUP.
        self.is_moving = False
        self.direction, self.SPEED = pg.math.Vector2(), 8
        # ACTIVE.
        self.init_stage()
        self.init_mark()
        # BACKGROUND.
        self.sky = Sky('OVERWORLD')
        # DELAY TIMER.
        self.enter_time = pg.time.get_ticks()
        self.allow_input, self.DELAY_DURATION = False, 500

    def init_stage(self):
        self.group_stage = pg.sprite.Group()
        for index, data in LEVELS.items():
            is_unlocked = index <= self.max_level
            self.group_stage.add(
                Stage(data['PLACE'], is_unlocked, data['GRAPHIC']))

    def init_mark(self):
        self.group_mark = pg.sprite.GroupSingle()
        self.group_mark.add(Mark(LEVELS[self.current_level]['PLACE']))

    def draw_links(self):
        if self.max_level > 0:
            points = [data['PLACE'] for index, data in LEVELS.items()
                      if index <= self.max_level]
            pg.draw.lines(self.screen, '#A04F45', False, points, 5)

    def input(self):
        # INFORMATION.
        keys = pg.key.get_pressed()
        # CALCULATE.
        if not self.is_moving and self.allow_input:
            if keys[pg.K_LEFT] and self.current_level > 0:
                self.direction = self.get_direction(-1)
                self.current_level -= 1
                self.is_moving = True
            elif keys[pg.K_RIGHT] and self.current_level < self.max_level:
                self.direction = self.get_direction(1)
                self.current_level += 1
                self.is_moving = True
            elif keys[pg.K_SPACE]:
                self.load_level(self.current_level)

    def get_direction(self, aim: int):
        # INFORMATION.
        src = pg.math.Vector2(LEVELS[self.current_level]['PLACE'])
        dst = pg.math.Vector2(LEVELS[self.current_level + aim]['PLACE'])
        # CALCULATE.
        return (dst - src).normalize()

    def update_mark(self):
        if self.is_moving:
            mark: Mark = self.group_mark.sprite
            mark.pos += self.direction * self.SPEED
            dest: Stage = self.group_stage.sprites()[self.current_level]
            if mark.rect.collidepoint(dest.colliding_point):
                self.is_moving = False
                self.direction.update()

    def input_timer(self):
        if not self.allow_input and pg.time.get_ticks() - self.enter_time > self.DELAY_DURATION:
            self.allow_input = True

    def run(self):
        # TIMER.
        self.input_timer()
        # SYSTEM.
        self.input()
        self.update_mark()
        # BACKGROUND.
        self.sky.draw()
        # STAGE.
        self.draw_links()
        self.group_stage.update()
        self.group_stage.draw(self.screen)
        # MARK.
        self.group_mark.update()
        self.group_mark.draw(self.screen)
