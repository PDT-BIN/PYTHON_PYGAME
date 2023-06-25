from os import walk

from pygame import Surface
from pygame.image import load as load_image


def load_folder_list(path: str) -> list[Surface]:
    for _, _, files in walk(path):
        return [load_image(f'{path}/{file}').convert_alpha() for file in files]


def load_folder_dict(path: str) -> dict[str, Surface]:
    for _, _, files in walk(path):
        return {file.strip('.png'): load_image(f'{path}/{file}').convert_alpha() for file in files}


def load_an_image(path: str) -> Surface:
    return load_image(path).convert_alpha()
