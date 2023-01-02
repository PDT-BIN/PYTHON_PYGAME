from pygame import Surface
from pygame.draw import rect
from pygame.font import Font
from pygame.math import Vector2
from pygame.time import get_ticks


class Score:
    def __init__(self, screen: Surface):
        self.screen = screen
        self.font = Font('font/SUBATOMIC.ttf', 30)
        self.pos = Vector2(self.screen.get_rect().midbottom) - (0, 80)

    def draw(self):
        score = get_ticks() // 1000
        self.surf = self.font.render(f'SCORE: {score}', True, 'WHITE')
        self.rect = self.surf.get_rect(center=self.pos)
        self.screen.blit(self.surf, self.rect)
        rect(self.screen, 'WHITE', self.rect.inflate(50, 30), 5, 5)
