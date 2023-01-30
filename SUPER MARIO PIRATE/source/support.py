from csv import reader
from os import walk

import pygame as pg
from settings import TILE_SIZE


def load_image_folder(path: str):
    for _, _, files in walk(path):
        return [pg.image.load(f'{path}/{file}').convert_alpha() for file in files]


def load_csv_file(path: str):
    with open(path) as map:
        return [row for row in reader(map)]


def crop_image(path: str):
    # CROPPING SCALE.
    SCALE = TILE_SIZE, TILE_SIZE
    # ORIGINAL IMAGE.
    image = pg.image.load(path).convert_alpha()
    # CROPPED IMAGES.
    images = list()
    for row in range(int(image.get_height() / TILE_SIZE)):
        for col in range(int(image.get_width() / TILE_SIZE)):
            # CROPPING INFORMATION.
            place = col * TILE_SIZE, row * TILE_SIZE
            # CROPPED IMAGE.
            cut_image = pg.Surface(SCALE, flags=pg.SRCALPHA)
            cut_image.blit(image, (0, 0), pg.Rect(place, SCALE))
            images.append(cut_image)
    return images
