from collections.abc import Callable

import pygame as pg
from asset import LEVELS
from decoration import *
from enemy import Enemy
from particle import ParticleEffect
from player import Player
from settings import TILE_SIZE
from support import crop_image, load_csv_file
from tiles import Coin, Crate, Palm, StaticTile, Tile


class Level:

    def __init__(self, level: int, load_overworld: Callable[[int, int], None],
                 update_coins: Callable[[int], None], update_health: Callable[[int], None]):
        # CORE.
        self.screen = pg.display.get_surface()
        self.world_shift = 0
        DATA = LEVELS[level]
        # OVERWORLD CONNECTION.
        self.load_overworld = load_overworld
        self.update_coins = update_coins
        self.current_level = level
        self.unlocked_level = DATA['UNLOCK']
        # PLAYER.
        layout_player = load_csv_file(DATA['Player'])
        self.player = pg.sprite.GroupSingle()
        self.goal = pg.sprite.GroupSingle()
        self.load_player_group(layout_player, update_health)
        # JUMP & LAND PARTICLE.
        self.group_dust = pg.sprite.GroupSingle()
        # EXPLOSION PARTICLE.
        self.group_explosion = pg.sprite.Group()
        # TERRAIN SETUP.
        layout_terrain = load_csv_file(DATA['Terrain'])
        self.group_terrain = self.load_tile_group(layout_terrain, 'Terrain')
        # GRASS SETUP.
        layout_grass = load_csv_file(DATA['Grass'])
        self.group_grass = self.load_tile_group(layout_grass, 'Grass')
        # CRATE SETUP.
        layout_crate = load_csv_file(DATA['Crates'])
        self.group_crate = self.load_tile_group(layout_crate, 'Crates')
        # COIN SETUP.
        layout_coin = load_csv_file(DATA['Coins'])
        self.group_coin = self.load_tile_group(layout_coin, 'Coins')
        # FOREGROUND PALM SETUP.
        layout_fg_palm = load_csv_file(DATA['FG_Palms'])
        self.group_fg_palm = self.load_tile_group(layout_fg_palm, 'FG_Palms')
        # BACKGROUND PALM SETUP.
        layout_bg_palm = load_csv_file(DATA['BG_Palms'])
        self.group_bg_palm = self.load_tile_group(layout_bg_palm, 'BG_Palms')
        # ENEMY.
        layout_enemy = load_csv_file(DATA['Enemies'])
        self.group_enemy = self.load_tile_group(layout_enemy, 'Enemies')
        # CONSTRAINT.
        layout_constraint = load_csv_file(DATA['Constraints'])
        self.group_constraint = self.load_tile_group(
            layout_constraint, 'Constraints')
        # DECORATION.
        self.sky = Sky()
        level_width = len(layout_terrain[0]) * TILE_SIZE
        self.water = Water(level_width)
        self.cloud = Cloud(level_width, 30)
        # SOUND EFFECT.
        self.sound_coin = pg.mixer.Sound('audio/effects/coin.wav')
        self.sound_stomp = pg.mixer.Sound('audio/effects/stomp.wav')

    def scroll(self):
        '''Scroll screen.'''
        # INFORMATION.
        player: Player = self.player.sprite
        x_pos, x_dir = player.rect.centerx, player.direction.x
        # CHECK.
        if x_pos < SCREEN_WIDTH / 4 and x_dir < 0:
            self.world_shift = 8
            player.MOVE_SPEED = 0
        elif x_pos > SCREEN_WIDTH - SCREEN_WIDTH / 4 and x_dir > 0:
            self.world_shift = -8
            player.MOVE_SPEED = 0
        else:
            self.world_shift = 0
            player.MOVE_SPEED = 8

    def load_tile_group(self, layout: list[list[str]], form: str):
        tiles = pg.sprite.Group()
        # LOAD TILE IMAGE.
        match form:
            case 'Terrain':
                images = crop_image('image/terrain/terrain_tiles.png')
            case 'Grass':
                images = crop_image('image/decoration/grass/grass.png')
        # LOAD TILE IMAGE TO GROUP.
        for row_index, row in enumerate(layout):
            for col_index, col in enumerate(row):
                if col != '-1':
                    place = col_index * TILE_SIZE, row_index * TILE_SIZE
                    match form:
                        case 'Terrain':
                            image = images[int(col)]
                            tiles.add(StaticTile(TILE_SIZE, place, image))
                        case 'Grass':
                            image = images[int(col)]
                            tiles.add(StaticTile(TILE_SIZE, place, image))
                        case 'Crates':
                            tiles.add(Crate(TILE_SIZE, place))
                        case 'Coins':
                            if col == '0':
                                path, value = 'image/coins/gold', 5
                            else:
                                path, value = 'image/coins/silver', 1
                            tiles.add(Coin(TILE_SIZE, place, path, value))
                        case 'FG_Palms':
                            if col == '1':
                                path, offset = 'image/terrain/palm_small', 40
                            else:
                                path, offset = 'image/terrain/palm_large', 70
                            tiles.add(Palm(TILE_SIZE, place, path, offset))
                        case 'BG_Palms':
                            path = 'image/terrain/palm_bg'
                            tiles.add(Palm(TILE_SIZE, place, path, 60))
                        case 'Enemies':
                            tiles.add(Enemy(TILE_SIZE, place))
                        case 'Constraints':
                            tiles.add(Tile(TILE_SIZE, place))
        return tiles

    def load_player_group(self, layout: list[list[str]], update_health: Callable[[int], None]):
        for row_index, row in enumerate(layout):
            for col_index, col in enumerate(row):
                if col != '-1':
                    place = col_index * TILE_SIZE, row_index * TILE_SIZE
                    if col == '0':
                        self.player.add(
                            Player(place, self.load_jump_effect, update_health))
                    else:
                        image = pg.image.load(
                            'image/character/hat.png').convert_alpha()
                        self.goal.add(StaticTile(TILE_SIZE, place, image))

    def reverse_enemy(self):
        for enemy in self.group_enemy.sprites():
            if pg.sprite.spritecollide(enemy, self.group_constraint, False):
                enemy.reverse()

    def load_jump_effect(self):
        place = self.player.sprite.rect.midbottom + \
            pg.math.Vector2((-10 * self.player.sprite.facing_right, -5))
        self.group_dust.add(ParticleEffect(place, 'jump'))

    def load_land_effect(self):
        place = self.player.sprite.rect.midbottom + \
            pg.math.Vector2((-10 * self.player.sprite.facing_right, -15))
        self.group_dust.add(ParticleEffect(place, 'land'))

    def check_win(self):
        if pg.sprite.spritecollide(self.player.sprite, self.goal, False):
            self.load_overworld(self.current_level, self.unlocked_level)

    def check_lose(self):
        if self.player.sprite.rect.top > SCREEN_HEIGHT:
            self.load_overworld(self.current_level, 0)

    def run(self):
        # DECORATION.
        self.sky.draw()
        self.cloud.draw(self.world_shift)
        # BACKGROUND PALM.
        self.group_bg_palm.update(self.world_shift)
        self.group_bg_palm.draw(self.screen)
        # PLAYER PARTICLE.
        self.group_dust.update(self.world_shift)
        self.group_dust.draw(self.screen)
        # TERRAIN.
        self.group_terrain.update(self.world_shift)
        self.group_terrain.draw(self.screen)
        # ENEMY.
        self.group_enemy.update(self.world_shift)
        self.group_constraint.update(self.world_shift)
        self.reverse_enemy()
        self.group_enemy.draw(self.screen)
        # ENEMY PARTICLE.
        self.group_explosion.update(self.world_shift)
        self.group_explosion.draw(self.screen)
        # CRATE.
        self.group_crate.update(self.world_shift)
        self.group_crate.draw(self.screen)
        # GRASS.
        self.group_grass.update(self.world_shift)
        self.group_grass.draw(self.screen)
        # COIN.
        self.group_coin.update(self.world_shift)
        self.group_coin.draw(self.screen)
        # FOREGROUND PALM.
        self.group_fg_palm.update(self.world_shift)
        self.group_fg_palm.draw(self.screen)
        # PLAYER.
        self.player.update()
        # COLLISION.
        self.collide_horizontally()
        self.collide_vertically()
        self.collide_coins()
        self.collide_enemies()
        # CAMERA.
        self.scroll()
        self.player.draw(self.screen)
        self.goal.update(self.world_shift)
        self.goal.draw(self.screen)
        # CHECK WIN & LOSE.
        self.check_win()
        self.check_lose()
        # WATER DECORATION.
        self.water.draw(self.world_shift)

    def collide_horizontally(self):
        player: Player = self.player.sprite
        player.move()
        collidable_groups = self.group_terrain.sprites() + self.group_crate.sprites() + \
            self.group_fg_palm.sprites()
        for sprite in collidable_groups:
            if sprite.rect.colliderect(player.hitbox):
                if player.direction.x < 0:
                    player.hitbox.left = sprite.rect.right
                    self.colliding_x = sprite.rect.right
                elif player.direction.x > 0:
                    player.hitbox.right = sprite.rect.left
                    self.colliding_x = sprite.rect.left

    def collide_vertically(self):
        player: Player = self.player.sprite
        player.fall()
        # CHECK ON GROUND BEFORE UPDATE.
        player_on_ground = player.on_ground
        # CHECK COLLISION.
        collidable_groups = self.group_terrain.sprites() + self.group_crate.sprites() + \
            self.group_fg_palm.sprites()
        for sprite in collidable_groups:
            if sprite.rect.colliderect(player.hitbox):
                if player.direction.y > 0:
                    player.hitbox.bottom = sprite.rect.top
                    # PLAYER IS ON THE GROUND.
                    player.on_ground = True
                elif player.direction.y < 0:
                    player.hitbox.top = sprite.rect.bottom
                player.direction.y = 0
        # CHECK STATUS.
        if player.on_ground and player.direction.y < 0 or player.direction.y > 1:
            player.on_ground = False
        # LAND PARTICLE.
        if not player_on_ground and player.on_ground and not self.group_dust.sprites():
            self.load_land_effect()

    def collide_coins(self):
        # INFORMATION.
        coins: list[Coin] = pg.sprite.spritecollide(
            self.player.sprite, self.group_coin, True)
        # CALCULATE.
        if coins:
            self.sound_coin.play()
            for coin in coins:
                self.update_coins(coin.value)

    def collide_enemies(self):
        player: Player = self.player.sprite
        enemies = pg.sprite.spritecollide(player, self.group_enemy, False)
        if enemies:
            for enemy in enemies:
                enemy_center, enemy_top = enemy.rect.centery, enemy.rect.top
                player_bottom = player.hitbox.bottom
                if enemy_top < player_bottom < enemy_center and player.direction.y >= 0:
                    self.sound_stomp.play()
                    player.jump()
                    self.group_explosion.add(ParticleEffect(
                        enemy.rect.center, 'group_explosion'))

                    enemy.kill()
                else:
                    player.get_damage()
