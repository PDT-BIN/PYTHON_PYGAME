from math import cos, radians, sin
from random import randint

from settings import *


class Sprite(pg.sprite.Sprite):
    def __init__(
        self,
        position: Point,
        surface: Surface = Surface((TILE_SIZE, TILE_SIZE)),
        groups: Group = (),
        z_index: int = Z_LAYERS["MAIN"],
    ):
        super().__init__(groups)
        self.image = surface
        self.rect = self.image.get_frect(topleft=position)
        self.old_rect = self.rect.copy()
        self.z = z_index


class AnimatedSprite(Sprite):
    def __init__(
        self,
        position: Point,
        frames: Frame,
        groups: Group = (),
        z_index: int = Z_LAYERS["MAIN"],
        animation_speed: float = ANIMATION_SPEED,
    ):
        self.frames, self.frame_index = frames, 0
        surface = self.frames[self.frame_index]
        super().__init__(position, surface, groups, z_index)
        # ANIMATION.
        self.ANIMATION_SPEED = animation_speed

    def animate(self, delta_time: float):
        self.frame_index += self.ANIMATION_SPEED * delta_time
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

    def update(self, delta_time: float):
        self.animate(delta_time)


class MovingSprite(AnimatedSprite):
    def __init__(
        self,
        frames: Frame,
        groups: Group,
        start_pos: Point,
        end_pos: Point,
        move_direction: Literal["X", "Y"],
        speed: int,
        flip: bool = False,
    ):
        super().__init__(start_pos, frames, groups)
        # OVERRIDE.
        if move_direction == "X":
            self.rect.midleft = start_pos
        else:
            self.rect.midtop = start_pos
        # MOVEMENT.
        self.MOVING = True
        self.move_direction = move_direction
        self.start_pos, self.end_pos = start_pos, end_pos
        self.direction = Vector2(1, 0) if move_direction == "X" else Vector2(0, 1)
        self.speed = speed
        self.flip = flip
        self.reverse = {"flip_x": False, "flip_y": False}

    def check_boundary(self):
        if self.move_direction == "X":
            # BOUNCE TO THE RIGHT.
            if self.rect.left <= self.start_pos[0]:
                self.direction.x = 1
                self.rect.left = self.start_pos[0]
            # BOUNCE TO THE LEFT.
            if self.rect.right >= self.end_pos[0]:
                self.direction.x = -1
                self.rect.right = self.end_pos[0]
            # REVERSE.
            self.reverse["flip_x"] = self.direction.x < 0
        else:
            # BOUNCE TO THE BOTTOM.
            if self.rect.top <= self.start_pos[1]:
                self.direction.y = 1
                self.rect.top = self.start_pos[1]
            # BOUNCE TO THE TOP.
            if self.rect.bottom >= self.end_pos[1]:
                self.direction.y = -1
                self.rect.bottom = self.end_pos[1]
            # REVERSE.
            self.reverse["flip_y"] = self.direction.y < 0

    def update(self, delta_time: float):
        self.old_rect = self.rect.copy()
        self.rect.topleft += self.direction * self.speed * delta_time
        self.check_boundary()
        self.animate(delta_time)
        if self.flip:
            self.image = pg.transform.flip(self.image, **self.reverse)


class Spike(Sprite):
    def __init__(
        self,
        center: Point,
        surface: Surface,
        groups: Group,
        radius: float,
        speed: int,
        start_angle: float,
        end_angle: float,
        z_index: int = Z_LAYERS["MAIN"],
    ):
        self.center = center
        self.radius = radius
        self.speed = speed
        self.start_angle = start_angle
        self.end_angle = end_angle
        # MOVEMENT.
        self.angle = start_angle
        self.direction = 1
        self.is_full_circle = self.end_angle == -1
        # OVERRIDE.
        super().__init__(self.get_trigonometry_position(), surface, groups, z_index)

    def get_trigonometry_position(self) -> Point:
        x = self.center[0] + cos(radians(self.angle)) * self.radius
        y = self.center[1] + sin(radians(self.angle)) * self.radius
        return x, y

    def update(self, delta_time: float):
        self.angle += self.direction * self.speed * delta_time
        # REVERSE IF NOT FULL CIRCLE.
        if not self.is_full_circle:
            if self.angle >= self.end_angle:
                self.direction = -1
            if self.angle <= self.start_angle:
                self.direction = 1
        # UPDATE IMAGE POSITION.
        self.rect.center = self.get_trigonometry_position()


class Item(AnimatedSprite):
    def __init__(
        self, item_type: str, position: Point, frames: Frame, groups: Group, data
    ):
        self.item_type = item_type
        self.data = data
        super().__init__(position, frames, groups)
        # OVERRIDE.
        self.rect.center = position

    def get_reward(self):
        match self.item_type:
            case "silver":
                self.data.coins += 1
            case "gold":
                self.data.coins += 5
            case "diamond":
                self.data.coins += 10
            case "skull":
                self.data.coins += 50
            case "potion":
                self.data.health += 1


class ParticleEffect(AnimatedSprite):
    def __init__(self, position: Point, frames: Frame, groups: Group):
        super().__init__(position, frames, groups, Z_LAYERS["FG"])
        # OVERRIDE.
        self.rect.center = position

    def animate(self, delta_time: float):
        self.frame_index += self.ANIMATION_SPEED * delta_time
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
        else:
            self.kill()


class Cloud(Sprite):
    def __init__(self, position: Point, surface: Surface, groups: Group):
        super().__init__(position, surface, groups, Z_LAYERS["CLOUDS"])
        # OVERRIDE.
        self.rect.midbottom = position
        # MOVEMENT.
        self.DIRECTION = -1
        self.SPEED = randint(50, 120)

    def update(self, delta_time: float):
        self.rect.x += self.DIRECTION * self.SPEED * delta_time
        # DESTROY.
        if self.rect.right <= 0:
            self.kill()


class Node(pg.sprite.Sprite):
    def __init__(
        self,
        position: Point,
        surface: Surface,
        groups: Group,
        level: int,
        data,
        paths: Mapping[str, str],
    ):
        # self.grid_pos = (position - Vector2(TILE_SIZE / 2, TILE_SIZE / 2)) / TILE_SIZE
        super().__init__(groups)
        self.image = surface
        self.rect = self.image.get_frect(center=position)
        self.z = Z_LAYERS["PATH"]
        self.level = level
        self.data = data
        # AVAILABLE PATHS.
        self.paths = paths

    def can_move(self, direction: str):
        """ONLY CAN MOVE BETWEEN UNLOCKED LEVELS"""
        return (
            direction in self.paths.keys()
            and int(self.paths[direction][0]) <= self.data.unlocked_level
        )


class Icon(pg.sprite.Sprite):
    def __init__(self, position: Point, frames: Frame, groups: Group):
        super().__init__(groups)
        self.frames, self.frame_index = frames, 0
        self.state = "idle"
        self.image = self.frames[self.state][self.frame_index]
        self.rect = self.image.get_frect(center=position)
        self.z = Z_LAYERS["MAIN"]
        # MOVEMENT.
        self.direction = Vector2()
        self.SPEED = 400
        self.path = None

    def start_move(self, path: Path):
        self.rect.center = path[0]
        self.path = path[1:]
        self.find_path()

    def find_path(self):
        if self.path:
            # VERTICAL.
            if self.rect.centerx == self.path[0][0]:
                y = 1 if self.rect.centery < self.path[0][1] else -1
                self.state = "down" if y == 1 else "up"
                self.direction = Vector2(0, y)
            # HORIZONTAL.
            else:
                x = 1 if self.rect.centerx < self.path[0][0] else -1
                self.state = "right" if x == 1 else "left"
                self.direction = Vector2(x, 0)
        else:
            self.state = "idle"
            self.frame_index = 0
            self.direction = Vector2()

    def follow_path(self):
        # VERTICAL.
        if (self.direction.y == 1 and self.rect.centery >= self.path[0][1]) or (
            self.direction.y == -1 and self.rect.centery <= self.path[0][1]
        ):
            self.rect.centery = self.path[0][1]
            del self.path[0]
            self.find_path()
        # HORIZONTAL.
        if (self.direction.x == 1 and self.rect.centerx >= self.path[0][0]) or (
            self.direction.x == -1 and self.rect.centerx <= self.path[0][0]
        ):
            self.rect.centerx = self.path[0][0]
            del self.path[0]
            self.find_path()

    def animate(self, delta_time: float):
        self.frame_index += ANIMATION_SPEED * delta_time
        if self.frame_index >= len(self.frames[self.state]):
            self.frame_index = 0
        self.image = self.frames[self.state][int(self.frame_index)]

    def update(self, delta_time: float):
        if self.path:
            self.rect.center += self.direction * self.SPEED * delta_time
            self.follow_path()
            self.animate(delta_time)


class Path(Sprite):
    def __init__(self, position: Point, surface: Surface, groups: Group, level: int):
        super().__init__(position, surface, groups, Z_LAYERS["PATH"])
        self.level = level
