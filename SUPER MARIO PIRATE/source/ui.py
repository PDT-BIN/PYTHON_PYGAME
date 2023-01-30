import pygame as pg


class UI:

    def __init__(self):
        # CORE.
        self.screen = pg.display.get_surface()
        self.font = pg.font.Font('font/ARCADEPI.ttf', 30)
        # HEALTH BAR.
        self.health_bar = pg.image.load(
            'image/ui/health_bar.png').convert_alpha()
        self.BAR_PLACE, self.BAR_MAX_WIDTH, self.BAR_HEIGHT = (54, 39), 152, 4
        # COIN.
        self.coin = pg.image.load('image/ui/coin.png').convert_alpha()
        self.coin_rect = self.coin.get_rect(topleft=(50, 60))

    def show_health(self, current: int, full: int):
        # BAR HEALTH.
        self.screen.blit(self.health_bar, (20, 10))
        # CALCULATE.
        health_ratio = current / full
        current_bar_width = self.BAR_MAX_WIDTH * health_ratio
        health_bar_rect = pg.Rect(
            self.BAR_PLACE, (current_bar_width, self.BAR_HEIGHT))
        # HEALTH.
        pg.draw.rect(self.screen, 'RED', health_bar_rect)

    def show_coin(self, quantity: int):
        # IMAGE.
        self.screen.blit(self.coin, self.coin_rect)
        # SCORE.
        score_surf = self.font.render(str(quantity), False, '#33323D')
        offset_rect = self.coin_rect.midright + pg.math.Vector2(10, 0)
        score_rect = score_surf.get_rect(midleft=offset_rect)
        self.screen.blit(score_surf, score_rect)

    def run(self, current: int, full: int, quantity: int):
        self.show_health(current, full)
        self.show_coin(quantity)
