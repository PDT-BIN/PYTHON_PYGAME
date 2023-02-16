from os import walk

import pygame as pg


def load_image_list(path: str):
    for _, _, files in walk(path):
        return [pg.image.load(f'{path}/{file}').convert_alpha() for file in files]


def load_image_dictionary(path: str):
    for _, _, files in walk(path):
        return {file.split('.')[0]: pg.image.load(f'{path}/{file}').convert_alpha() for file in files}
