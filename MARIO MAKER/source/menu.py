from collections.abc import Sequence

import pygame as pg
from pygame import Surface
from pygame.sprite import AbstractGroup
from settings import *
from supports import load_an_image


class Menu:
    def __init__(self):
        self.screen = pg.display.get_surface()
        self.upload_data()
        self.create_menu()

    def upload_data(self):
        self.menu_surfs: dict[str, list[Surface]] = {}
        for item_key, value in EDITOR_DATA.items():
            if menu_key := value['menu']:
                if menu_key in self.menu_surfs:
                    self.menu_surfs[menu_key].append(
                        (item_key, load_an_image(value['menu_surf'])))
                else:
                    self.menu_surfs[menu_key] = [
                        (item_key, load_an_image(value['menu_surf']))]

    def create_menu(self):
        # MENU AREA.
        size, margin = 180, 6
        pos = WINDOW_WIDTH - size - margin, WINDOW_HEIGHT - size - margin
        self.rect = pg.Rect(pos, (size, size))
        # BUTTON AREA.
        size, margin = size / 2, margin - 1
        generic_rect = pg.Rect(pos, (size, size)).inflate(-margin, -margin)
        self.tile_button_rect = generic_rect.copy()
        self.coin_button_rect = generic_rect.move(size, 0)
        self.palm_button_rect = generic_rect.move(0, size)
        self.enemy_button_rect = generic_rect.move(size, size)
        # BUTTON GROUP.
        self.buttons: Sequence[Button] = pg.sprite.Group()
        Button(self.buttons, self.tile_button_rect, self.menu_surfs['terrain'])
        Button(self.buttons, self.coin_button_rect, self.menu_surfs['coin'])
        Button(self.buttons, self.palm_button_rect,
               self.menu_surfs['palm fg'], self.menu_surfs['palm bg'])
        Button(self.buttons, self.enemy_button_rect, self.menu_surfs['enemy'])

    def click(self, mouse_pos: tuple[int, int], mouse_button: tuple[int, int, int]) -> int | None:
        for sprite in self.buttons:
            if sprite.rect.collidepoint(mouse_pos):
                # MIDDLE CLICK: SWITCH BETWEEEN 'MAIN' & 'ALT' MODE.
                if mouse_button[1] and sprite.items['alt']:
                    sprite.main_active = not sprite.main_active
                # RIGHT CLICK: SWITCH ITEM.
                if mouse_button[2]:
                    sprite.switch()
                return sprite.get_id()

    def highlight(self, index: int):
        match EDITOR_DATA[index]['menu']:
            case 'terrain':
                pg.draw.rect(self.screen, BUTTON_LINE_COLOR,
                             self.tile_button_rect.inflate(4, 4), 5, 4)
            case 'coin':
                pg.draw.rect(self.screen, BUTTON_LINE_COLOR,
                             self.coin_button_rect.inflate(4, 4), 5, 4)
            case 'palm fg' | 'palm bg':
                pg.draw.rect(self.screen, BUTTON_LINE_COLOR,
                             self.palm_button_rect.inflate(4, 4), 5, 4)
            case 'enemy':
                pg.draw.rect(self.screen, BUTTON_LINE_COLOR,
                             self.enemy_button_rect.inflate(4, 4), 5, 4)

    def display(self, index: int):
        # UPDATE & DRAW BUTTON.
        self.buttons.update()
        self.buttons.draw(self.screen)
        # DRAW HIGHLIGHT.
        self.highlight(index)


class Button(pg.sprite.Sprite):
    def __init__(self, groups: AbstractGroup, rect: pg.Rect,
                 items: list[Surface], alt_items: list[Surface] | None = None):
        super().__init__(groups)
        # ORIGINAL.
        self.image = Surface(rect.size)
        self.rect = rect
        # RESOURCE.
        self.items: dict[str, list[Surface] | None] = {
            'main': items, 'alt': alt_items}
        self.main_active = True
        self.index = 0

    def get_id(self) -> int:
        return self.items['main' if self.main_active else 'alt'][self.index][0]

    def switch(self):
        self.index += 1
        if self.index >= len(self.items['main' if self.main_active else 'alt']):
            self.index = 0

    def update(self):
        # FILL IN BUTTON AREA WITH BACKGROUND COLOR.
        self.image.fill(BUTTON_BG_COLOR)
        # GET THE IMAGE BASE ON THE STATE & INDEX.
        surf: Surface = self.items['main' if self.main_active else 'alt'][self.index][1]
        # CENTER THE IMAGE IN THE BUTTON AREA.
        rect = surf.get_rect(
            center=(self.rect.width / 2, self.rect.height / 2))
        # DRAW BUTTON AREA.
        self.image.blit(surf, rect)
