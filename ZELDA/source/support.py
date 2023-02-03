from csv import reader
from os import walk

import pygame as pg


def load_csv_layout(path: str):
    with open(path) as map:
        return [row for row in reader(map, delimiter=',')]


def load_image_folder(path: str):
    for _, _, files in walk(path):
        return [pg.image.load(f'{path}/{file}').convert_alpha() for file in files]
