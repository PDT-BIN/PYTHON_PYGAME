import pygame as pg
from player import Player
from settings import *


class Item:

    def __init__(self, place: tuple[int, int], size: tuple[int, int], index: int, font: pg.font.Font):
        # CORE.
        self.rect = pg.Rect(place, size)
        self.index = index
        self.font = font

    def draw_content(self, screen: pg.Surface, name: str, cost: int, is_selected: bool):
        color = TEXT_COLOR_SELECTED if is_selected else TEXT_COLOR
        offset = pg.math.Vector2(0, 20)
        # TITLE.
        name_surf = self.font.render(name, False, color)
        name_rect = name_surf.get_rect(midtop=self.rect.midtop + offset)
        # COST.
        cost_surf = self.font.render(str(int(cost)), False, color)
        cost_rect = cost_surf.get_rect(midbottom=self.rect.midbottom - offset)
        # DRAW.
        screen.blit(name_surf, name_rect)
        screen.blit(cost_surf, cost_rect)

    def draw_bar(self, screen: pg.Surface, value: int, max_value: int, is_selected: bool):
        # INFORMATION.
        color = TEXT_COLOR_SELECTED if is_selected else TEXT_COLOR
        offset = pg.math.Vector2(0, 60)
        top, bottom = self.rect.midtop + offset, self.rect.midbottom - offset

        # BAR SETUP.
        value_height = value * (bottom[1] - top[1]) / max_value
        bar_rect = pg.Rect(top[0] - 15, bottom[1] - value_height, 30, 10)

        # DRAW.
        pg.draw.line(screen, color, top, bottom, 5)
        pg.draw.rect(screen, color, bar_rect)

    def trigger(self, player: Player):
        upgrade_attribute = tuple(player.stats.keys())[self.index]
        upgrade_cost = player.upgrade_cost[upgrade_attribute]

        if player.exp >= upgrade_cost:
            upgrade_value = player.stats[upgrade_attribute]
            max_value = player.MAX_STATS[upgrade_attribute]

            if upgrade_value < max_value:
                player.exp -= upgrade_cost
                player.stats[upgrade_attribute] *= 1.2
                player.upgrade_cost[upgrade_attribute] *= 1.4

                if player.stats[upgrade_attribute] > max_value:
                    player.stats[upgrade_attribute] = max_value

    def draw(self, screen: pg.Surface, selected_index: int, name: str,
             value: int, max_value: int,  cost: int):
        bg_color = UPGRADE_BG_COLOR_SELECTED if (
            is_selected := selected_index == self.index) else UI_BG_COLOR
        pg.draw.rect(screen, bg_color, self.rect)
        pg.draw.rect(screen, UI_BORDER_COLOR, self.rect, 3)
        self.draw_content(screen, name, cost, is_selected)
        self.draw_bar(screen, value, max_value, is_selected)


class UpgradeController:

    def __init__(self, player: Player):
        # CORE.
        self.screen = pg.display.get_surface()
        self.player = player
        self.font = pg.font.Font(UI_FONT, UI_FONT_SIZE)
        self.attribute_names = list(player.MAX_STATS.keys())
        self.max_values = list(player.MAX_STATS.values())
        self.item_quantity = len(self.attribute_names)
        # SELECTION SYSTEM.
        self.selection_index = 0
        self.can_select, self.SELECTION_COOLDOWN = True, 300
        self.selection_time = None
        # SETUP.
        self.load_items()

    def load_items(self):
        # ITEM DIMENSION.
        size = (width := self.screen.get_width() // (self.item_quantity + 1),
                self.screen.get_height() * 0.8)
        # OFFSET & PADDING.
        offset = self.screen.get_width() // self.item_quantity
        padding = (offset - width) // 2
        # LOADING.
        self.list_item: list[Item] = []
        for index in range(self.item_quantity):
            place = index * offset + padding, self.screen.get_height() * 0.1

            self.list_item.append(Item(place, size, index, self.font))

    def input(self):
        keys = pg.key.get_pressed()

        if self.can_select:
            if keys[pg.K_LEFT] and self.selection_index > 0:
                self.selection_index -= 1
                self.can_select = False
                self.selection_time = pg.time.get_ticks()
            elif keys[pg.K_RIGHT] and self.selection_index < len(self.attribute_names) - 1:
                self.selection_index += 1
                self.can_select = False
                self.selection_time = pg.time.get_ticks()

            if keys[pg.K_SPACE]:
                self.can_select = False
                self.selection_time = pg.time.get_ticks()
                self.list_item[self.selection_index].trigger(self.player)

    def cooldown(self):
        if not self.can_select:
            if pg.time.get_ticks() - self.selection_time > self.SELECTION_COOLDOWN:
                self.can_select = True

    def display(self):
        self.input()
        self.cooldown()

        for index, item in enumerate(self.list_item):
            name = self.attribute_names[index]
            value = self.player.get_value_by_index(index)
            max_value = self.max_values[index]
            cost = self.player.get_cost_by_index(index)
            item.draw(self.screen, self.selection_index,
                      name, value, max_value, cost)
