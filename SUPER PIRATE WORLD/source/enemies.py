from random import choice

from player import Player
from settings import *
from sprites import Sprite
from timers import Timer


class Tooth(pg.sprite.Sprite):
    def __init__(
        self,
        position: Point,
        frames: Frame,
        groups: Group,
        group_collidable: Sequence[Sprite],
    ):
        super().__init__(groups)
        self.frames, self.frame_index = frames, 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_frect(topleft=position)
        self.z = Z_LAYERS["MAIN"]
        # MOVEMENT.
        self.direction = choice((-1, 1))
        self.SPEED = 200
        self.collidable_rects = [sprite.rect for sprite in group_collidable]
        self.reverse_timer = Timer(1000)

    def reverse(self):
        if not self.reverse_timer.is_active:
            self.direction *= -1
            self.reverse_timer.activate()

    def move(self, delta_time: float):
        self.rect.x += self.direction * self.SPEED * delta_time
        # CHECK BOUNDARY.
        position = self.rect.topleft + Vector2(-1, 0)
        WALL_RECT = pg.FRect(position, (self.rect.width + 2, 1))
        FLOOR_LEFT = pg.FRect(self.rect.bottomleft, (-1, 1))
        FLOOR_RIGHT = pg.FRect(self.rect.bottomright, (1, 1))

        if (
            WALL_RECT.collidelist(self.collidable_rects) != -1
            or (
                FLOOR_LEFT.collidelist(self.collidable_rects) < 0 and self.direction < 0
            )
            or (
                FLOOR_RIGHT.collidelist(self.collidable_rects) < 0
                and self.direction > 0
            )
        ):
            self.direction *= -1

    def animate(self, delta_time: float):
        self.frame_index += ANIMATION_SPEED * delta_time
        # RESET INDEX.
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]
        # FLIP IMAGE.
        if self.direction == -1:
            self.image = pg.transform.flip(self.image, True, False)

    def update(self, delta_time: float):
        self.reverse_timer.update()
        self.move(delta_time)
        self.animate(delta_time)


class Shell(pg.sprite.Sprite):
    def __init__(
        self,
        position: Point,
        frames: Frame,
        groups: Group,
        player: Player,
        reverse: bool,
        create_pearl: Callable[[Point, int], None],
    ):
        super().__init__(groups)
        self.player = player
        self.frame_index = 0
        # REVERSE.
        if reverse:
            self.bullet_direction = -1
            self.frames = {}
            for key, surfaces in frames.items():
                self.frames[key] = [
                    pg.transform.flip(surface, True, False) for surface in surfaces
                ]
        else:
            self.bullet_direction = 1
            self.frames = frames
        self.state = "idle"
        self.image = self.frames[self.state][self.frame_index]
        self.rect = self.image.get_frect(topleft=position)
        self.old_rect = self.rect.copy()
        self.z = Z_LAYERS["MAIN"]
        # ATTACK.
        self.attack_timer = Timer(3000)
        self.has_fired = False
        self.create_pearl = create_pearl

    def check_state(self):
        player_pos = Vector2(self.player.hitbox_rect.center)
        shell_pos = Vector2(self.rect.center)
        # PLAYER IS NEAR THE SHELL.
        is_nearby = shell_pos.distance_to(player_pos) <= 500
        # PLAYER IS FRONT OF THE SHELL.
        is_front = (
            shell_pos.x < player_pos.x
            if self.bullet_direction > 0
            else shell_pos.x > player_pos.x
        )
        # PLAYER IS IN THE SAME LEVEL OF SHELL.
        is_level = abs(shell_pos.y - player_pos.y) <= 30
        # PLAYER IS IN ATTACK RANGE OF SHELL.
        if is_nearby and is_front and is_level and not self.attack_timer.is_active:
            self.state = "fire"
            self.attack_timer.activate()

    def attack(self):
        start = self.rect.midright if self.bullet_direction > 0 else self.rect.midleft
        offset = Vector2(10 * self.bullet_direction, 6)
        self.create_pearl(start + offset, self.bullet_direction)

    def animate(self, delta_time: float):
        self.frame_index += ANIMATION_SPEED * delta_time
        # CHECK ATTACK FRAME.
        if self.frame_index < len(self.frames[self.state]):
            self.image = self.frames[self.state][int(self.frame_index)]
            # ATTACKING.
            if (
                self.state == "fire"
                and not self.has_fired
                and int(self.frame_index) == 3
            ):
                self.attack()
                self.has_fired = True
        else:
            self.frame_index = 0
            if self.state == "fire":
                self.state = "idle"
                self.has_fired = False

    def update(self, delta_time: float):
        self.attack_timer.update()
        self.check_state()
        self.animate(delta_time)


class Pearl(pg.sprite.Sprite):
    def __init__(
        self,
        position: Point,
        surface: Surface,
        groups: Group,
        direction: int,
        speed: int,
    ):
        super().__init__(groups)
        self.image = surface
        self.rect = self.image.get_frect(center=position)
        self.z = Z_LAYERS["MAIN"]
        # MOVEMENT.
        self.direction = direction
        self.SPEED = speed
        self.timers = {"LIFE TIMER": Timer(5000), "REVERSE TIMER": Timer(250)}
        self.timers["LIFE TIMER"].activate()

    def update_timers(self):
        for timer in self.timers.values():
            timer.update()

    def destroy(self):
        if not self.timers["LIFE TIMER"].is_active:
            self.kill()

    def reverse(self):
        if not self.timers["REVERSE TIMER"].is_active:
            self.direction *= -1
            self.timers["REVERSE TIMER"].activate()

    def update(self, delta_time: float):
        self.update_timers()
        self.rect.x += self.direction * self.SPEED * delta_time
        self.destroy()
