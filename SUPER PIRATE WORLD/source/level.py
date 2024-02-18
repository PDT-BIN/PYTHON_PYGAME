from random import uniform

from enemies import *
from groups import AllSprites
from player import Player
from pytmx import TiledMap, TiledObject
from settings import *
from sprites import *
from statistic import Data


class Level:
    def __init__(
        self,
        tmx_map: TiledMap,
        level_frames: Asset,
        data: Data,
        switch_stage: Callable[[str, int], None],
        sounds: Audio,
    ):
        self.screen = pg.display.get_surface()
        self.data = data
        self.switch_stage = switch_stage
        # MAP SPECIFICATION.
        self.LEVEL_WIDTH = tmx_map.width * TILE_SIZE
        self.LEVEL_HEIGHT = tmx_map.height * TILE_SIZE
        # GROUP.
        level_properties = self.get_level_properties(tmx_map, level_frames)
        self.level_unlock = level_properties.pop("level_unlock")
        self.all_sprites = AllSprites(**level_properties)
        self.group_collidable: Sequence[Sprite] = pg.sprite.Group()
        self.group_semicolidable = pg.sprite.Group()
        self.group_damage: Sequence[Sprite] = pg.sprite.Group()
        self.group_tooth = pg.sprite.Group()
        self.group_pearl: Sequence[Pearl] = pg.sprite.Group()
        self.group_item: Sequence[Item] = pg.sprite.Group()

        self.load_data(tmx_map, level_frames, sounds)
        # REUSABLE FRAME.
        self.surface_pearl = level_frames["pearl"]
        self.frames_partical = level_frames["particle"]
        # SOUNDS.
        self.sound_item = sounds["ITEM"]
        self.sound_pearl = sounds["PEARL"]
        self.sound_damage = sounds["DAMAGE"]
        self.sound_item.set_volume(0.2)
        self.sound_damage.set_volume(0.5)

    def get_level_properties(self, tmx_map: TiledMap, level_frames: Asset):
        # GET DATA INSTANCE.
        instance: TiledObject = tmx_map.get_layer_by_name("Data")[0]
        # GET PROPERTY DICTIONARY.
        properties = instance.properties
        return {
            "width": tmx_map.width,
            "height": tmx_map.height,
            "bg_tile": level_frames["bg_tiles"].get(properties["bg"], None),
            "top_limit": properties.get("top_limit", 0),
            "clouds": {
                "small_cloud": level_frames["small_cloud"],
                "large_cloud": level_frames["large_cloud"],
            },
            "skyline": properties.get("horizontal_pos", WINDOW_HEIGHT / 2),
            "level_unlock": properties.get("level_unlock", None),
        }

    def load_data(self, tmx_map: TiledMap, level_frames: Asset, sounds: Audio):
        """LOAD DATA FROM TMX FILE & ADD TO GROUPS."""
        for layer in ("BG", "Terrain", "FG", "Platforms"):
            for col_idx, row_idx, surface in tmx_map.get_layer_by_name(layer).tiles():
                groups = [self.all_sprites]
                if layer == "Terrain":
                    groups.append(self.group_collidable)
                if layer == "Platforms":
                    groups.append(self.group_semicolidable)
                match layer:
                    case "BG" | "FG":
                        z = Z_LAYERS["BG TILES"]
                    case _:
                        z = Z_LAYERS["MAIN"]

                Sprite((col_idx * TILE_SIZE, row_idx * TILE_SIZE), surface, groups, z)

        for instance in tmx_map.get_layer_by_name("BG details"):
            name: str = instance.name
            position = instance.x, instance.y
            z_index = Z_LAYERS["BG DETAILS"]
            # STATIC DETAIL.
            if name == "static":
                Sprite(position, instance.image, self.all_sprites, z_index)
            # ANIMATED DETAIL.
            else:
                frames = level_frames[name]
                AnimatedSprite(position, frames, self.all_sprites, z_index)
                # ADD LIGHT EFFECT TO CANDLE DETAIL.
                if name == "candle":
                    position += Vector2(-20, -20)
                    frames = level_frames["candle_light"]
                    AnimatedSprite(position, frames, self.all_sprites, z_index)

        for instance in tmx_map.get_layer_by_name("Moving Objects"):
            instance: TiledObject

            name: str = instance.name
            # TRIGONOMETRY MOVEMENT.
            if name == "spike":
                center = (
                    instance.x + instance.width / 2,
                    instance.y + instance.height / 2,
                )
                Spike(
                    center,
                    level_frames["spike"],
                    (self.all_sprites, self.group_damage),
                    instance.properties["radius"],
                    instance.properties["speed"],
                    instance.properties["start_angle"],
                    instance.properties["end_angle"],
                )
                # DRAW PATH OF SPIKE.
                for radius in range(0, instance.properties["radius"], 20):
                    Spike(
                        center,
                        level_frames["spike_chain"],
                        self.all_sprites,
                        radius,
                        instance.properties["speed"],
                        instance.properties["start_angle"],
                        instance.properties["end_angle"],
                        Z_LAYERS["BG DETAILS"],
                    )
            # HORIZONTAL/VERTICAL MOVEMENT.
            else:
                frames = level_frames[name]
                speed = instance.properties["speed"]
                flip = instance.properties["flip"]
                # GROUP.
                groups = [self.all_sprites]
                if instance.properties["platform"]:
                    groups.append(self.group_semicolidable)
                else:
                    groups.append(self.group_damage)
                # MOVEMENT DIRECTION.
                if instance.width > instance.height:
                    move_direction = "X"
                    start_pos = instance.x, instance.y + instance.height / 2
                    end_pos = (
                        instance.x + instance.width,
                        instance.y + instance.height / 2,
                    )
                else:
                    move_direction = "Y"
                    start_pos = instance.x + instance.width / 2, instance.y
                    end_pos = (
                        instance.x + instance.width / 2,
                        instance.y + instance.height,
                    )
                MovingSprite(
                    frames, groups, start_pos, end_pos, move_direction, speed, flip
                )
                # DRAW PATH OF SAW.
                if name == "saw":
                    surface = level_frames["saw_chain"]
                    if move_direction == "X":
                        y = start_pos[1] - surface.get_height() / 2
                        left, right = int(start_pos[0]), int(end_pos[0])
                        for x in range(left, right, 20):
                            Sprite(
                                (x, y),
                                surface,
                                self.all_sprites,
                                Z_LAYERS["BG DETAILS"],
                            )
                    else:
                        x = start_pos[0] - surface.get_width() / 2
                        top, bottom = int(start_pos[1]), int(end_pos[1])
                        for y in range(top, bottom, 20):
                            Sprite(
                                (x, y),
                                surface,
                                self.all_sprites,
                                Z_LAYERS["BG DETAILS"],
                            )

        for instance in tmx_map.get_layer_by_name("Objects"):
            instance: TiledObject

            name: str = instance.name
            position = instance.x, instance.y
            # PLAYER OBJECT.
            if name == "player":
                self.player = Player(
                    position,
                    level_frames["player"],
                    self.all_sprites,
                    self.group_collidable,
                    self.group_semicolidable,
                    self.data,
                    sounds["ATTACK"],
                    sounds["JUMP"],
                )
            else:
                # STATIC OBJECT.
                if name in ("barrel", "crate"):
                    Sprite(
                        position,
                        instance.image,
                        (self.all_sprites, self.group_collidable),
                    )
                # ANIMATED OBJECT.
                else:
                    # FRAME.
                    frames = (
                        level_frames[name]
                        if "palm" not in name
                        else level_frames["palms"][name]
                    )
                    if name == "floor_spike" and instance.properties["inverted"]:
                        frames = [
                            pg.transform.flip(frame, False, True) for frame in frames
                        ]
                    # GROUP.
                    groups = [self.all_sprites]
                    if name in ("palm_small", "palm_large"):
                        groups.append(self.group_semicolidable)
                    if name in ("saw", "floor_spike"):
                        groups.append(self.group_damage)
                    # Z INDEX.
                    z_index = (
                        Z_LAYERS["MAIN"] if "bg" not in name else Z_LAYERS["BG DETAILS"]
                    )
                    # ANIMATION SPEED.
                    animation_speed = (
                        ANIMATION_SPEED
                        if "palm" not in name
                        else ANIMATION_SPEED + uniform(-1, 1)
                    )
                    AnimatedSprite(position, frames, groups, z_index, animation_speed)
                # FLAG OBJECT.
                if name == "flag":
                    self.FINISH = pg.FRect(
                        instance.x, instance.y, instance.width, instance.height
                    )

        for instance in tmx_map.get_layer_by_name("Enemies"):
            name = instance.name
            position = instance.x, instance.y
            match name:
                case "tooth":
                    Tooth(
                        position,
                        level_frames["tooth"],
                        (self.all_sprites, self.group_damage, self.group_tooth),
                        self.group_collidable,
                    )
                case "shell":
                    Shell(
                        position,
                        level_frames["shell"],
                        (self.all_sprites, self.group_collidable),
                        self.player,
                        instance.properties["reverse"],
                        self.create_pearl,
                    )

        for instance in tmx_map.get_layer_by_name("Items"):
            name = instance.name
            position = instance.x + TILE_SIZE / 2, instance.y + TILE_SIZE / 2
            Item(
                name,
                position,
                level_frames["items"][name],
                (self.all_sprites, self.group_item),
                self.data,
            )

        for instance in tmx_map.get_layer_by_name("Water"):
            for row in range(int(instance.height / TILE_SIZE)):
                for col in range(int(instance.width / TILE_SIZE)):
                    x, y = instance.x + col * TILE_SIZE, instance.y + row * TILE_SIZE
                    if row == 0:
                        AnimatedSprite(
                            (x, y),
                            level_frames["water_top"],
                            self.all_sprites,
                            Z_LAYERS["WATER"],
                        )
                    else:
                        Sprite(
                            (x, y),
                            level_frames["water_body"],
                            self.all_sprites,
                            Z_LAYERS["WATER"],
                        )

    def create_pearl(self, position: Point, direction: int):
        """SHOOTING A PEARL TO THE PLAYER"""
        Pearl(
            position,
            self.surface_pearl,
            (self.all_sprites, self.group_damage, self.group_pearl),
            direction,
            150,
        )
        self.sound_pearl.play()

    def create_particle(self, position: Point):
        ParticleEffect(position, self.frames_partical, self.all_sprites)

    def collide_pearl(self):
        """COLLISION BETWEEN PEARL AND OBSTACLE"""
        for sprite in self.group_collidable:
            for pearl in pg.sprite.spritecollide(sprite, self.group_pearl, True):
                pearl: Pearl
                self.create_particle(pearl.rect.center)

    def collide_player(self):
        """COLLISION BETWEEN PLAYER AND DAMAGABLE SPRITE"""
        for sprite in self.group_damage:
            if sprite.rect.colliderect(self.player.hitbox_rect):
                self.player.get_damage()
                self.sound_damage.play()
                if isinstance(sprite, Pearl):
                    sprite.kill()

    def collide_item(self):
        """COLLISION BETWEEN PLAYER AND ITEM"""
        for sprite in pg.sprite.spritecollide(self.player, self.group_item, True):
            sprite: Item
            sprite.get_reward()
            self.create_particle(sprite.rect.center)
            self.sound_item.play()

    def collide_attack(self):
        """COLLISION BETWEEN PLAYER ATTACK AND PEARL & TOOTH"""
        player_x = self.player.rect.centerx
        for target in self.group_pearl.sprites() + self.group_tooth.sprites():
            target: Union[Pearl, Tooth]
            # FACING TO TARGET.
            target_x = target.rect.centerx
            facing_target = (player_x < target_x and self.player.facing_right) or (
                player_x > target_x and not self.player.facing_right
            )
            # REVERSE TARGET DIRECTION.
            if (
                self.player.rect.colliderect(target.rect)
                and self.player.attacking
                and facing_target
            ):
                target.reverse()

    def check_constraint(self):
        # LEFT CONSTRAINT.
        if self.player.hitbox_rect.left <= 0:
            self.player.hitbox_rect.left = 0
        # RIGHT CONSTRAINT.
        if self.player.hitbox_rect.right >= self.LEVEL_WIDTH:
            self.player.hitbox_rect.right = self.LEVEL_WIDTH
        # BOTTOM CONSTRAINT.
        if self.player.hitbox_rect.bottom >= self.LEVEL_HEIGHT:
            self.switch_stage("OVERWORLD", -1)
        # SUCCESS CONSTRAINT.
        if self.player.hitbox_rect.colliderect(self.FINISH):
            self.switch_stage("OVERWORLD", self.level_unlock)

    def run(self, delta_time: float):
        """UPDATE & DRAW ALL SPRITES."""
        self.screen.fill("BLACK")
        # UPDATE SPRITE.
        self.all_sprites.update(delta_time)
        # SPRITE COLLISION.
        self.collide_pearl()
        self.collide_player()
        self.collide_item()
        self.collide_attack()
        self.check_constraint()
        # DRAW SPRITE.
        self.all_sprites.draw(self.player.hitbox_rect.center, delta_time)
