from random import randint

import pygame as pg
from overlay import Overlay
from player import Player
from pytmx.util_pygame import load_pygame
from settings import *
from shop import Shop
from sky import Rain, Sky
from soil import SoilLayer
from sprites import Generic, Interaction, Particle, Tree, Water, WildFlower
from supports import *
from transistion import Transistion


class CameraGroup(pg.sprite.Group):

    def __init__(self):
        super().__init__()
        # CORE.
        self.screen = pg.display.get_surface()
        self.offset = pg.math.Vector2()

    def draws(self, player: Player):
        # UPDATE OFFSET.
        self.offset.update(player.rect.centerx - SCREEN_WIDTH / 2,
                           player.rect.centery - SCREEN_HEIGHT / 2)
        # DRAW.
        for sprite in sorted(self.sprites(), key=lambda e: (e.z, e.rect.centery)):
            offset_rect = sprite.rect.copy()
            offset_rect.center -= self.offset
            self.screen.blit(sprite.image, offset_rect)


class Level:

    def __init__(self):
        # CORE.
        self.screen = pg.display.get_surface()
        # GROUP.
        self.all_sprites = CameraGroup()
        self.group_obstacle = pg.sprite.Group()
        self.group_tree = pg.sprite.Group()
        self.group_interaction = pg.sprite.Group()
        # LAND.
        self.soil_layer = SoilLayer(self.all_sprites, self.group_obstacle)
        # WEATHER.
        self.rain = Rain(self.all_sprites)
        self.is_raining = randint(0, 10) > 7
        # DAYTIME.
        self.sky = Sky()
        # ENTITY.
        self.load_data()
        # SYSTEM.
        self.overlay = Overlay(self.player)
        self.transistion = Transistion(self.player, self.reset)
        # SHOP.
        self.shop_active = False
        self.shop = Shop(self.player, self.toggle_shop)
        # AUDIO.
        self.sound_success = pg.mixer.Sound('audio/success.wav')
        self.sound_success.set_volume(0.3)
        # MUSIC.
        pg.mixer.music.load('audio/music.mp3')
        pg.mixer.music.set_volume(0.5)
        pg.mixer.music.play(-1)

    def load_data(self):
        data = load_pygame('data/map.tmx')
        # BACKGROUND.
        Generic((0, 0), pg.image.load(
            'image/world/ground.png').convert_alpha(), self.all_sprites, LAYERS['ground'])
        # HOUSE.
        for layer in ('HouseFloor', 'HouseFurnitureBottom'):
            for x, y, image in data.get_layer_by_name(layer).tiles():
                Generic((x * TILE_SIZE, y * TILE_SIZE), image,
                        self.all_sprites, LAYERS['house bottom'])
        for layer in ('HouseWalls', 'HouseFurnitureTop'):
            for x, y, image in data.get_layer_by_name(layer).tiles():
                Generic((x * TILE_SIZE, y * TILE_SIZE),
                        image, self.all_sprites)
        # FENCE.
        for x, y, image in data.get_layer_by_name('Fence').tiles():
            Generic((x * TILE_SIZE, y * TILE_SIZE), image,
                    (self.all_sprites, self.group_obstacle))
        # WATER. (ANIMATING)
        animations_water = load_image_list('image/water')
        for x, y, image in data.get_layer_by_name('Water').tiles():
            Water((x * TILE_SIZE, y * TILE_SIZE),
                  animations_water, self.all_sprites)
        # WILDFLOWER. (OBJECT)
        for obj in data.get_layer_by_name('Decoration'):
            WildFlower((obj.x, obj.y), obj.image,
                       (self.all_sprites, self.group_obstacle))
        # TREE. (OBJECT)
        for obj in data.get_layer_by_name('Trees'):
            Tree((obj.x, obj.y), obj.image, (self.all_sprites,
                 self.group_obstacle, self.group_tree), obj.name,
                 self.add_item_to_player)
        # CONSTRAINT TILE.
        for x, y, image in data.get_layer_by_name('Collision').tiles():
            Generic((x * TILE_SIZE, y * TILE_SIZE),
                    image, self.group_obstacle)
        # PLAYER.
        for obj in data.get_layer_by_name('Player'):
            match obj.name:
                case 'Start':
                    self.player = Player((obj.x, obj.y), self.all_sprites, self.group_obstacle,
                                         self.group_tree, self.group_interaction, self.soil_layer, self.toggle_shop)
                case 'Bed':
                    Interaction((obj.x, obj.y), pg.Surface(
                        (obj.width, obj.height)), self.group_interaction, obj.name)
                case 'Trader':
                    Interaction((obj.x, obj.y), pg.Surface(
                        (obj.width, obj.height)), self.group_interaction, obj.name)

    def add_item_to_player(self, item: str):
        self.player.inventory_item[item] += 1
        self.sound_success.play()

    def reset(self):
        # GROWING PLANTS.
        self.soil_layer.update_plants()
        # RENEW APPLES IN THE TREES.
        for tree in self.group_tree.sprites():
            if tree.is_alive:
                tree.group_apple.empty()
                tree.spawn_apples()
        # REMOVE WATER IN THE SOILS.
        self.soil_layer.remove_water_tile()
        # CREATE RAIN RANDOMLY.
        self.is_raining = randint(0, 10) > 7
        # START A NEW DAY.
        self.sky.color_day = [255, 255, 255]

    def check_plant_harvest(self):
        for plant in self.soil_layer.group_plant.sprites():
            if plant.is_harvestable and plant.rect.colliderect(self.player.hitbox):
                self.add_item_to_player(plant.seed_type)
                Particle(plant.rect.topleft, plant.image,
                         self.all_sprites, LAYERS['main'])
                self.soil_layer.grid[plant.rect.centery //
                                     TILE_SIZE][plant.rect.centerx // TILE_SIZE].remove('P')
                plant.kill()

    def toggle_shop(self):
        self.shop_active = not self.shop_active

    def run(self, delta_time: float):
        # DRAW.
        self.all_sprites.draws(self.player)
        # UPDATE LOGIC.
        if not self.shop_active:
            # ACTIVITY.
            self.all_sprites.update(delta_time)
            self.check_plant_harvest()
            # WEATHER.
            if self.is_raining:
                self.rain.update()
                self.soil_layer.irrigate_by_rain()
        else:
            self.shop.update()
        # DISPLAY USED TOOL & SEED.
        self.overlay.display()
        # DAYTIME.
        self.sky.display(delta_time)
        # RESET.
        if self.player.is_sleeping:
            self.transistion.play()
