from typing import Any, Callable, Literal, Mapping, Sequence, Tuple, TypeAlias, Union

import pygame as pg
from pygame import Surface
from pygame.font import Font
from pygame.math import Vector2
from pygame.mixer import Sound
from pygame.sprite import AbstractGroup

# TYPE HINT.
Point: TypeAlias = Union[Tuple[float, float], Vector2]
Path: TypeAlias = Sequence[Point]
Group: TypeAlias = Union[AbstractGroup, Sequence[AbstractGroup]]
Frame: TypeAlias = Union[
    Sequence[Surface], Mapping[str, Union[Surface, Sequence[Surface]]]
]
Asset: TypeAlias = Mapping[str, Union[Surface, Frame]]
Audio: TypeAlias = Union[Sound, Mapping[str, Sound]]


# SPECIFICATIONS.
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
TILE_SIZE = 64
ANIMATION_SPEED = 6

# OBJECT LAYERS.
Z_LAYERS = {
    "BG": 0,
    "CLOUDS": 1,
    "BG TILES": 2,
    "PATH": 3,
    "BG DETAILS": 4,
    "MAIN": 5,
    "WATER": 6,
    "FG": 7,
}
