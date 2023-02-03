from random import choice, randint

import pygame as pg
from enemy import Enemy
from magic import MagicController
from particle import AnimationController
from player import Player
from settings import *
from support import load_csv_layout, load_image_folder
from tile import Tile
from ui import UI
from upgrade import UpgradeController
from weapon import Weapon


class YSortCameraGroup(pg.sprite.Group):

    def __init__(self):
        super().__init__()
        # CORE.
        self.screen = pg.display.get_surface()
        self.bg = pg.image.load('image/tilemap/ground.png').convert()
        self.offset = pg.math.Vector2()

    def draws(self, player: Player):
        # GET THE OFFSET.
        self.offset.update(player.rect.centerx - WIDTH / 2,
                           player.rect.centery - HEIGTH / 2)
        # DRAW THE ENITY.
        self.screen.blit(self.bg, -self.offset)
        for sprite in sorted(self.sprites(), key=lambda e: e.rect.centery):
            offset_place = sprite.rect.topleft - self.offset
            self.screen.blit(sprite.image, offset_place)

    def update_enemy(self, player: Player):
        group_enemy: list[Enemy] = [sprite for sprite in self.sprites()
                                    if hasattr(sprite, 'form') and sprite.form == 'Enemy']
        for sprite in group_enemy:
            sprite.update_enemy(player)


class Level:

    def __init__(self):
        # CORE.
        self.screen = pg.display.get_surface()
        self.status = 'PLAY'
        # GROUP.
        self.group_visible = YSortCameraGroup()
        self.group_obstacle = pg.sprite.Group()
        self.group_attack = pg.sprite.Group()
        self.group_attackable = pg.sprite.Group()
        self.current_attack = None
        # SETUP.
        self.load_map()
        self.ui = UI()
        self.animation_controller = AnimationController()
        self.magic_controller = MagicController(self.animation_controller)
        self.upgrade_controller = UpgradeController(self.player)
        # AUDIO.
        pg.mixer.music.load('audio/main.ogg')
        pg.mixer.music.set_volume(0.5)
        pg.mixer.music.play(-1)

    def load_map(self):
        layouts = {
            'Boundary': load_csv_layout('data/map/map_FloorBlocks.csv'),
            'Grass': load_csv_layout('data/map/map_Grass.csv'),
            'Object': load_csv_layout('data/map/map_Objects.csv'),
            'Entity': load_csv_layout('data/map/map_Entities.csv')
        }

        images = {
            'Grass': load_image_folder('image/grass'),
            'Object': load_image_folder('image/objects')
        }

        for form, layout in layouts.items():
            for row_index, row in enumerate(layout):
                for col_index, col in enumerate(row):
                    if col != '-1':
                        place = col_index * TILESIZE, row_index * TILESIZE
                        match form:
                            case 'Boundary':
                                Tile(place, self.group_obstacle, 'Invisible')
                            case 'Grass':
                                Tile(place, (self.group_visible, self.group_obstacle, self.group_attackable),
                                     'Grass', choice(images['Grass']))
                            case 'Object':
                                Tile(place, (self.group_visible, self.group_obstacle),
                                     'Object', images['Object'][int(col)])
                            case 'Entity':
                                if col != '394':
                                    name = 'bamboo' if col == '390' else 'spirit' if col == '391' \
                                        else 'raccoon' if col == '392' else 'squid'
                                    Enemy(name, place, (self.group_visible, self.group_attackable),
                                          self.group_obstacle, self.damage_player, self.trigger_death_particle,
                                          self.add_exp)
                                else:
                                    self.player = Player(place, self.group_visible, self.group_obstacle,
                                                         self.create_attack, self.destroy_attack, self.create_magic)

    def create_attack(self):
        self.current_attack = Weapon(
            self.player, (self.group_visible, self.group_attack))

    def destroy_attack(self):
        if self.current_attack:
            self.current_attack.kill()
            self.current_attack = None

    def create_magic(self, form: str, strength: int, cost: int):
        if form == 'heal':
            self.magic_controller.heal(
                self.player, strength, cost, self.group_visible)
        else:
            self.magic_controller.flame(
                self.player, cost, (self.group_visible, self.group_attack))

    def damage_player(self, amount: int, form: str):
        if self.player.is_vulnerable:
            self.player.health -= amount

            # PARTICLE EFFECT.
            self.animation_controller.create_particles(
                self.player.rect.center, form, self.group_visible)

            self.player.is_vulnerable = False
            self.player.hurt_time = pg.time.get_ticks()

    def trigger_death_particle(self, place: tuple[int, int], form: str):
        self.animation_controller.create_particles(
            place, form, self.group_visible)

    def add_exp(self, amount: int):
        self.player.exp += amount

    def player_attack_logic(self):
        if self.group_attack:
            for attack_sprite in self.group_attack.sprites():
                attacked_sprites: list[Enemy | Tile] = pg.sprite.spritecollide(
                    attack_sprite, self.group_attackable, False)
                if attacked_sprites:
                    for attacked_sprite in attacked_sprites:
                        if attacked_sprite.form == 'Grass':
                            attacked_sprite.kill()

                            # PARTICLE EFFECT.
                            place = attacked_sprite.rect.center
                            offset = pg.math.Vector2(0, 75)
                            for _ in range(randint(3, 6)):
                                self.animation_controller.create_grass_particle(
                                    place - offset, self.group_visible)
                        else:
                            attacked_sprite.get_damage(
                                self.player, attack_sprite.form)

    def toggle_menu(self):
        if self.status == 'PLAY':
            self.status = 'PAUSE'
        elif self.status == 'PAUSE':
            self.status = 'PLAY'

    def check_death(self):
        enemies = [sprite for sprite in self.group_visible.sprites()
                   if hasattr(sprite, 'form') and sprite.form == 'Enemy']
        if self.status != 'LOST' and (self.player.health <= 0 or not enemies):
            self.status = 'LOST'
            self.load_bye()

    def load_bye(self):
        self.font = pg.font.Font('font/joystix.ttf', 30)
        self.bye_surfs = [self.font.render(text, False, 'WHITE') for text in
                          ('THANK YOU FOR PLAYING!', 'CREATE BY BIN BIN', 'GUIDE BY CHRISTIAN KOCH')]
        self.bye_rects = [surf.get_rect() for surf in self.bye_surfs]

        for index, rect in enumerate(self.bye_rects):
            if index != 0:
                offset = pg.math.Vector2(0, 20)
                rect.midtop = self.bye_rects[index - 1].midbottom + offset
            else:
                rect.midtop = self.screen.get_rect().midbottom

    def good_bye(self):
        # DRAW.
        for surf, rect in zip(self.bye_surfs, self.bye_rects):
            self.screen.blit(surf, rect)
        # UPDATE.
        for rect in self.bye_rects:
            rect.y -= 1
        # END.
        if self.bye_rects[-1].bottom < 0:
            pg.quit()
            exit()

    def run(self):
        match self.status:
            case 'PLAY' | 'PAUSE':
                self.group_visible.draws(self.player)
                self.ui.display(self.player)
                if self.status == 'PLAY':
                    self.group_visible.update()
                    self.group_visible.update_enemy(self.player)
                    self.player_attack_logic()
                else:
                    self.upgrade_controller.display()
            case 'LOST':
                self.screen.fill('BLACK')
                self.good_bye()

        self.check_death()
