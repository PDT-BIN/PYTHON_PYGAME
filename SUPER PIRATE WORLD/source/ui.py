from random import randint

from settings import *
from sprites import AnimatedSprite
from timers import Timer


class UI:
    def __init__(self, font: Font, ui_frames: Asset):
        self.screen = pg.display.get_surface()
        self.font = font
        # GROUP.
        self.all_sprites = pg.sprite.Group()
        # GRAPHIC.
        self.frames_heart = ui_frames["heart"]
        self.surface_coin = ui_frames["coin"]
        # COINS.
        self.coin_quantity = 0
        # TIMER.
        self.coin_timer = Timer(1000)

    def update_health(self, quantity: int):
        # REMOVE OLD SPRITE.
        for sprite in self.all_sprites:
            sprite.kill()
        # CREATE NEW SPRITE.
        WIDTH, GAP = self.frames_heart[0].get_width(), 10
        for i in range(quantity):
            x, y = GAP + i * (WIDTH + GAP), GAP
            Heart((x, y), self.frames_heart, self.all_sprites)

    def update_coins(self, quanity: int):
        self.coin_quantity = quanity
        self.coin_timer.activate()

    def show_coins(self):
        if self.coin_timer.is_active:
            # DRAW QUANTITY.
            text_surface = self.font.render(str(self.coin_quantity), False, "#33323D")
            text_rect = text_surface.get_frect(topleft=(10, 30))
            self.screen.blit(text_surface, text_rect)
            # DRAW ICON.
            coin_rect = self.surface_coin.get_rect(center=text_rect.bottomright)
            self.screen.blit(self.surface_coin, coin_rect.move(12, -5))

    def update(self, delta_time: float):
        self.coin_timer.update()
        self.all_sprites.update(delta_time)
        self.all_sprites.draw(self.screen)
        self.show_coins()


class Heart(AnimatedSprite):
    def __init__(self, position: Point, frames: Frame, groups: Group):
        super().__init__(position, frames, groups)
        self.is_active = False

    def animate(self, delta_time: float):
        self.frame_index += self.ANIMATION_SPEED * delta_time
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
        else:
            self.frame_index = 0
            self.is_active = False

    def update(self, delta_time: float):
        if self.is_active:
            self.animate(delta_time)
        else:
            if randint(0, 2000) == 1:
                self.is_active = True
