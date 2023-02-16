import pygame as pg
from player import Player
from settings import *


class Overlay:

    def __init__(self, player: Player):
        # CORE.
        self.screen = pg.display.get_surface()
        self.player = player
        # GRAPHICS.
        self.surf_tools = {tool: pg.image.load(
            f'image/overlay/{tool}.png').convert_alpha() for tool in player.tools}
        self.surf_seeds = {seed: pg.image.load(
            f'image/overlay/{seed}.png').convert_alpha() for seed in player.seeds}

    def display(self):
        surf_tool = self.surf_tools[self.player.selected_tool]
        rect_tool = surf_tool.get_rect(midbottom=OVERLAY_POSITIONS['tool'])
        self.screen.blit(surf_tool, rect_tool)

        surf_seed = self.surf_seeds[self.player.selected_seed]
        rect_seed = surf_seed.get_rect(midbottom=OVERLAY_POSITIONS['seed'])
        self.screen.blit(surf_seed, rect_seed)
