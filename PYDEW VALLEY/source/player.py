from collections.abc import Callable, Iterable

import pygame as pg
from cooldown import Timer
from settings import *
from soil import SoilLayer
from supports import *


class Player(pg.sprite.Sprite):

    def __init__(self, place: tuple[int, int], groups: Iterable[pg.sprite.Group], group_obstacle: pg.sprite.Group,
                 group_tree: pg.sprite.Group, group_interaction: pg.sprite.Group, soil_layer: SoilLayer,
                 toggle_shop: Callable[[], None]):
        super().__init__(groups)
        # ASSETS.
        self.load_assets()
        self.status, self.frame_index = 'down_idle', 0
        # CORE.
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(center=place)
        self.z = LAYERS['main']
        # COLLISION.
        self.hitbox = self.rect.inflate(-126, -70)
        self.obstacles = group_obstacle
        # MOVEMENT.
        self.pos = pg.math.Vector2(self.rect.center)
        self.direction, self.speed = pg.math.Vector2(), 200
        # TIMER.
        self.timers = {
            'TOOL_USE': Timer(350, self.use_tool),
            'TOOL_SWITCH': Timer(200),
            'SEED_USE': Timer(350, self.use_seed),
            'SEED_SWITCH': Timer(200)
        }
        # TOOLS.
        self.tools = ['hoe', 'axe', 'water']
        self.tool_index = 0
        self.selected_tool = self.tools[self.tool_index]
        # SEEDS.
        self.seeds = ['corn', 'tomato']
        self.seed_index = 0
        self.selected_seed = self.seeds[self.seed_index]
        # INTERACTION GROUP & METHOD.
        self.trees = group_tree
        self.interactions = group_interaction
        self.soil_layer = soil_layer
        self.toggle_shop = toggle_shop
        # INVENTORY.
        self.inventory_item = {
            'wood': 5, 'apple': 5,
            'corn': 5, 'tomato': 5
        }
        self.inventory_seed = {
            'corn': 5, 'tomato': 5
        }
        self.money = 100
        # SLEEPING.
        self.is_sleeping = False
        # AUDIO.
        self.sound_water = pg.mixer.Sound('audio/water.mp3')
        self.sound_water.set_volume(0.2)

    def load_assets(self):
        self.animations: dict[str, list[pg.Surface]] = {
            'left': None, 'right': None, 'up': None, 'down': None,
            'left_hoe': None, 'right_hoe': None, 'up_hoe': None, 'down_hoe': None,
            'left_axe': None, 'right_axe': None, 'up_axe': None, 'down_axe': None,
            'left_idle': None, 'right_idle': None, 'up_idle': None, 'down_idle': None,
            'left_water': None, 'right_water': None, 'up_water': None, 'down_water': None
        }

        for status in self.animations.keys():
            self.animations[status] = load_image_list(
                f'image/character/{status}')

    def input(self):
        if not (self.timers['TOOL_USE'].is_actived or self.is_sleeping):
            keys = pg.key.get_pressed()
            # HORIZONTAL MOVEMENT.
            if keys[pg.K_LEFT]:
                self.direction.x = -1
                self.status = 'left'
            elif keys[pg.K_RIGHT]:
                self.direction.x = 1
                self.status = 'right'
            else:
                self.direction.x = 0
            # VERTICAL MOVEMENT.
            if keys[pg.K_UP]:
                self.direction.y = -1
                self.status = 'up'
            elif keys[pg.K_DOWN]:
                self.direction.y = 1
                self.status = 'down'
            else:
                self.direction.y = 0
            # USE TOOL.
            if keys[pg.K_SPACE]:
                self.timers['TOOL_USE'].activate()
                self.frame_index = 0
                self.direction = pg.math.Vector2()
            # SWITCH TOOL.
            if keys[pg.K_q] and not self.timers['TOOL_SWITCH'].is_actived:
                self.timers['TOOL_SWITCH'].activate()
                self.tool_index += 1
                # RESTART INDEX.
                if self.tool_index > len(self.tools) - 1:
                    self.tool_index = 0
                self.selected_tool = self.tools[self.tool_index]
            # USE SEED.
            if keys[pg.K_s] and not self.timers['SEED_USE'].is_actived:
                self.timers['SEED_USE'].activate()
                self.frame_index = 0
                self.direction = pg.math.Vector2()
            # SWITCH SEED.
            if keys[pg.K_e] and not self.timers['SEED_SWITCH'].is_actived:
                self.timers['SEED_SWITCH'].activate()
                self.seed_index += 1
                # RESTART INDEX.
                if self.seed_index > len(self.seeds) - 1:
                    self.seed_index = 0
                self.selected_seed = self.seeds[self.seed_index]
            # GO TO BED.
            if keys[pg.K_RETURN]:
                if collided_sprite := pg.sprite.spritecollide(self, self.interactions, False):
                    if collided_sprite[0].name == 'Bed':
                        self.status = 'left_idle'
                        self.is_sleeping = True
                    else:
                        self.toggle_shop()

    def get_status(self):
        if self.direction.magnitude() == 0:
            self.status = self.status.split('_')[0] + '_idle'
        if self.timers['TOOL_USE'].is_actived:
            self.status = self.status.split('_')[0] + f'_{self.selected_tool}'

    def move(self, delta_time: float):
        # DIOGINAL MOVEMENT.
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()
        # HORIZONTAL MOVEMENT.
        self.pos.x += self.direction.x * self.speed * delta_time
        self.hitbox.centerx = round(self.pos.x)
        self.rect.centerx = self.hitbox.centerx
        self.collide('horizontal')
        # VERTICAL MOVEMENT.
        self.pos.y += self.direction.y * self.speed * delta_time
        self.hitbox.centery = round(self.pos.y)
        self.rect.centery = self.hitbox.centery
        self.collide('vertical')

    def animate(self, delta_time: float):
        self.frame_index += 4 * delta_time

        if self.frame_index >= len(self.animations[self.status]):
            self.frame_index = 0

        self.image = self.animations[self.status][int(self.frame_index)]

    def cooldown(self):
        for timer in self.timers.values():
            timer.update()

    def collide(self, direction: str):
        for sprite in self.obstacles.sprites():
            if hasattr(sprite, 'hitbox'):
                if self.hitbox.colliderect(sprite.hitbox):
                    if direction == 'horizontal':
                        if self.direction.x < 0:
                            self.hitbox.left = sprite.hitbox.right
                        elif self.direction.x > 0:
                            self.hitbox.right = sprite.hitbox.left
                        self.rect.centerx = self.hitbox.centerx
                        self.pos.x = self.hitbox.centerx
                    else:
                        if self.direction.y < 0:
                            self.hitbox.top = sprite.hitbox.bottom
                        elif self.direction.y > 0:
                            self.hitbox.bottom = sprite.hitbox.top
                        self.rect.centery = self.hitbox.centery
                        self.pos.y = self.hitbox.centery

    def set_target_position(self):
        self.target_pos: tuple[int, int] = self.rect.center + \
            PLAYER_TOOL_OFFSET[self.status.split('_')[0]]

    def update(self, delta_time: float):
        self.input()
        self.get_status()
        self.move(delta_time)
        self.animate(delta_time)
        self.set_target_position()
        self.cooldown()

    def use_tool(self):
        match self.selected_tool:
            case 'hoe':
                self.soil_layer.excavate(self.target_pos)
            case 'water':
                self.soil_layer.irrigate(self.target_pos)
                self.sound_water.play()
            case 'axe':
                for tree in self.trees.sprites():
                    if tree.rect.collidepoint(self.target_pos):
                        tree.damage()

    def use_seed(self):
        if self.inventory_seed[self.selected_seed] > 0:
            self.soil_layer.plant_seed(self.target_pos, self.selected_seed)
            self.inventory_seed[self.selected_seed] -= 1
