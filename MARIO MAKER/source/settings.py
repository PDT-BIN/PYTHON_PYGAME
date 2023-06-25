# SCALE & RATE INFORMATION.
TILE_SIZE = 64
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
ANIMATION_SPEED = 8

# OFFSET INFORMATION.
COIN_OFFSET = TILE_SIZE // 2, TILE_SIZE // 2    # FROM THE TOPLEFT.
ENEMY_OFFSET = TILE_SIZE // 2, TILE_SIZE        # FROM THE MIDBOTTOM.
TEXT_OFFSET = TILE_SIZE - 10, 0

# COLOR INFORMATION.
SKY_COLOR = '#DDC6A1'
SEA_COLOR = '#92A9CE'
HORIZON_COLOR = '#F5F1DE'
HORIZON_TOP_COLOR = '#D1AA9D'
LINE_COLOR = '#000000'
BUTTON_BG_COLOR = '#33323D'
BUTTON_LINE_COLOR = '#F5F1DE'

# USE TO STORE DATA OF TILE.
EDITOR_DATA: dict[int, dict[str, str | None]] = {
    0: {'style': 'player', 'type': 'object', 'menu': None, 'menu_surf': None, 'preview': None, 'graphics': 'image/player/idle_right'},
    1: {'style': 'sky',    'type': 'object', 'menu': None, 'menu_surf': None, 'preview': None, 'graphics': None},

    2: {'style': 'terrain', 'type': 'tile', 'menu': 'terrain', 'menu_surf': 'image/menu/land.png',  'preview': 'image/preview/land.png',  'graphics': None},
    3: {'style': 'water',   'type': 'tile', 'menu': 'terrain', 'menu_surf': 'image/menu/water.png', 'preview': 'image/preview/water.png', 'graphics': 'image/terrain/water/animation'},

    4: {'style': 'coin', 'type': 'tile', 'menu': 'coin', 'menu_surf': 'image/menu/gold.png',    'preview': 'image/preview/gold.png',    'graphics': 'image/items/gold'},
    5: {'style': 'coin', 'type': 'tile', 'menu': 'coin', 'menu_surf': 'image/menu/silver.png',  'preview': 'image/preview/silver.png',  'graphics': 'image/items/silver'},
    6: {'style': 'coin', 'type': 'tile', 'menu': 'coin', 'menu_surf': 'image/menu/diamond.png', 'preview': 'image/preview/diamond.png', 'graphics': 'image/items/diamond'},

    7:  {'style': 'enemy', 'type': 'tile', 'menu': 'enemy', 'menu_surf': 'image/menu/spikes.png',      'preview': 'image/preview/spikes.png',      'graphics': 'image/enemies/spikes'},
    8:  {'style': 'enemy', 'type': 'tile', 'menu': 'enemy', 'menu_surf': 'image/menu/tooth.png',       'preview': 'image/preview/tooth.png',       'graphics': 'image/enemies/tooth/idle'},
    9:  {'style': 'enemy', 'type': 'tile', 'menu': 'enemy', 'menu_surf': 'image/menu/shell_left.png',  'preview': 'image/preview/shell_left.png',  'graphics': 'image/enemies/shell_left/idle'},
    10: {'style': 'enemy', 'type': 'tile', 'menu': 'enemy', 'menu_surf': 'image/menu/shell_right.png', 'preview': 'image/preview/shell_right.png', 'graphics': 'image/enemies/shell_right/idle'},

    11: {'style': 'palm_fg', 'type': 'object', 'menu': 'palm fg', 'menu_surf': 'image/menu/small_fg.png', 'preview': 'image/preview/small_fg.png', 'graphics': 'image/terrain/palm/small_fg'},
    12: {'style': 'palm_fg', 'type': 'object', 'menu': 'palm fg', 'menu_surf': 'image/menu/large_fg.png', 'preview': 'image/preview/large_fg.png', 'graphics': 'image/terrain/palm/large_fg'},
    13: {'style': 'palm_fg', 'type': 'object', 'menu': 'palm fg', 'menu_surf': 'image/menu/left_fg.png',  'preview': 'image/preview/left_fg.png',  'graphics': 'image/terrain/palm/left_fg'},
    14: {'style': 'palm_fg', 'type': 'object', 'menu': 'palm fg', 'menu_surf': 'image/menu/right_fg.png', 'preview': 'image/preview/right_fg.png', 'graphics': 'image/terrain/palm/right_fg'},

    15: {'style': 'palm_bg', 'type': 'object', 'menu': 'palm bg', 'menu_surf': 'image/menu/small_bg.png', 'preview': 'image/preview/small_bg.png', 'graphics': 'image/terrain/palm/small_bg'},
    16: {'style': 'palm_bg', 'type': 'object', 'menu': 'palm bg', 'menu_surf': 'image/menu/large_bg.png', 'preview': 'image/preview/large_bg.png', 'graphics': 'image/terrain/palm/large_bg'},
    17: {'style': 'palm_bg', 'type': 'object', 'menu': 'palm bg', 'menu_surf': 'image/menu/left_bg.png',  'preview': 'image/preview/left_bg.png',  'graphics': 'image/terrain/palm/left_bg'},
    18: {'style': 'palm_bg', 'type': 'object', 'menu': 'palm bg', 'menu_surf': 'image/menu/right_bg.png', 'preview': 'image/preview/right_bg.png', 'graphics': 'image/terrain/palm/right_bg'},
}

# USE TO CHECK TILES SURROUNDING SELECTED TILE.
NEIGHBOR_DIRECTIONS: dict[str, tuple[int, int]] = {
    'A': (0, -1),   'B': (1, -1),
    'C': (1, 0),    'D': (1, 1),
    'E': (0, 1),    'F': (-1, 1),
    'G': (-1, 0),   'H': (-1, -1)
}

# USE TO CHECK THE ORDINAL FOR DRAWING IN FRAME.
LEVEL_LAYERS: dict[str, int] = {
    'clouds': 1, 'ocean': 2, 'bg': 3, 'water': 4, 'main': 5
}
