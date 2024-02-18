from settings import *
from sprites import *
from statistic import Data
from supports import *
from timers import Timer


class Player(pg.sprite.Sprite):
    def __init__(
        self,
        position: Point,
        frames: Frame,
        groups: Group,
        collidable_group: Sequence[Sprite],
        semicolliable_group: Sequence[Sprite],
        data: Data,
        sound_attack: Audio,
        sound_jump: Audio,
    ):
        super().__init__(groups)
        self.z = Z_LAYERS["MAIN"]
        self.data = data
        # ANIMATION.
        self.frames, self.frame_index = frames, 0
        self.state, self.facing_right = "idle", True
        self.image = self.frames[self.state][self.frame_index]
        # COLLISION.
        self.rect = self.image.get_frect(topleft=position)
        self.hitbox_rect = self.rect.inflate(-76, -36)
        self.old_rect = self.hitbox_rect.copy()
        # MOVEMENT.
        self.direction = Vector2()
        self.SPEED = 200
        self.GRAVITY = 1300
        self.JUMP_HEIGHT = 900
        self.platform: MovingSprite = None
        # ATTACK.
        self.attacking = False
        # STATE.
        self.can_jump = False
        self.on_surface = {"FLOOR": False, "LEFT": False, "RIGHT": False}
        # TIMER.
        self.timers = {
            "WALL JUMP": Timer(400),
            "WALL SLIDE BLOCK": Timer(250),
            "PLATFORM SKIP": Timer(100),
            "ATTACK BLOCK": Timer(500),
            "HIT": Timer(500),
        }
        # GROUP.
        self.group_collidable = collidable_group
        self.group_semicolliable = semicolliable_group
        # SOUND.
        self.sound_attack = sound_attack
        self.sound_jump = sound_jump
        self.sound_jump.set_volume(0.1)

    def update_timers(self):
        """HANDLE TIMERS STATE"""
        for timer in self.timers.values():
            timer.update()

    def input(self):
        """HANDLE INPUT"""
        keys = pg.key.get_pressed()

        if not self.timers["WALL JUMP"].is_active:
            input_vector = Vector2()
            if keys[pg.K_LEFT]:
                input_vector.x -= 1
                self.facing_right = False

            if keys[pg.K_RIGHT]:
                input_vector.x += 1
                self.facing_right = True

            self.direction.x = (
                input_vector.normalize().x
                if input_vector.magnitude() != 0
                else input_vector.x
            )

            if keys[pg.K_DOWN]:
                self.timers["PLATFORM SKIP"].activate()

            if keys[pg.K_x]:
                self.attack()

        if keys[pg.K_SPACE]:
            self.can_jump = True

    def move(self, delta_time: float):
        """HANDLE MOVEMENT"""
        # UPDATE HORIZONTAL MOVEMENT.
        self.hitbox_rect.x += self.direction.x * self.SPEED * delta_time
        self.collide("X")
        # CHECK JUMPING.
        if self.can_jump:
            # JUMP FROM FLOOR.
            if self.on_surface["FLOOR"]:
                self.direction.y = -self.JUMP_HEIGHT
                self.timers["WALL SLIDE BLOCK"].activate()
                self.sound_jump.play()
            # JUMP FROM WALL.
            elif (
                any((self.on_surface["LEFT"], self.on_surface["RIGHT"]))
                and not self.timers["WALL SLIDE BLOCK"].is_active
            ):
                self.timers["WALL JUMP"].activate()
                self.direction.y = -self.JUMP_HEIGHT
                self.direction.x = 1 if self.on_surface["LEFT"] else -1
                self.sound_jump.play()
            self.can_jump = False
        # UPDATE VERTICAL MOVEMENT (SLIDE & JUMP/FALL).
        if (
            not self.on_surface["FLOOR"]
            and any((self.on_surface["LEFT"], self.on_surface["RIGHT"]))
            and not self.timers["WALL SLIDE BLOCK"].is_active
            and not self.timers["WALL JUMP"].is_active
        ):
            self.direction.y = 0  # SLIDING CONSTRAINT.
            self.hitbox_rect.y += self.GRAVITY / 10 * delta_time
        else:
            self.direction.y += self.GRAVITY / 2 * delta_time
            self.hitbox_rect.y += self.direction.y * delta_time
            self.direction.y += self.GRAVITY / 2 * delta_time
        self.collide("Y")
        # SEMI-COLLISION.
        self.semicollide()
        # ASSIGN HITBOX TO RECT.
        self.rect.center = self.hitbox_rect.center

    def collide(self, axis: str):
        """HANDLE COLLISION"""
        for sprite in self.group_collidable:
            if sprite.rect.colliderect(self.hitbox_rect):
                if axis == "X":
                    # LEFT COLLISION.
                    if self.hitbox_rect.left <= sprite.rect.right and int(
                        self.old_rect.left
                    ) >= int(sprite.old_rect.right):
                        self.hitbox_rect.left = sprite.rect.right
                    # RIGHT COLLISION.
                    if self.hitbox_rect.right >= sprite.rect.left and int(
                        self.old_rect.right
                    ) <= int(sprite.old_rect.left):
                        self.hitbox_rect.right = sprite.rect.left
                else:
                    # TOP COLLISION.
                    if self.hitbox_rect.top <= sprite.rect.bottom and int(
                        self.old_rect.top
                    ) >= int(sprite.old_rect.bottom):
                        self.hitbox_rect.top = sprite.rect.bottom
                        # if hasattr(sprite, "MOVING"):  # PLATFORM CONSTRAINT.
                        #     self.hitbox_rect.y += 5
                    # BOTTOM COLLISION.
                    if self.hitbox_rect.bottom >= sprite.rect.top and int(
                        self.old_rect.bottom
                    ) <= int(sprite.old_rect.top):
                        self.hitbox_rect.bottom = sprite.rect.top
                    # FALL DOWN.
                    self.direction.y = 0

    def semicollide(self):
        """HANDLE SEMICOLLISION"""
        if not self.timers["PLATFORM SKIP"].is_active:
            for sprite in self.group_semicolliable:
                if sprite.rect.colliderect(self.hitbox_rect):
                    # BOTTOM COLLISION.
                    if self.hitbox_rect.bottom >= sprite.rect.top and int(
                        self.old_rect.bottom
                    ) <= int(sprite.old_rect.top):
                        self.hitbox_rect.bottom = sprite.rect.top
                        # ONLY STICK TO THE PLATFORM WHEN FALLING DOWN.
                        if self.direction.y > 0:
                            self.direction.y = 0

    def check_contact(self):
        """HANDLE FLOORING & SLIDING STATES"""
        collide_rects = [sprite.rect for sprite in self.group_collidable]
        # CHECK PLAYER IS ON THE FLOOR => FLOORING.
        position = self.hitbox_rect.bottomleft
        RECT_FLOOR = pg.Rect(position, (self.hitbox_rect.width, 2))
        self.on_surface["FLOOR"] = RECT_FLOOR.collidelist(collide_rects) >= 0
        # CHECK PLAYER IS ON THE RIGHT OF THE WALL => SLIDING.
        position = self.hitbox_rect.topleft + Vector2((-2, self.hitbox_rect.height / 4))
        RECT_LEFT = pg.Rect(position, (2, self.hitbox_rect.height / 2))
        self.on_surface["LEFT"] = RECT_LEFT.collidelist(collide_rects) >= 0
        # CHECK PLAYER IS ON THE LEFT OF THE WALL => SLIDING.
        position = self.hitbox_rect.topright + Vector2((0, self.hitbox_rect.height / 4))
        RECT_RIGHT = pg.Rect(position, (2, self.hitbox_rect.height / 2))
        self.on_surface["RIGHT"] = RECT_RIGHT.collidelist(collide_rects) >= 0
        # CHECK PLAYER IS ON A PLATFORM => FLOORING.
        RECT_PLATFORM = [sprite.rect for sprite in self.group_semicolliable]
        # ONLY CHECK WHEN PLAYER FALLS DOWN.
        if self.direction.y >= 0:
            self.on_surface["FLOOR"] |= RECT_FLOOR.collidelist(RECT_PLATFORM) >= 0
        # STORE THE "MOVING" PLATFORM THAT THE PLAYER IS FLOORING.
        self.platform = None
        for sprite in [
            sprite for sprite in self.group_semicolliable if hasattr(sprite, "MOVING")
        ]:
            if sprite.rect.colliderect(RECT_FLOOR):
                self.platform = sprite

    def follow_platfrom(self, delta_time: float):
        """MOVE IN PLATFORM DIRECTION"""
        if self.platform:
            self.hitbox_rect.topleft += (
                self.platform.direction * self.platform.speed * delta_time
            )

    def attack(self):
        if not self.timers["ATTACK BLOCK"].is_active:
            self.attacking = True
            self.frame_index = 0
            self.timers["ATTACK BLOCK"].activate()
            self.sound_attack.play()

    def check_state(self):
        # ON THE GROUND.
        if self.on_surface["FLOOR"]:
            if self.attacking:
                self.state = "attack"
            else:
                self.state = "idle" if self.direction.x == 0 else "run"
        # ON THE AIR.
        else:
            if self.attacking:
                self.state = "air_attack"
            else:
                if any((self.on_surface["LEFT"], self.on_surface["RIGHT"])):
                    self.state = "wall"
                else:
                    self.state = "jump" if self.direction.y < 0 else "fall"

    def animate(self, delta_time: float):
        self.frame_index += ANIMATION_SPEED * delta_time
        # RESET FRAME INDEX.
        if self.frame_index >= len(self.frames[self.state]):
            self.frame_index = 0
            # SET "IDLE" STATE AFTER "ATTACK" STATE.
            if self.state == "attack":
                self.state = "idle"
            # STOP ATTACKING WHEN OUT OF ATTACK FRAMES.
            if self.attacking:
                self.attacking = False

        self.image = self.frames[self.state][int(self.frame_index)]
        # FLIP IMAGE IF FACING LEFT.
        if not self.facing_right:
            self.image = pg.transform.flip(self.image, True, False)

    def get_damage(self):
        if not self.timers["HIT"].is_active:
            self.data.health -= 1
            self.timers["HIT"].activate()

    def flick(self):
        if self.timers["HIT"].is_active and sin(pg.time.get_ticks() * 100) >= 0:
            white_mask = pg.mask.from_surface(self.image)
            surface = white_mask.to_surface()
            surface.set_colorkey("BLACK")
            self.image = surface

    def update(self, delta_time: float):
        self.old_rect = self.hitbox_rect.copy()
        self.update_timers()

        self.input()
        self.follow_platfrom(delta_time)
        self.move(delta_time)
        self.check_contact()

        self.check_state()
        self.animate(delta_time)
        self.flick()
