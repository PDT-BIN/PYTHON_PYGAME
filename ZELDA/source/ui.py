import pygame as pg
from player import Player
from settings import *


class UI:

    def __init__(self):
        # CORE.
        self.screen = pg.display.get_surface()
        self.font = pg.font.Font(UI_FONT, UI_FONT_SIZE)

        # BAR SETUP.
        self.health_bar_rect = pg.Rect(10, 10, HEALTH_BAR_WIDTH, BAR_HEIGHT)
        self.energy_bar_rect = pg.Rect(10, 35, ENERGY_BAR_WIDTH, BAR_HEIGHT)
        # ATTACK GRAPHIC.
        self.weapon_graphics = [pg.image.load(datum['Graphic']).convert_alpha()
                                for datum in WEAPON_DATA.values()]
        self.magic_graphics = [pg.image.load(datum['Graphic']).convert_alpha()
                               for datum in MAGIC_DATA.values()]

    def draw_bar(self, current: int, maximum: int, bg_rect: pg.Rect, color: str):
        # DRAW BG.
        pg.draw.rect(self.screen, UI_BG_COLOR, bg_rect)

        # CONVERT STAT INTO PIXEL.
        current_rect = bg_rect.copy()
        current_rect.width = current * bg_rect.width / maximum

        # DRAW BAR.
        pg.draw.rect(self.screen, color, current_rect)
        pg.draw.rect(self.screen, UI_BORDER_COLOR, bg_rect, 3)

    def draw_exp(self, exp: int):
        # INFORMATION.
        text_surf = self.font.render(str(int(exp)), False, TEXT_COLOR)
        text_rect = text_surf.get_rect(bottomright=(WIDTH - 20, HEIGTH - 20))
        bg_rect = text_rect.inflate(20, 20)

        # DRAW.
        pg.draw.rect(self.screen, UI_BG_COLOR, bg_rect)
        self.screen.blit(text_surf, text_rect)
        pg.draw.rect(self.screen, UI_BORDER_COLOR, bg_rect, 3)

    def draw_option_box(self, place: tuple[int, int], is_switching: bool):
        # INFORMATION.
        bg_rect = pg.Rect(place, (ITEM_BOX_SIZE, ITEM_BOX_SIZE))
        boder_color = UI_BORDER_COLOR if is_switching else UI_BORDER_COLOR_ACTIVE

        # DRAW.
        pg.draw.rect(self.screen, UI_BG_COLOR, bg_rect)
        pg.draw.rect(self.screen, boder_color, bg_rect, 3)

        return bg_rect

    def overlay_weapon(self, index: int, is_switching: bool):
        # INFORMATION.
        bg_rect = self.draw_option_box((10, 630), is_switching)
        weapon_surf = self.weapon_graphics[index]
        weapon_rect = weapon_surf.get_rect(center=bg_rect.center)

        # DRAW.
        self.screen.blit(weapon_surf, weapon_rect)

    def overlay_magic(self, index: int, is_switching: bool):
        # INFORMATION.
        bg_rect = self.draw_option_box((80, 635), is_switching)
        magic_surf = self.magic_graphics[index]
        magic_rect = magic_surf.get_rect(center=bg_rect.center)

        # DRAW.
        self.screen.blit(magic_surf, magic_rect)

    def display(self, player: Player):
        self.draw_bar(
            player.health, player.stats['Health'], self.health_bar_rect, HEALTH_COLOR)
        self.draw_bar(
            player.energy, player.stats['Energy'], self.energy_bar_rect, ENERGY_COLOR)
        self.draw_exp(player.exp)
        self.overlay_weapon(player.weapon_index, player.can_switch_weapon)
        self.overlay_magic(player.magic_index, player.can_switch_magic)
