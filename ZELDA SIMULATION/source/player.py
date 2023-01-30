import pygame as pg


class Player(pg.sprite.Sprite):

    def __init__(self, place, groups, group_obstacle: pg.sprite.Group):
        super().__init__(groups)
        # CORE.
        self.image = pg.image.load('image/player.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=place)
        # COLLIDING RECT.
        self.hitbox = self.rect.inflate(0, -26)
        # MOVEMENT.
        self.direction = pg.math.Vector2()
        # COLLISION.
        self.group_obstacle = group_obstacle

    def input(self):
        keys = pg.key.get_pressed()

        if keys[pg.K_LEFT]:
            self.direction.x = -1
        elif keys[pg.K_RIGHT]:
            self.direction.x = 1
        else:
            self.direction.x = 0

        if keys[pg.K_UP]:
            self.direction.y = -1
        elif keys[pg.K_DOWN]:
            self.direction.y = 1
        else:
            self.direction.y = 0

    def move(self, speed: int):
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        self.hitbox.x += self.direction.x * speed
        self.collide('Horizontal')

        self.hitbox.y += self.direction.y * speed
        self.collide('Vertical')

        self.rect.center = self.hitbox.center

    def collide(self, direction: str):
        if direction == 'Horizontal':
            for sprite in self.group_obstacle.sprites():
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.x < 0:
                        self.hitbox.left = sprite.hitbox.right
                    else:
                        self.hitbox.right = sprite.hitbox.left
        else:
            for sprite in self.group_obstacle.sprites():
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.y < 0:
                        self.hitbox.top = sprite.hitbox.bottom
                    else:
                        self.hitbox.bottom = sprite.hitbox.top

    def update(self):
        self.input()
        self.move(8)
