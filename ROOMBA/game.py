from sys import exit

import pygame as pg
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder


class PathFinder:
    '''Class to manage looking for the shortest path.'''

    def __init__(self, matrix: list[list[int]]):
        # CORE.
        self.matrix = matrix
        self.gird = Grid(matrix=matrix)
        self.path: list[tuple[int, int]] = []
        # IMAGE.
        self.image = pg.image.load('image/SELECTION.png').convert_alpha()
        self.rect = self.image.get_rect()
        # ROOMBA.
        self.roomba = pg.sprite.GroupSingle(Roomba())

    def draw(self):
        '''Draw the finder symbol.'''
        mouse_pos = pg.mouse.get_pos()
        col, row = mouse_pos[0] // 32, mouse_pos[1] // 32
        if self.matrix[row][col] == 1:
            self.rect.topleft = col * 32, row * 32
            screen.blit(self.image, self.rect)

    def find(self):
        '''Find the shortest path.'''
        mouse_pos = pg.mouse.get_pos()
        # INFORMATION.
        src_x, src_y = self.roomba.sprite.get_pos()
        dst_x, dst_y = mouse_pos[0] // 32, mouse_pos[1] // 32
        # SOURCE & DESTINATION.
        src_pos = self.gird.node(src_x, src_y)
        dst_pos = self.gird.node(dst_x, dst_y)
        # PATH.
        finder = AStarFinder(diagonal_movement=DiagonalMovement.always)
        self.path, _ = finder.find_path(src_pos, dst_pos, self.gird)
        # CLEAN CACHE.
        self.gird.cleanup()
        # SET PATH FOR ROOMBA.
        self.roomba.sprite.set_path(self.path)

    def show(self):
        '''Show the shortest path.'''
        if len(self.path) > 1:
            points: list[tuple[int, int]] = []
            for point in self.path:
                x_pos = point[0] * 32 + 16
                y_pos = point[1] * 32 + 16
                points.append((x_pos, y_pos))
                pg.draw.circle(screen, 'BLACK', (x_pos, y_pos), 1)
            pg.draw.lines(screen, 'BLACK', False, points, 2)

    def update(self):
        '''Update all activities.'''
        self.draw()
        self.show()
        # ROOMBA.
        self.roomba.update()
        self.roomba.draw(screen)


class Roomba(pg.sprite.Sprite):

    def __init__(self):
        super().__init__()
        # CORE.
        self.image = pg.image.load('image/ROOMBA.png').convert_alpha()
        self.rect = self.image.get_rect(center=(64, 64))
        # MOVEMENT.
        self.pos = self.rect.center
        self.direction, self.speed = pg.math.Vector2(), 2
        # PATH.
        self.path: list[tuple[int, int]] = list()
        # COLLISION POINTS.
        self.points: list[pg.Rect] = list()

    def get_pos(self):
        '''Get the Roomba mapping position.'''
        pos = self.rect.center
        return pos[0] // 32, pos[1] // 32

    def set_path(self, path: list[tuple[int, int]]):
        '''Set the Roomba path.'''
        # CREATE PATH.
        self.path = path
        # CREATE COLLISION POINTS.
        self.set_points()
        # SET DIRECTION AT FIRST.
        self.set_direction()

    def set_points(self):
        '''Create all rects of points in the path.'''
        if self.path:
            self.points.clear()
            for point in self.path:
                x_pos = point[0] * 32 + 16 - 2
                y_pos = point[1] * 32 + 16 - 2
                self.points.append(pg.Rect((x_pos, y_pos), (4, 4)))

    def set_direction(self):
        '''Set the direction to the next point on path.'''
        if self.points:
            src_pos = pg.math.Vector2(self.pos)
            dst_pos = pg.math.Vector2(self.points[0].center)
            self.direction = (dst_pos - src_pos).normalize()

    def check_collision(self):
        '''
        Change direction if Roomba reaches the point.\n
        End the path if Roomba passes all the points.
        '''
        if self.points:
            for point in self.points:
                if point.collidepoint(self.pos):
                    del self.points[0]
                    self.set_direction()
        else:
            self.direction.update()
            self.path.clear()

    def update(self):
        '''Update all activities.'''
        # UPDATE MOVEMENT.
        self.pos += self.direction * self.speed
        self.rect.center = self.pos
        # CHECK COLLISION.
        self.check_collision()


pg.init()
# DISPLAY.
DIMENSION = (1280, 720)
screen = pg.display.set_mode(DIMENSION)
pg.display.set_caption('ROOMBA')

# TIME.
clock = pg.time.Clock()

# SETUP.
ground = pg.image.load('image/MAP.png').convert()
MATRIX = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
     0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0,
     1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0,
     1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0,
     0, 0, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0,
     0, 0, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 0],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 0,
     0, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 0,
     0, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1,
     1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1,
     1, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1,
     1, 0, 0, 1, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1,
     1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0,
     0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0,
     0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1,
     1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    [0, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
     1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    [0, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0,
     0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0,
     0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 1, 0, 0, 0],
    [0, 1, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 1,
     1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 0, 0, 1, 1, 1, 1, 0, 0, 0],
    [0, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 1,
     1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 1,
     1,  1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 1,
     1,  1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0],
    [0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 1,
     1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
     0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]
finder = PathFinder(MATRIX)

# MAIN.
pg.mouse.set_visible(False)
while True:
    # EVENT.
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            exit()
        if event.type == pg.MOUSEBUTTONDOWN:
            finder.find()
    # GROUND.
    screen.blit(ground, (0, 0))
    # UPDATE.
    finder.update()
    # DRAW.

    pg.display.update()
    clock.tick(60)
