WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720

BLOCK_MAP = [
    '666666666666',
    '444557755444',
    '333333333333',
    '222222222222',
    '111111111111',
    '            ',
    '            ',
    '            ',
    '            '
]

COLOR_LEGEND = {
    '1': 'blue', '2': 'green', '3': 'red', '4': 'orange',
    '5': 'purple', '6': 'bronce', '7': 'grey'
}

UPGRADES = ('heart', 'speed', 'size', 'laser')

GAP_SIZE, TOP_OFFSET = 2, WINDOW_HEIGHT // 30
BLOCK_WIDTH = WINDOW_WIDTH / len(BLOCK_MAP[0]) - GAP_SIZE
BLOCK_HEIGHT = WINDOW_HEIGHT / len(BLOCK_MAP) - GAP_SIZE
