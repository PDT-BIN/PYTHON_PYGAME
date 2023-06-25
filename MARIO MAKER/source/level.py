from collections.abc import Callable, Sequence
from random import choice, randint
from sys import exit

import pygame as pg
from pygame.math import Vector2 as Vector
from pygame.sprite import Group
from settings import *
from sprites import (Animate, Block, Cloud, Coin, Generic, Particle, Player,
                     Shell, Spike, Tooth)
from supports import *


class Level:
    def __init__(self, layers: dict[str, dict[tuple[int, int], str | int]],
                 switch: Callable[[dict[str, dict] | None], None], assets: Sequence[Surface] | Surface,
                 sounds: dict[str, pg.mixer.Sound]):
        self.screen = pg.display.get_surface()
        self.switch = switch
        # RESOURCES.
        self.coin_particle = assets['particle']
        self.cloud_surfs = assets['clouds']
        # GROUP.
        self.all_sprites = CameraGroup()
        self.coin_sprites = Group()
        self.damage_sprites = Group()
        self.collidable_sprites = Group()
        self.shell_sprites = Group()
        # START-UP.
        self.build_level(layers, assets, sounds['jump'])
        self.cloud_timer = pg.USEREVENT + 2
        pg.time.set_timer(self.cloud_timer, 2000)
        # LEVEL LIMIT.
        self.level_limit = {
            'left': -WINDOW_WIDTH // 2,
            'right': max(list(layers['terrain'].keys()), key=lambda pos: pos[0], default=(0, 0))[0] + 500
        }
        self.startup_clouds()
        # MUSIC & SOUND.
        self.music = sounds['music']
        self.music.set_volume(0.4)
        self.music.play(loops=-1)
        self.coin_sound = sounds['coin']
        self.coin_sound.set_volume(0.3)
        self.jump_sound = sounds['jump']
        self.jump_sound.set_volume(0.3)
        self.hit_sound = sounds['hit']
        self.hit_sound.set_volume(0.3)
        # MISSION.
        self.heart_surf = assets['heart']
        self.create_hearts()
        self.font = pg.font.SysFont('VERDANA', 16, True)
        self.complete_surf = assets['complete']
        self.success_surf = assets['success']
        self.success_rect = self.success_surf.get_rect(
            center=self.screen.get_rect().center)
        self.fail_surf = assets['fail']
        self.fail_rect = self.fail_surf.get_rect(
            center=self.screen.get_rect().center)

    def build_level(self, layers: dict[str, dict[tuple[int, int], str | int]],
                    assets: Sequence[Surface] | Surface, jump_sound: pg.mixer.Sound):
        for layer_name, layer_data in layers.items():
            for pos, data in layer_data.items():
                if layer_name == 'terrain':
                    Generic((self.all_sprites, self.collidable_sprites),
                            assets['land'][data], pos)
                elif layer_name == 'water':
                    if data == 'top':
                        Animate(self.all_sprites,
                                assets['water_top'], pos, LEVEL_LAYERS['water'])
                    else:
                        Generic(self.all_sprites,
                                assets['water_bot'], pos, LEVEL_LAYERS['water'])
                else:
                    match data:
                        case 0:
                            self.player = Player(
                                self.all_sprites, assets['player'], pos, self.collidable_sprites, jump_sound)
                        case 1: self.sky_line = self.all_sprites.sky_line = pos[1]
                        case 4: Coin((self.all_sprites, self.coin_sprites), assets['gold'], pos, 'gold')
                        case 5: Coin((self.all_sprites, self.coin_sprites), assets['silver'], pos, 'silver')
                        case 6: Coin((self.all_sprites, self.coin_sprites), assets['diamond'], pos, 'diamond')
                        case 7: Spike((self.all_sprites, self.damage_sprites), assets['spike'], pos)
                        case 8:
                            Tooth((self.all_sprites, self.damage_sprites),
                                  assets['tooth'], pos, self.collidable_sprites)
                        case 9:
                            Shell((self.all_sprites, self.collidable_sprites, self.shell_sprites),
                                  assets['shell'], pos, 'left', assets['pearl'], self.damage_sprites)
                        case 10:
                            Shell((self.all_sprites, self.collidable_sprites, self.shell_sprites),
                                  assets['shell'], pos, 'right', assets['pearl'], self.damage_sprites)
                        case 11:
                            Animate(self.all_sprites,
                                    assets['palms']['small_fg'], pos)
                            Block(self.collidable_sprites,
                                  (46, 50), pos + Vector(17, 0))
                        case 12:
                            Animate(self.all_sprites,
                                    assets['palms']['large_fg'], pos)
                            Block(self.collidable_sprites,
                                  (46, 50), pos + Vector(17, 0))
                        case 13:
                            Animate(self.all_sprites,
                                    assets['palms']['left_fg'], pos)
                            Block(self.collidable_sprites,
                                  (46, 50), pos + Vector(17, 0))
                        case 14:
                            Animate(self.all_sprites,
                                    assets['palms']['right_fg'], pos)
                            Block(self.collidable_sprites,
                                  (46, 50), pos + Vector(67, 0))
                        case 15: Animate(self.all_sprites, assets['palms']['small_bg'], pos, LEVEL_LAYERS['bg'])
                        case 16: Animate(self.all_sprites, assets['palms']['large_bg'], pos, LEVEL_LAYERS['bg'])
                        case 17: Animate(self.all_sprites, assets['palms']['left_bg'], pos, LEVEL_LAYERS['bg'])
                        case 18: Animate(self.all_sprites, assets['palms']['right_bg'], pos, LEVEL_LAYERS['bg'])
        # LINK THE PLAYER TO SHELL.
        for sprite in self.shell_sprites:
            setattr(sprite, 'player', self.player)
        # CREATE MISSION.
        self.create_mission(assets)

    def create_mission(self, assets: Sequence[Surface] | Surface):
        # CREATE MISSION. {'type': [('Surface', 'Rect', 'Text Postition'), 'quantity', 'achieved']}
        self.missions: dict[str, list] = {}
        for index, name in enumerate(('silver', 'gold', 'diamond')):
            surf: Surface = assets[name][0]
            offset = WINDOW_WIDTH - 2 * TILE_SIZE, index * TILE_SIZE
            rect = surf.get_rect(center=Vector(offset) + COIN_OFFSET)
            text_pos = Vector(rect.center) + TEXT_OFFSET
            self.missions[name] = [(surf, rect, text_pos), 0, 0]
        # GET MISSION.
        for sprite in self.coin_sprites:
            self.missions[sprite.coin_type][1] += 1

    def create_hearts(self):
        self.hearts = []
        for index in range(3):
            offset = Vector(index * TILE_SIZE, 0) + COIN_OFFSET
            rect = self.heart_surf.get_rect(center=offset)
            self.hearts.append(rect)

    def event_loop(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                exit()
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                self.switch()
                self.music.stop()
            if event.type == self.cloud_timer:
                x = self.level_limit['right'] + randint(100, 300)
                y = self.sky_line - randint(-25, 600)
                self.create_cloud(choice(self.cloud_surfs), (x, y))

    def check_collision(self):
        # BETWEEEN PLAYER & COIN SPRITES.
        for sprite in pg.sprite.spritecollide(self.player, self.coin_sprites, True):
            self.missions[sprite.coin_type][2] += 1
            self.coin_sound.play()
            Particle(self.all_sprites, self.coin_particle, sprite.rect.center)
        # BETWEEN PLAYER & DAMAGE SPRITES.
        for sprite in self.damage_sprites:
            if pg.sprite.spritecollide(self.player, self.damage_sprites, False, pg.sprite.collide_mask):
                if self.player.get_damage():
                    self.hit_sound.play()
                    self.hearts.pop()

    def startup_clouds(self):
        for _ in range(15):
            x = randint(self.level_limit['left'], self.level_limit['right'])
            y = self.sky_line - randint(-25, 600)
            self.create_cloud(choice(self.cloud_surfs), (x, y))

    def create_cloud(self, surface: Surface, position: tuple[int, int]):
        Cloud(self.all_sprites, pg.transform.scale2x(surface) if randint(0, 5) > 3 else surface,
              position, self.level_limit['left'])

    def draw_missions(self):
        for mission in self.missions.values():
            self.screen.blit(mission[0][0], mission[0][1])
            surf = self.complete_surf if mission[1] == mission[2] else self.font.render(
                f'{mission[2]} / {mission[1]}', True, 'BLACK').convert_alpha()
            rect = surf.get_rect(center=mission[0][2])
            self.screen.blit(surf, rect)

    def draw_hearts(self):
        for rect in self.hearts:
            self.screen.blit(self.heart_surf, rect)

    def check_finish(self):
        if not hasattr(self, 'finish'):
            # CHECK FAIL.
            if len(self.hearts) == 0 or self.check_cliff():
                self.finish = [(self.fail_surf, self.fail_rect)]
            else:
                # CHECK SUCCESS.
                for mission in self.missions.values():
                    if mission[1] != mission[2]:
                        break
                else:
                    font = pg.font.SysFont('chalkdusterttf', 32)
                    state = self.success_surf, self.success_rect
                    result = (surface := pg.transform.rotate(pg.transform.scale2x(font.render(
                        'MISSION COMPLETE!', True, 'ROYALBLUE')), 25).convert_alpha(),
                        surface.get_rect(center=self.screen.get_rect().center))
                    self.finish = [state, result]

    def check_cliff(self):
        for sprite in self.collidable_sprites:
            if self.player.rect.top <= sprite.rect.bottom:
                return False
        return True

    def draw_finish(self):
        if hasattr(self, 'finish'):
            self.screen.blits(self.finish)

    def run(self, delta_time: float):
        # EVENTS.
        self.event_loop()
        if not hasattr(self, 'finish'):
            self.check_collision()
            self.check_finish()
            # UPDATE.
            self.all_sprites.update(delta_time)
        # DRAW.
        self.all_sprites.draw(self.player)
        self.draw_missions()
        self.draw_hearts()
        self.draw_finish()


class CameraGroup(Group):
    def __init__(self):
        super().__init__()
        # PERSONAL.
        self.screen = pg.display.get_surface()
        self.offset = Vector()
        self.sky_line: int

    def draw_sky(self):
        # DRAW SKY BACKGROUND.
        self.screen.fill(SKY_COLOR)
        if (sky_pos := self.sky_line - self.offset.y) < WINDOW_HEIGHT:
            # DRAW SEA BACKGROUND.
            pg.draw.rect(self.screen, SEA_COLOR, pg.Rect(
                0, sky_pos, WINDOW_WIDTH, WINDOW_HEIGHT - sky_pos))
            # DRAW SKY LINE.
            sky_rect_bot = pg.Rect(0, sky_pos - 10, WINDOW_WIDTH, 10)
            sky_rect_mid = pg.Rect(0, sky_pos - 16, WINDOW_WIDTH, 4)
            sky_rect_top = pg.Rect(0, sky_pos - 20, WINDOW_WIDTH, 2)
            pg.draw.rect(self.screen, HORIZON_TOP_COLOR, sky_rect_bot)
            pg.draw.rect(self.screen, HORIZON_TOP_COLOR, sky_rect_mid)
            pg.draw.rect(self.screen, HORIZON_TOP_COLOR, sky_rect_top)
            # DRAW HORIZONTAL LINE.
            pg.draw.line(self.screen, HORIZON_COLOR,
                         (0, sky_pos), (WINDOW_WIDTH, sky_pos), 3)
        # FULL OF SEA.
        if sky_pos < 0:
            self.screen.fill(SEA_COLOR)

    def draw(self, player: Player):
        # CALCULATE OFFSET.
        self.offset = Vector(player.rect.centerx - WINDOW_WIDTH // 2,
                             player.rect.centery - WINDOW_HEIGHT // 2)
        # DRAW.
        self.draw_sky()
        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.z):
            offset_rect = sprite.rect.copy()
            offset_rect.center -= self.offset
            self.screen.blit(sprite.image, offset_rect)
