from sys import exit

import pygame as pg


# HEALTH BAR.
class StaticHealthBar:

    def __init__(self):
        # CORE.
        self.image = pg.image.load('image/HEALTH_BAR.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=(25, 25))
        # INFORMATION.
        BAR_WIDTH, BAR_HEIGHT = 156, 7
        self.MAX_HEALTH, self.cur_health = 1000, 500
        self.health_rect = pg.Rect(25 + 32, 25 + 27, 0, BAR_HEIGHT)
        self.RATIO = BAR_WIDTH / self.MAX_HEALTH

    def update(self, quantity: int):
        self.cur_health += quantity
        if self.cur_health < 0:
            self.cur_health = 0
        elif self.cur_health > self.MAX_HEALTH:
            self.cur_health = self.MAX_HEALTH

    def ratio(self, value: int):
        return int(value * self.RATIO)

    def draw(self):
        # UPDATE RECT.
        self.health_rect.width = self.ratio(self.cur_health)
        # DRAW.
        screen.blit(self.image, self.rect)
        pg.draw.rect(screen, 'RED', self.health_rect)


class AnimatingHealthBar:

    def __init__(self):
        # CORE.
        self.image = pg.image.load('image/HEALTH_BAR.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=(25, 75))
        # INFORMATION.
        BAR_WIDTH, BAR_HEIGHT = 156, 7
        self.MAX_HEALTH, self.cur_health = 1000, 0
        self.health_rect = pg.Rect(25 + 32, 75 + 27, 0, BAR_HEIGHT)
        self.RATIO = BAR_WIDTH / self.MAX_HEALTH
        # ANIMATION.
        self.tar_health, self.SPEED = 500, 5
        self.gap_rect = pg.Rect(0, 75 + 27, 0, BAR_HEIGHT)

    def update(self, quantity: int):
        self.tar_health += quantity
        if self.tar_health < 0:
            self.tar_health = 0
        elif self.tar_health > self.MAX_HEALTH:
            self.tar_health = self.MAX_HEALTH

    def ratio(self, value: int):
        return int(value * self.RATIO)

    def draw(self):
        # GAP INFORMATION.
        gap_color = 'RED'
        # UPDATE HEALTH.
        if self.cur_health < self.tar_health:
            self.cur_health += self.SPEED
            gap_color = 'GREEN'
        elif self.cur_health > self.tar_health:
            self.cur_health -= self.SPEED
            gap_color = 'YELLOW'
        # UPDATE RECT.
        self.health_rect.width = self.ratio(self.cur_health)
        gap_width = self.ratio(self.tar_health - self.cur_health)
        self.gap_rect.x = self.health_rect.right + gap_width * (gap_width < 0)
        self.gap_rect.width = abs(gap_width)
        # DRAW.
        screen.blit(self.image, self.rect)
        pg.draw.rect(screen, 'RED', self.health_rect)
        pg.draw.rect(screen, gap_color, self.gap_rect)


# DISPLAY.
pg.init()
screen = pg.display.set_mode((250, 175))
pg.display.set_caption('Health Bar Simulation')
pg.display.set_icon(pg.image.load('image/HEART.png').convert_alpha())
# SYSTEM.
clock = pg.time.Clock()

# ENTITY.
player_1 = StaticHealthBar()
player_2 = AnimatingHealthBar()

# MAIN.
while True:
    # EVENT.
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            exit()
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_UP:
                player_1.update(200)
                player_2.update(200)
            if event.key == pg.K_DOWN:
                player_1.update(-200)
                player_2.update(-200)
    # UPDATE & DRAW.
    screen.fill('#000000')
    player_1.draw()
    player_2.draw()
    # SYSTEM.
    pg.display.update()
    clock.tick(60)
