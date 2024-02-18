from math import ceil
from random import choice, randint
from typing import Self

from settings import *
from sprites import Cloud, Icon, Sprite
from statistic import Data
from timers import Timer


class WorldSprite(pg.sprite.Group):
    def __init__(self, data: Data):
        super().__init__()
        self.screen = pg.display.get_surface()
        self.offset = Vector2()
        self.data = data

    def draw(self: Union[Self, Sequence[Sprite]], player_pos: Point):
        # SET OFFSET RELATIVE TO PLAYER.
        self.offset.x = -(player_pos[0] - WINDOW_WIDTH / 2)
        self.offset.y = -(player_pos[1] - WINDOW_HEIGHT / 2)
        # DRAW BACKGROUND.
        for sprite in sorted(self, key=lambda sprite: sprite.z):
            sprite: Sprite

            if sprite.z < Z_LAYERS["MAIN"]:
                offset_pos = sprite.rect.topleft + self.offset
                # ONLY DRAW THE UNLOCKED LEVEL.
                if sprite.z == Z_LAYERS["PATH"]:
                    if sprite.level <= self.data.unlocked_level:
                        self.screen.blit(sprite.image, offset_pos)
                else:
                    self.screen.blit(sprite.image, offset_pos)
        # DRAW MAIN.
        for sprite in sorted(self, key=lambda sprite: sprite.rect.centery):
            sprite: Sprite
            if sprite.z == Z_LAYERS["MAIN"]:
                offset_pos = sprite.rect.topleft + self.offset
                if isinstance(sprite, Icon):
                    self.screen.blit(sprite.image, offset_pos + Vector2(0, -28))
                else:
                    self.screen.blit(sprite.image, offset_pos)


class AllSprites(pg.sprite.Group):
    def __init__(
        self,
        width: int,
        height: int,
        bg_tile: Surface,
        top_limit: int,
        clouds: Frame,
        skyline: int,
    ):
        super().__init__()
        self.screen = pg.display.get_surface()
        self.offset = Vector2()
        # DRAW BACKGROUND.
        self.width = width * TILE_SIZE
        self.height = height * TILE_SIZE
        self.skyline = skyline
        self.has_sky = not bg_tile
        # CONSTRAINTS.
        self.BORDERS = {
            "LEFT": 0,
            "RIGHT": -self.width + WINDOW_WIDTH,
            "BOTTOM": -self.height + WINDOW_HEIGHT,
            "TOP": top_limit,
        }
        # BACKGROUND.
        if bg_tile:
            for row in range(-ceil(top_limit / TILE_SIZE), height):
                for col in range(width):
                    x, y = col * TILE_SIZE, row * TILE_SIZE
                    Sprite((x, y), bg_tile, self, -1)
        else:
            # FRAMES.
            self.small_cloud = clouds["small_cloud"]
            self.large_cloud = clouds["large_cloud"]
            self.CLOUD_DIRECTION = -1
            # LARGE CLOUD.
            self.LC_x, self.LC_SPEED = 0, 50
            self.LC_WIDTH, self.LC_HEIGHT = self.large_cloud.get_size()
            self.LC_TILES = int(self.width / self.LC_WIDTH) + 2
            # SMALL CLOUD.
            self.SC_WIDTH, self.SC_HEIGHT = self.small_cloud[0].get_size()
            self.SC_timer = Timer(2500, self.spawn_small_cloud, True)
            self.SC_timer.activate()
            for _ in range(20):
                x = randint(0, self.width)
                y = randint(-self.BORDERS["TOP"], self.skyline)
                Cloud((x, y), choice(self.small_cloud), self)

    def spawn_small_cloud(self):
        x = randint(self.width, self.width + 200)
        y = randint(-self.BORDERS["TOP"], self.skyline)
        Cloud((x, y), choice(self.small_cloud), self)

    def draw_large_clouds(self, delta_time: float):
        # MOVEMENT.
        self.LC_x += self.CLOUD_DIRECTION * self.LC_SPEED * delta_time
        y = self.skyline - self.LC_HEIGHT + self.offset.y
        if self.LC_x <= -self.LC_WIDTH:
            self.LC_x = 0
        # DRAW.
        for tile in range(self.LC_TILES):
            x = self.LC_x + tile * self.LC_WIDTH + self.offset.x
            self.screen.blit(self.large_cloud, (x, y))

    def camera_constraint(self):
        if self.offset.x >= self.BORDERS["LEFT"]:
            self.offset.x = self.BORDERS["LEFT"]
        if self.offset.x <= self.BORDERS["RIGHT"]:
            self.offset.x = self.BORDERS["RIGHT"]
        if self.offset.y <= self.BORDERS["BOTTOM"]:
            self.offset.y = self.BORDERS["BOTTOM"]
        if self.offset.y >= self.BORDERS["TOP"]:
            self.offset.y = self.BORDERS["TOP"]

    def draw_sky(self):
        skyline = self.skyline + self.offset.y
        # DRAW SKY.
        self.screen.fill("#DDC6A1")
        # DRAW SEA.
        sea_rect = pg.FRect(0, skyline, self.width, self.height - skyline)
        pg.draw.rect(self.screen, "#92A9CE", sea_rect)
        # DRAW SKYLINE.
        pg.draw.line(self.screen, "#F5F1DE", (0, skyline), (WINDOW_WIDTH, skyline), 4)

    def draw(self: Union[Self, Sequence[Sprite]], player_pos: Point, delta_time: float):
        # SET OFFSET RELATIVE TO PLAYER.
        self.offset.x = -(player_pos[0] - WINDOW_WIDTH / 2)
        self.offset.y = -(player_pos[1] - WINDOW_HEIGHT / 2)
        self.camera_constraint()
        # DRAW SKY.
        if self.has_sky:
            self.SC_timer.update()
            self.draw_sky()
            self.draw_large_clouds(delta_time)
        # DRAW SPRITE.
        for sprite in sorted(self, key=lambda sprite: sprite.z):
            sprite: Sprite

            offset_pos = sprite.rect.topleft + self.offset
            self.screen.blit(sprite.image, offset_pos)
