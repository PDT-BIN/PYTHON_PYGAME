from os import walk

import pygame as pg


class Player(pg.sprite.Sprite):
    def __init__(self, pos: tuple, groups: pg.sprite.Group, obstacles: pg.sprite.Group):
        super().__init__(groups)
        # Asserts.
        self.assets()
        self.status, self.frame_index = 'up', 0
        # Core attributes.
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(center=pos)
        # Movement.
        self.pos = pg.math.Vector2(self.rect.center)
        self.direction = pg.math.Vector2()
        self.speed = 200
        # Collision sprites.
        self.obstables = obstacles
        self.hitbox = self.rect.inflate(0, -self.rect.height / 2)

    def collides(self, direction: str):
        match direction:
            case 'horizontal':
                for sprite in self.obstables:
                    if sprite.hitbox.colliderect(self.hitbox):
                        if hasattr(sprite, 'name') and sprite.name == 'car':
                            self.speed = 0
                        else:
                            if self.direction.x > 0:  # Moving right.
                                self.hitbox.right = sprite.hitbox.left
                            if self.direction.x < 0:  # Moving left.
                                self.hitbox.left = sprite.hitbox.right
                            self.rect.centerx = self.hitbox.centerx
                            self.pos.x = self.hitbox.centerx
            case _:
                for sprite in self.obstables:
                    if sprite.hitbox.colliderect(self.hitbox):
                        if hasattr(sprite, 'name') and sprite.name == 'car':
                            self.speed = 0
                        else:
                            if self.direction.y > 0:  # Moving down.
                                self.hitbox.bottom = sprite.hitbox.top
                            if self.direction.y < 0:  # Moving up.
                                self.hitbox.top = sprite.hitbox.bottom
                            self.rect.centery = self.hitbox.centery
                            self.pos.y = self.hitbox.centery

    def assets(self):
        self.animations: dict[str, list[pg.Surface]] = {}
        for index, (path, folders, files) in enumerate(walk('image/player')):
            match index:
                case 0:
                    self.animations = {folder: None for folder in folders}
                case _:
                    keyword = path.split('\\')[1]
                    storage = [pg.image.load(f'{path}/{file}').convert_alpha()
                               for file in files]
                    self.animations[keyword] = storage

    def move(self, dt: float):
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()
        # Horizontal movement + Collision.
        self.pos.x += self.direction.x * self.speed * dt
        self.hitbox.centerx = round(self.pos.x)
        self.rect.centerx = self.hitbox.centerx
        self.collides('horizontal')
        # Vertical movement + Collision.
        self.pos.y += self.direction.y * self.speed * dt
        self.hitbox.centery = round(self.pos.y)
        self.rect.centery = self.hitbox.centery
        self.collides('vertical')

    def input(self):
        keys = pg.key.get_pressed()
        # Horizontal movement.
        if keys[pg.K_LEFT]:
            self.direction.x = -1
            self.status = 'left'
        elif keys[pg.K_RIGHT]:
            self.direction.x = +1
            self.status = 'right'
        else:
            self.direction.x = 0
        # Vertical movement.
        if keys[pg.K_UP]:
            self.direction.y = -1
            self.status = 'up'
        elif keys[pg.K_DOWN]:
            self.direction.y = +1
            self.status = 'down'
        else:
            self.direction.y = 0

    def animate(self, dt: float):
        current_animation = self.animations[self.status]
        match self.direction.magnitude():
            case 0:
                self.frame_index = 0
            case _:
                self.frame_index += 10 * dt
                if self.frame_index >= len(current_animation):
                    self.frame_index = 0
                self.image = current_animation[int(self.frame_index)]

    def restrict(self):
        if self.rect.left < 640:
            self.pos.x = 640 + self.rect.width / 2
            self.rect.left = self.hitbox.left = 640
        if self.rect.right > 2560:
            self.pos.x = 2560 - self.rect.width / 2
            self.rect.right = self.hitbox.right = 2560
        # Hitbox should be above half of height from the bottom.
        if self.rect.bottom > 3500:
            self.pos.y = 3500 - self.rect.height / 2
            self.rect.bottom = 3500
            self.hitbox.centery = self.rect.centery

    def update(self, dt: float):
        self.input()
        self.move(dt)
        self.animate(dt)
        self.restrict()
