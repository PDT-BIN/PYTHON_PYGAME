from random import randint
from sys import exit

import pygame

from meteor import Meteor
from score import Score
from ship import Ship


class Game:

    def __init__(self):
        # SYSTEM.
        pygame.init()
        self.clock = pygame.time.Clock()
        # SETTINGS.
        self.background = pygame.image.load('image/BACKGROUND.png')
        self.screen = pygame.display.set_mode((1280, 720))
        pygame.display.set_caption('Space Shooter')
        # ENTITIES.
        self.group_ship = pygame.sprite.GroupSingle()
        self.ship = Ship(self.screen, self.group_ship)
        self.group_meteor = pygame.sprite.Group()
        self.score = Score(self.screen)
        # CUSTOM EVENT.
        self.METEOR_FALLING = pygame.USEREVENT + 1
        pygame.time.set_timer(self.METEOR_FALLING, 400)

    def run(self):
        pygame.mouse.set_visible(False)
        pygame.mixer.music.load('music/MUSIC.wav')
        pygame.mixer.music.play(-1)
        while True:
            # EVENT.
            for event in pygame.event.get():
                match event.type:
                    case pygame.QUIT:
                        Game.quit()
                    case self.METEOR_FALLING:
                        self.spawn()
            self.lost()
            # DELTA TIME.
            self.delta = self.clock.tick() / 1000
            # BACKGROUND.
            self.screen.blit(self.background, (0, 0))
            # UPDATE.
            self.group_ship.update(self.delta, self.group_meteor)
            self.group_meteor.update(self.delta, self.screen.get_height())
            # DRAW.
            self.score.draw()
            self.group_ship.draw(self.screen)
            self.group_meteor.draw(self.screen)
            pygame.display.update()

    def spawn(self):
        rand_x = randint(-100, self.screen.get_width() + 100)
        rand_y = randint(-150, -50)
        Meteor((rand_x, rand_y), self.group_meteor)

    def lost(self):
        if self.ship.ship_collision(self.group_meteor):
            Game.quit()

    @staticmethod
    def quit():
        pygame.quit()
        exit()


if __name__ == '__main__':
    Game().run()
