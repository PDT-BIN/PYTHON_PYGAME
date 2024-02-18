import sys

from level import Level
from overworld import Overworld
from pytmx.util_pygame import load_pygame
from settings import *
from statistic import UI, Data
from supports import *


class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pg.display.set_caption("SUPER PIRATE WORLD")
        self.clock = pg.time.Clock()
        # RESOURCE.
        self.import_assets()
        self.ui = UI(self.font, self.ui_frames)
        self.data = Data(self.ui)
        self.TMX_MAPS = {
            0: load_pygame(get_path("data", "levels", "0.tmx")),
            1: load_pygame(get_path("data", "levels", "1.tmx")),
            2: load_pygame(get_path("data", "levels", "2.tmx")),
            3: load_pygame(get_path("data", "levels", "3.tmx")),
            4: load_pygame(get_path("data", "levels", "4.tmx")),
            5: load_pygame(get_path("data", "levels", "5.tmx")),
            6: load_pygame(get_path("data", "levels", "6.tmx")),
        }
        self.TMX_OVERWORLD = load_pygame(get_path("data", "overworld", "overworld.tmx"))
        self.SOUNDS = {
            "ITEM": pg.mixer.Sound(get_path("audio", "coin.wav")),
            "ATTACK": pg.mixer.Sound(get_path("audio", "attack.wav")),
            "DAMAGE": pg.mixer.Sound(get_path("audio", "damage.wav")),
            "HIT": pg.mixer.Sound(get_path("audio", "hit.wav")),
            "JUMP": pg.mixer.Sound(get_path("audio", "jump.wav")),
            "PEARL": pg.mixer.Sound(get_path("audio", "pearl.wav")),
        }
        # MAIN CONTROL.
        self.stage = Overworld(
            self.TMX_OVERWORLD, self.overworld_frames, self.data, self.switch_stage
        )
        # BACKGROUND MUSIC.
        pg.mixer.music.load(get_path("audio", "starlight_city.mp3"))
        pg.mixer.music.set_volume(0.3)
        pg.mixer.music.play(-1)

    def switch_stage(self, target: str, unlock: int = 0):
        if target == "LEVEL":
            self.stage = Level(
                self.TMX_MAPS[self.data.current_level],
                self.level_frames,
                self.data,
                self.switch_stage,
                self.SOUNDS,
            )
        else:
            if unlock > 0:
                if unlock > self.data.unlocked_level:
                    self.data.unlocked_level = unlock
            else:
                self.data.health -= 1
            self.stage = Overworld(
                self.TMX_OVERWORLD, self.overworld_frames, self.data, self.switch_stage
            )

    def import_assets(self):
        self.level_frames = {
            "flag": import_folder_list("image", "level", "flag"),
            "saw": import_folder_list("image", "enemies", "saw", "animation"),
            "floor_spike": import_folder_list("image", "enemies", "floor_spikes"),
            "palms": import_sub_folder("image", "level", "palms"),
            "candle": import_folder_list("image", "level", "candle"),
            "window": import_folder_list("image", "level", "window"),
            "big_chain": import_folder_list("image", "level", "big_chains"),
            "small_chain": import_folder_list("image", "level", "small_chains"),
            "candle_light": import_folder_list("image", "level", "candle light"),
            "player": import_sub_folder("image", "player"),
            "helicopter": import_folder_list("image", "level", "helicopter"),
            "boat": import_folder_list("image", "objects", "boat"),
            "saw_chain": import_image("image", "enemies", "saw", "saw_chain"),
            "spike": import_image("image", "enemies", "spike_ball", "Spiked Ball"),
            "spike_chain": import_image(
                "image", "enemies", "spike_ball", "spiked_chain"
            ),
            "tooth": import_folder_list("image", "enemies", "tooth", "run"),
            "shell": import_sub_folder("image", "enemies", "shell"),
            "pearl": import_image("image", "enemies", "bullets", "pearl"),
            "items": import_sub_folder("image", "items"),
            "particle": import_folder_list("image", "effects", "particle"),
            "water_top": import_folder_list("image", "level", "water", "top"),
            "water_body": import_image("image", "level", "water", "body"),
            "bg_tiles": import_folder_dict("image", "level", "bg", "tiles"),
            "small_cloud": import_folder_list("image", "level", "clouds", "small"),
            "large_cloud": import_image("image", "level", "clouds", "large_cloud"),
        }
        self.font = pg.font.Font(get_path("image", "ui", "runescape_uf.ttf"), 40)
        self.ui_frames = {
            "heart": import_folder_list("image", "ui", "heart"),
            "coin": import_image("image", "ui", "coin"),
        }
        self.overworld_frames = {
            "palms": import_folder_list("image", "overworld", "palm"),
            "water": import_folder_list("image", "overworld", "water"),
            "path": import_folder_dict("image", "overworld", "path"),
            "icon": import_sub_folder("image", "overworld", "icon"),
        }

    def check_game_over(self):
        if self.data.health <= 0:
            pg.quit()
            sys.exit()

    def run(self):
        """MAIN LOOP"""
        while True:
            # DELTA TIME (SECONDS PER FRAME).
            delta_time = self.clock.tick() / 1000
            # HANDLE EVENTS.
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
            # MAIN FLOW.
            self.stage.run(delta_time)
            self.ui.update(delta_time)
            self.check_game_over()
            # REFRESH SCREEN.
            pg.display.update()


if __name__ == "__main__":
    Game().run()
