from collections.abc import Callable

import pygame as pg
from cooldown import Timer
from player import Player
from settings import *


class Shop:

    def __init__(self, player: Player, toggle_shop: Callable[[], None]):
        # CORE.
        self.screen = pg.display.get_surface()
        self.font = pg.font.Font('font/LycheeSoda.ttf', 30)
        self.player = player
        # INTERACTION.
        self.toggle_shop = toggle_shop
        # STATISTIC.
        self.width = 400
        self.spacing, self.padding = 20, 8
        # ENTRIES.
        self.options = list(self.player.inventory_item) + \
            list(self.player.inventory_seed)
        self.sellable_index = len(list(self.player.inventory_item)) - 1
        self.load_data()
        # SELECTION.
        self.item_index = 0
        self.timer = Timer(200)

    def load_data(self):
        self.surf_texts: list[pg.Surface] = []
        self.total_height = 0

        for option in self.options:
            surf_text = self.font.render(option, False, 'BLACK')
            self.surf_texts.append(surf_text)
            self.total_height += surf_text.get_height() + 2 * self.padding
        self.total_height += (len(self.surf_texts) - 1) * self.spacing

        offset_left = (SCREEN_WIDTH - self.width) / 2
        self.offset_top = (SCREEN_HEIGHT - self.total_height) / 2
        self.rect_menu = pg.Rect(
            offset_left, self.offset_top, self.width, self.total_height)
        # BUY/SELL INFORMATION.
        self.surf_buy_text = self.font.render('buy', False, 'BLACK')
        self.surf_sell_text = self.font.render('sell', False, 'BLACK')

    def display_money(self):
        surf_text = self.font.render(f'${self.player.money}', False, 'BLACK')
        rect_text = surf_text.get_rect(midbottom=(
            SCREEN_WIDTH / 2, SCREEN_HEIGHT - 20))
        pg.draw.rect(self.screen, 'WHITE', rect_text.inflate(10, 10), 0, 5)
        self.screen.blit(surf_text, rect_text)

    def display_entry(self, surf_text: pg.Surface, amount: int, offset_top: int, is_selected: bool):
        # BACKGROUND.
        rect_bg = pg.Rect(self.rect_menu.left, offset_top,
                          self.width, surf_text.get_height() + 2 * self.padding)
        pg.draw.rect(self.screen, 'WHITE', rect_bg, 0, 5)
        # TEXT.
        rect_text = surf_text.get_rect(
            midleft=rect_bg.midleft + pg.math.Vector2(20, 0))
        self.screen.blit(surf_text, rect_text)
        # AMOUNT.
        surf_amount = self.font.render(str(amount), False, 'BLACK')
        rect_amount = surf_amount.get_rect(
            midright=rect_bg.midright + pg.math.Vector2(-20, 0))
        self.screen.blit(surf_amount, rect_amount)
        # CHECK SELECTED.
        if is_selected:
            # BODER.
            pg.draw.rect(self.screen, 'BLACK', rect_bg, 5, 5)
            # ADDITIONAL INFORMATION.
            surf_info = self.surf_sell_text if self.item_index <= self.sellable_index else self.surf_buy_text
            rect_info = surf_info.get_rect(
                midleft=rect_bg.midleft + pg.math.Vector2(175, 0))
            self.screen.blit(surf_info, rect_info)

    def input(self):
        keys = pg.key.get_pressed()
        # CLOSE.
        if keys[pg.K_ESCAPE]:
            self.toggle_shop()
        # MOVE.
        if not self.timer.is_actived:
            if keys[pg.K_UP]:
                self.item_index -= 1
                self.timer.activate()
            elif keys[pg.K_DOWN]:
                self.item_index += 1
                self.timer.activate()
            elif keys[pg.K_SPACE]:
                self.timer.activate()
                # SELL.
                choosen_item = self.options[self.item_index]
                if self.item_index <= self.sellable_index:
                    if self.player.inventory_item[choosen_item] > 0:
                        self.player.inventory_item[choosen_item] -= 1
                        self.player.money += SALE_PRICES[choosen_item]
                # BUY.
                else:
                    if self.player.money >= PURCHASE_PRICES[choosen_item]:
                        self.player.inventory_seed[choosen_item] += 1
                        self.player.money -= PURCHASE_PRICES[choosen_item]

            # CONSTRAINT.
            if self.item_index < 0:
                self.item_index = len(self.options) - 1
            elif self.item_index > len(self.options) - 1:
                self.item_index = 0

    def update(self):
        self.input()
        # MOENY.
        self.display_money()
        # MENU ENTRY.
        statistic = list(self.player.inventory_item.values()) + \
            list(self.player.inventory_seed.values())
        for index, surf_text in enumerate(self.surf_texts):
            offset_top = self.offset_top + index * \
                (surf_text.get_height() + 2 * self.padding + self.spacing)
            self.display_entry(
                surf_text, statistic[index], offset_top, self.item_index == index)
        # TIMER.
        self.timer.update()
