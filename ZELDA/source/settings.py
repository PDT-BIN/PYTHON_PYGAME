WIDTH, HEIGTH = 1280, 720
TILESIZE = 64

# OFFSET.
HITBOX_OFFSET = {
    'Player': -26,
    'Object': -40,
    'Grass': -10,
    'Invisible': 0
}

# UI.
BAR_HEIGHT = 20
HEALTH_BAR_WIDTH = 200
ENERGY_BAR_WIDTH = 140
ITEM_BOX_SIZE = 80
UI_FONT = 'font/joystix.ttf'
UI_FONT_SIZE = 18

# GENERAL COLORS.
WATER_COLOR = '#71DDEE'
UI_BG_COLOR = '#222222'
UI_BORDER_COLOR = '#111111'
TEXT_COLOR = '#EEEEEE'

# UI COLORS.
HEALTH_COLOR = 'RED'
ENERGY_COLOR = 'BLUE'
UI_BORDER_COLOR_ACTIVE = 'GOLD'

# UPGRADE MENU.
TEXT_COLOR_SELECTED = '#111111'
BAR_COLOR = '#EEEEEE'
BAR_COLOR_SELECTED = '#111111'
UPGRADE_BG_COLOR_SELECTED = '#EEEEEE'

WEAPON_DATA = {
    'sword': {'Cooldown': 100, 'Damage': 15, 'Graphic': 'image/weapons/sword/full.png'},
    'lance': {'Cooldown': 400, 'Damage': 30, 'Graphic': 'image/weapons/lance/full.png'},
    'axe': {'Cooldown': 300, 'Damage': 20, 'Graphic': 'image/weapons/axe/full.png'},
    'rapier': {'Cooldown': 50, 'Damage': 8, 'Graphic': 'image/weapons/rapier/full.png'},
    'sai': {'Cooldown': 80, 'Damage': 10, 'Graphic': 'image/weapons/sai/full.png'}
}

MAGIC_DATA = {
    'flame': {'Strength': 5, 'Cost': 20, 'Graphic': 'image/particles/flame/fire.png'},
    'heal': {'Strength': 20, 'Cost': 10, 'Graphic': 'image/particles/heal/heal.png'}
}

MONSTER_DATA = {
    'squid': {'Health': 100, 'Exp': 100, 'Damage': 20, 'Attack_type': 'slash',
              'Attack_sound': 'audio/attack/slash.wav', 'Speed': 3, 'Resistance': 3,
              'Attack_radius': 80, 'Notice_radius': 360},
    'raccoon': {'Health': 300, 'Exp': 250, 'Damage': 40, 'Attack_type': 'claw',
                'Attack_sound': 'audio/attack/claw.wav', 'Speed': 2, 'Resistance': 3,
                'Attack_radius': 120, 'Notice_radius': 400},
    'spirit': {'Health': 100, 'Exp': 110, 'Damage': 8, 'Attack_type': 'thunder',
               'Attack_sound': 'audio/attack/fireball.wav', 'Speed': 4, 'Resistance': 3,
               'Attack_radius': 60, 'Notice_radius': 350},
    'bamboo': {'Health': 70, 'Exp': 120, 'Damage': 6, 'Attack_type': 'leaf_attack',
               'Attack_sound': 'audio/attack/slash.wav', 'Speed': 3, 'Resistance': 3,
               'Attack_radius': 50, 'Notice_radius': 300}}
