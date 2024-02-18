from os import walk
from os.path import join
from typing import Mapping, Sequence

from pygame import Surface
from pygame.image import load


def get_path(*components: str) -> str:
    return join(*components)


def import_image(*component: str, alpha: bool = True, format: str = "png") -> Surface:
    surface = load(f"{get_path(*component)}.{format}")
    return surface.convert_alpha() if alpha else surface.convert()


def import_folder_list(*component: str) -> Sequence[Surface]:
    frames = []
    for folder_path, _, file_names in walk(get_path(*component)):
        for file_name in sorted(file_names, key=lambda name: int(name.split(".")[0])):
            path = get_path(folder_path, file_name)
            frames.append(load(path).convert_alpha())
    return frames


def import_folder_dict(*component: str) -> Mapping[str, Surface]:
    frames = {}
    for folder_path, _, file_names in walk(get_path(*component)):
        for file_name in file_names:
            path = get_path(folder_path, file_name)
            surface = load(path).convert_alpha()
            frames[file_name.split(".")[0]] = surface
    return frames


def import_sub_folder(*component: str) -> Mapping[str, Sequence[Surface]]:
    frames = {}
    for _, sub_folders, _ in walk(get_path(*component)):
        if sub_folders:
            for sub_folder in sub_folders:
                frames[sub_folder] = import_folder_list(*component, sub_folder)
    return frames
