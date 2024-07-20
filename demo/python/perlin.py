from perlin_noise import PerlinNoise
from typing import List, Any, Dict, Tuple, TypedDict
import pygame
import argparse
from dataclasses import dataclass
import rich
from time import time_ns
import json
from tileset import load_tileset, Tile, Name, get_animation_steps, Animation
from pathlib import Path
from enum import Enum
from random import choice
import numpy as np
from PIL import Image

BLACK = (0, 0, 0)
GREY = (100, 100, 100)
RED = (255, 0, 0)

ANIMATION_SEQUENCE_LEN = 4
ANIMATION_INV_SPEED = 5

CHUNK_SIZE = 8


def info(msg: str, end: str = '\n'):
    rich.print(f"[bold green]INFO[/bold green]: {msg}", end=end)


def warning(msg: str, end: str = '\n'):
    rich.print(f"[bold yellow]WARNING[/bold yellow]: {msg}", end=end)


class NoiseOctave(TypedDict):
    amplitude: float
    octaves: float


class LandType(Enum):
    ROCK = 'r'
    GRASS = 'g'
    WATER = 'w'


class LandHeights(TypedDict):
    ROCK: float
    GRASS: float
    WATER: float


def to_land_type(x: float, land_heights: LandHeights) -> LandType:
    for k, v in land_heights.items():
        if x > v:
            return LandType._member_map_[k]


@dataclass
class Cell:
    i: int
    j: int
    background: Tile
    foreground: Tile | None


LT = LandType
TILEMAP = {
    # iiii
    "gggg": [
        ("grass_1", None),
        ("grass_2", None),
        ("grass_3", None),
        ("grass_4", None),
        ("grass_5", None),
        ("grass_6", None),
        ("grass_7", None),
        ("grass_8", None),
        ("grass_9", None),
    ],
    "wwww": [("water", None)],
    "rrrr": [("grass_1", None)],

    # iiij
    "gggw": [("river_corner_north_west", None)],  # noqa: E501
    "ggwg": [("river_corner_north_east", None)],  # noqa: E501
    "gwgg": [("river_corner_south_west", None)],  # noqa: E501
    "wggg": [("river_corner_south_east", None)],  # noqa: E501

    "wwwg": [("river_inv_corner_south_east", None)],  # noqa: E501
    "wwgw": [("river_inv_corner_south_west", None)],  # noqa: E501
    "wgww": [("river_inv_corner_north_east", None)],  # noqa: E501
    "gwww": [("river_inv_corner_north_west", None)],  # noqa: E501

    "gggr": [("rock_north_west", None)],  # noqa: E501
    "ggrg": [("rock_north_east", None)],  # noqa: E501
    "grgg": [("rock_south_west", None)],  # noqa: E501
    "rggg": [("rock_south_east", None)],  # noqa: E501

    "wwwr": [("water", "rock_north_west_2")],  # noqa: E501
    "wwrw": [("water", "rock_north_east_2")],  # noqa: E501
    "wrww": [("water", "rock_south_west_2")],  # noqa: E501
    "rwww": [("water", "rock_south_east_2")],  # noqa: E501

    "rrrw": [("water", "rock_corner_south_east_2")],  # noqa: E501
    "rrwr": [("water", "rock_corner_south_west_2")],  # noqa: E501
    "rwrr": [("water", "rock_corner_north_east_2")],  # noqa: E501
    "wrrr": [("water", "rock_corner_north_west_2")],  # noqa: E501

    "rrrg": [("rock_corner_south_east", None)],  # noqa: E501
    "rrgr": [("rock_corner_south_west", None)],  # noqa: E501
    "rgrr": [("rock_corner_north_east", None)],  # noqa: E501
    "grrr": [("rock_corner_north_west", None)],  # noqa: E501

    # iijj
    "wggw": [("river_diag_anti", None)],  # noqa: E501
    "gwwg": [("river_diag", None)],
    "ggww": [("river_north", None)],
    "gwgw": [("river_west", None)],
    "wgwg": [("river_east", None)],
    "wwgg": [("river_south", None)],

    "wrrw": [("water", "rock_diag_anti_2")],  # noqa: E501
    "rwwr": [("water", "rock_diag_2")],
    "rrww": [("water", "rock_south_2")],
    "rwrw": [("water", "rock_east_2")],
    "wrwr": [("water", "rock_west_2")],
    "wwrr": [("water", "rock_north_2")],

    "rggr": [("rock_diag", None)],
    "grrg": [("rock_diag_anti", None)],
    "ggrr": [("rock_north", None)],
    "grgr": [("rock_west", None)],
    "rgrg": [("rock_east", None)],
    "rrgg": [("rock_south", None)],

    # iijk
    "wwgr": [("river_south", "rock_north_west_2")],  # noqa: E501
    "gwrw": [("river_west", "rock_north_east_2")],  # noqa: E501
    "rgww": [("river_north", "rock_south_east_2")],  # noqa: E501
    "wrwg": [("river_east", "rock_south_west_2")],  # noqa: E501

    "wwrg": [("river_south", "rock_north_east_2")],  # noqa: E501
    "rwgw": [("river_west", "rock_south_east_2")],  # noqa: E501
    "grww": [("river_north", "rock_south_west_2")],  # noqa: E501
    "wgwr": [("river_east", "rock_north_west_2")],  # noqa: E501

    "rrwg": [("river_east", "rock_south_2")],  # noqa: E501
    "wrgr": [("river_corner_south_east", "rock_west_2")],  # noqa: E501
    "gwrr": [("river_west", "rock_north_2")],  # noqa: E501
    "rgrw": [("river_corner_north_west", "rock_east_2")],  # noqa: E501

    "rrgw": [("river_corner_north_west", "rock_south_2")],  # noqa: E501
    "grwr": [("river_corner_north_east", "rock_west_2")],  # noqa: E501
    "wgrr": [("river_east", "rock_north_2")],  # noqa: E501
    "rwrg": [("river_south", "rock_east_2")],  # noqa: E501

    "ggwr": [("river_corner_north_east", "rock_north_west_2")],  # noqa: E501
    "wgrg": [("river_corner_south_east", "rock_north_east_2")],  # noqa: E501
    "rwgg": [("river_corner_south_west", "rock_south_east_2")],  # noqa: E501
    "grgw": [("river_corner_north_west", "rock_south_west_2")],  # noqa: E501

    "ggrw": [("river_corner_north_west", "rock_north_east_2")],  # noqa: E501
    "rgwg": [("river_corner_north_east", "rock_south_east_2")],  # noqa: E501
    "wrgg": [("river_corner_south_east", "rock_south_west_2")],  # noqa: E501
    "gwgr": [("river_corner_south_west", "rock_north_west_2")],  # noqa: E501

    "gwrg": [("river_corner_south_west", "rock_north_east_2")],  # noqa: E501
    "rggw": [("river_corner_north_west", "rock_south_east_2")],  # noqa: E501
    "grwg": [("river_corner_north_east", "rock_south_west_2")],  # noqa: E501
    "wggr": [("river_corner_south_east", "rock_north_west_2")],  # noqa: E501

    "wgrw": [("river_inv_corner_north_east", "rock_north_east_2")],  # noqa: E501
    "rwwg": [("river_inv_corner_south_east", "rock_south_east_2")],  # noqa: E501
    "wrgw": [("river_inv_corner_south_west", "rock_south_west_2")],  # noqa: E501
    "gwwr": [("river_inv_corner_north_west", "rock_north_west_2")],  # noqa: E501

    "rwgr": [("river_corner_south_west", "rock_diag_2")],  # noqa: E501
    "grrw": [("river_corner_north_west", "rock_diag_anti_2")],  # noqa: E501
    "rgwr": [("river_corner_north_east", "rock_diag_2")],  # noqa: E501
    "wrrg": [("river_corner_south_east", "rock_diag_anti_2")],  # noqa: E501
}

FOREST_TILEMAP = {
    # full forest
    "111111111": ["forest"],

    # exactly 4 in the corners
    "000011011": ["forest_corner_north_west", "forest_corner_in_north_west"],
    "000110110": ["forest_corner_north_east", "forest_corner_in_north_east"],
    "011011000": ["forest_corner_south_west", "forest_corner_in_south_west"],
    "110110000": ["forest_corner_south_east", "forest_corner_in_south_east"],

    "000110111": ["forest_corner_north_east", "forest_corner_in_north_east"],
    "000111110": ["forest_corner_north_east", "forest_corner_in_north_east"],
    "001110110": ["forest_corner_north_east", "forest_corner_in_north_east"],
    "001110111": ["forest_corner_north_east", "forest_corner_in_north_east"],
    "001111110": ["forest_corner_north_east", "forest_corner_in_north_east"],
    "010110110": ["forest_corner_north_east", "forest_corner_in_north_east"],
    "010110111": ["forest_corner_north_east", "forest_corner_in_north_east"],
    "010111110": ["forest_corner_north_east", "forest_corner_in_north_east"],
    "011110110": ["forest_corner_north_east", "forest_corner_in_north_east"],
    "011110111": ["forest_corner_north_east", "forest_corner_in_north_east"],
    "100110110": ["forest_corner_north_east", "forest_corner_in_north_east"],
    "100110111": ["forest_corner_north_east", "forest_corner_in_north_east"],
    "100111110": ["forest_corner_north_east", "forest_corner_in_north_east"],
    "101110110": ["forest_corner_north_east", "forest_corner_in_north_east"],
    "101110111": ["forest_corner_north_east", "forest_corner_in_north_east"],
    "101111110": ["forest_corner_north_east", "forest_corner_in_north_east"],

    "011011001": ["forest_corner_south_west", "forest_corner_in_south_west"],
    "011011010": ["forest_corner_south_west", "forest_corner_in_south_west"],
    "011011100": ["forest_corner_south_west", "forest_corner_in_south_west"],
    "011011101": ["forest_corner_south_west", "forest_corner_in_south_west"],
    "011011110": ["forest_corner_south_west", "forest_corner_in_south_west"],
    "011111000": ["forest_corner_south_west", "forest_corner_in_south_west"],
    "011111001": ["forest_corner_south_west", "forest_corner_in_south_west"],
    "011111010": ["forest_corner_south_west", "forest_corner_in_south_west"],
    "011111100": ["forest_corner_south_west", "forest_corner_in_south_west"],
    "011111101": ["forest_corner_south_west", "forest_corner_in_south_west"],
    "111011000": ["forest_corner_south_west", "forest_corner_in_south_west"],
    "111011001": ["forest_corner_south_west", "forest_corner_in_south_west"],
    "111011010": ["forest_corner_south_west", "forest_corner_in_south_west"],
    "111011100": ["forest_corner_south_west", "forest_corner_in_south_west"],
    "111011101": ["forest_corner_south_west", "forest_corner_in_south_west"],
    "111011110": ["forest_corner_south_west", "forest_corner_in_south_west"],

    "110110001": ["forest_corner_south_east", "forest_corner_in_south_east"],
    "110110010": ["forest_corner_south_east", "forest_corner_in_south_east"],
    "110110011": ["forest_corner_south_east", "forest_corner_in_south_east"],
    "110110100": ["forest_corner_south_east", "forest_corner_in_south_east"],
    "110110101": ["forest_corner_south_east", "forest_corner_in_south_east"],
    "110111000": ["forest_corner_south_east", "forest_corner_in_south_east"],
    "110111001": ["forest_corner_south_east", "forest_corner_in_south_east"],
    "110111010": ["forest_corner_south_east", "forest_corner_in_south_east"],
    "110111100": ["forest_corner_south_east", "forest_corner_in_south_east"],
    "110111101": ["forest_corner_south_east", "forest_corner_in_south_east"],
    "111110000": ["forest_corner_south_east", "forest_corner_in_south_east"],
    "111110001": ["forest_corner_south_east", "forest_corner_in_south_east"],
    "111110010": ["forest_corner_south_east", "forest_corner_in_south_east"],
    "111110011": ["forest_corner_south_east", "forest_corner_in_south_east"],
    "111110100": ["forest_corner_south_east", "forest_corner_in_south_east"],
    "111110101": ["forest_corner_south_east", "forest_corner_in_south_east"],

    "000011111": ["forest_corner_north_west", "forest_corner_in_north_west"],
    "000111011": ["forest_corner_north_west", "forest_corner_in_north_west"],
    "001011011": ["forest_corner_north_west", "forest_corner_in_north_west"],
    "001011111": ["forest_corner_north_west", "forest_corner_in_north_west"],
    "001111011": ["forest_corner_north_west", "forest_corner_in_north_west"],
    "010011011": ["forest_corner_north_west", "forest_corner_in_north_west"],
    "010011111": ["forest_corner_north_west", "forest_corner_in_north_west"],
    "010111011": ["forest_corner_north_west", "forest_corner_in_north_west"],
    "100011011": ["forest_corner_north_west", "forest_corner_in_north_west"],
    "100011111": ["forest_corner_north_west", "forest_corner_in_north_west"],
    "100111011": ["forest_corner_north_west", "forest_corner_in_north_west"],
    "101011011": ["forest_corner_north_west", "forest_corner_in_north_west"],
    "101011111": ["forest_corner_north_west", "forest_corner_in_north_west"],
    "101111011": ["forest_corner_north_west", "forest_corner_in_north_west"],
    "110011011": ["forest_corner_north_west", "forest_corner_in_north_west"],
    "110011111": ["forest_corner_north_west", "forest_corner_in_north_west"],

    # exact cardinal directions
    "000111111": ["forest_north"],
    "111111000": ["forest_south"],
    "110110110": ["forest_east"],
    "011011011": ["forest_west"],

    "001111111": ["forest_north"],
    "010111111": ["forest_north"],
    "101111111": ["forest_north"],
    "100111111": ["forest_north"],

    "111111001": ["forest_south"],
    "111111010": ["forest_south"],
    "111111101": ["forest_south"],
    "111111100": ["forest_south"],

    "110110111": ["forest_east"],
    "110111110": ["forest_east"],
    "111110110": ["forest_east"],
    "111110111": ["forest_east"],

    "011011111": ["forest_west"],
    "011111011": ["forest_west"],
    "111011011": ["forest_west"],
    "111011111": ["forest_west"],

    "011111111": ["forest_corner_inv_north_west"],
    "110111111": ["forest_corner_inv_north_east"],
    "111111110": ["forest_corner_inv_south_east"],
    "111111011": ["forest_corner_inv_south_west"],

    "110111011": ["forest_diag"],
    "011111110": ["forest_diag_anti"],

    # 3 or less
    "000010000": ["tree_1", "tree_2", "tree_3"],
    "000010001": ["tree_1", "tree_2", "tree_3"],
    "000010010": ["tree_1", "tree_2", "tree_3"],
    "000010011": ["tree_1", "tree_2", "tree_3"],
    "000010100": ["tree_1", "tree_2", "tree_3"],
    "000010101": ["tree_1", "tree_2", "tree_3"],
    "000010110": ["tree_1", "tree_2", "tree_3"],
    "000011000": ["tree_1", "tree_2", "tree_3"],
    "000011001": ["tree_1", "tree_2", "tree_3"],
    "000011010": ["tree_1", "tree_2", "tree_3"],
    "000011100": ["tree_1", "tree_2", "tree_3"],
    "000110000": ["tree_1", "tree_2", "tree_3"],
    "000110001": ["tree_1", "tree_2", "tree_3"],
    "000110010": ["tree_1", "tree_2", "tree_3"],
    "000110100": ["tree_1", "tree_2", "tree_3"],
    "000111000": ["tree_1", "tree_2", "tree_3"],
    "001010000": ["tree_1", "tree_2", "tree_3"],
    "001010001": ["tree_1", "tree_2", "tree_3"],
    "001010010": ["tree_1", "tree_2", "tree_3"],
    "001010100": ["tree_1", "tree_2", "tree_3"],
    "001011000": ["tree_1", "tree_2", "tree_3"],
    "001110000": ["tree_1", "tree_2", "tree_3"],
    "010010000": ["tree_1", "tree_2", "tree_3"],
    "010010001": ["tree_1", "tree_2", "tree_3"],
    "010010010": ["tree_1", "tree_2", "tree_3"],
    "010010100": ["tree_1", "tree_2", "tree_3"],
    "010011000": ["tree_1", "tree_2", "tree_3"],
    "010110000": ["tree_1", "tree_2", "tree_3"],
    "011010000": ["tree_1", "tree_2", "tree_3"],
    "100010000": ["tree_1", "tree_2", "tree_3"],
    "100010001": ["tree_1", "tree_2", "tree_3"],
    "100010010": ["tree_1", "tree_2", "tree_3"],
    "100010100": ["tree_1", "tree_2", "tree_3"],
    "100011000": ["tree_1", "tree_2", "tree_3"],
    "100110000": ["tree_1", "tree_2", "tree_3"],
    "101010000": ["tree_1", "tree_2", "tree_3"],
    "110010000": ["tree_1", "tree_2", "tree_3"],

    # exactly 4 without the corners
    "000010111": ["tree_1", "tree_2", "tree_3"],
    "000011101": ["tree_1", "tree_2", "tree_3"],
    "000011110": ["tree_1", "tree_2", "tree_3"],
    "000110011": ["tree_1", "tree_2", "tree_3"],
    "000110101": ["tree_1", "tree_2", "tree_3"],
    "000111001": ["tree_1", "tree_2", "tree_3"],
    "000111010": ["tree_1", "tree_2", "tree_3"],
    "000111100": ["tree_1", "tree_2", "tree_3"],
    "001010011": ["tree_1", "tree_2", "tree_3"],
    "001010101": ["tree_1", "tree_2", "tree_3"],
    "001010110": ["tree_1", "tree_2", "tree_3"],
    "001011001": ["tree_1", "tree_2", "tree_3"],
    "001011010": ["tree_1", "tree_2", "tree_3"],
    "001011100": ["tree_1", "tree_2", "tree_3"],
    "001110001": ["tree_1", "tree_2", "tree_3"],
    "001110010": ["tree_1", "tree_2", "tree_3"],
    "001110100": ["tree_1", "tree_2", "tree_3"],
    "001111000": ["tree_1", "tree_2", "tree_3"],
    "010010011": ["tree_1", "tree_2", "tree_3"],
    "010010101": ["tree_1", "tree_2", "tree_3"],
    "010010110": ["tree_1", "tree_2", "tree_3"],
    "010011001": ["tree_1", "tree_2", "tree_3"],
    "010011010": ["tree_1", "tree_2", "tree_3"],
    "010011100": ["tree_1", "tree_2", "tree_3"],
    "010110001": ["tree_1", "tree_2", "tree_3"],
    "010110010": ["tree_1", "tree_2", "tree_3"],
    "010110100": ["tree_1", "tree_2", "tree_3"],
    "010111000": ["tree_1", "tree_2", "tree_3"],
    "011010001": ["tree_1", "tree_2", "tree_3"],
    "011010010": ["tree_1", "tree_2", "tree_3"],
    "011010100": ["tree_1", "tree_2", "tree_3"],
    "011110000": ["tree_1", "tree_2", "tree_3"],
    "100010011": ["tree_1", "tree_2", "tree_3"],
    "100010101": ["tree_1", "tree_2", "tree_3"],
    "100010110": ["tree_1", "tree_2", "tree_3"],
    "100011001": ["tree_1", "tree_2", "tree_3"],
    "100011010": ["tree_1", "tree_2", "tree_3"],
    "100011100": ["tree_1", "tree_2", "tree_3"],
    "100110001": ["tree_1", "tree_2", "tree_3"],
    "100110010": ["tree_1", "tree_2", "tree_3"],
    "100110100": ["tree_1", "tree_2", "tree_3"],
    "100111000": ["tree_1", "tree_2", "tree_3"],
    "101010001": ["tree_1", "tree_2", "tree_3"],
    "101010010": ["tree_1", "tree_2", "tree_3"],
    "101010100": ["tree_1", "tree_2", "tree_3"],
    "101011000": ["tree_1", "tree_2", "tree_3"],
    "101110000": ["tree_1", "tree_2", "tree_3"],
    "110010001": ["tree_1", "tree_2", "tree_3"],
    "110010010": ["tree_1", "tree_2", "tree_3"],
    "110010100": ["tree_1", "tree_2", "tree_3"],
    "110011000": ["tree_1", "tree_2", "tree_3"],
    "111010000": ["tree_1", "tree_2", "tree_3"],

    # exactly 5 without the ones grouped together
    "000111101": ["tree_1", "tree_2", "tree_3"],
    "001010111": ["tree_1", "tree_2", "tree_3"],
    "001011101": ["tree_1", "tree_2", "tree_3"],
    "001011110": ["tree_1", "tree_2", "tree_3"],
    "001110011": ["tree_1", "tree_2", "tree_3"],
    "001110101": ["tree_1", "tree_2", "tree_3"],
    "001111001": ["tree_1", "tree_2", "tree_3"],
    "001111010": ["tree_1", "tree_2", "tree_3"],
    "001111100": ["tree_1", "tree_2", "tree_3"],
    "010010111": ["tree_1", "tree_2", "tree_3"],
    "010011101": ["tree_1", "tree_2", "tree_3"],
    "010011110": ["tree_1", "tree_2", "tree_3"],
    "010110011": ["tree_1", "tree_2", "tree_3"],
    "010110101": ["tree_1", "tree_2", "tree_3"],
    "010111001": ["tree_1", "tree_2", "tree_3"],
    "010111010": ["tree_1", "tree_2", "tree_3"],
    "010111100": ["tree_1", "tree_2", "tree_3"],
    "011010011": ["tree_1", "tree_2", "tree_3"],
    "011010101": ["tree_1", "tree_2", "tree_3"],
    "011010110": ["tree_1", "tree_2", "tree_3"],
    "011110001": ["tree_1", "tree_2", "tree_3"],
    "011110010": ["tree_1", "tree_2", "tree_3"],
    "011110100": ["tree_1", "tree_2", "tree_3"],
    "100010111": ["tree_1", "tree_2", "tree_3"],
    "100011101": ["tree_1", "tree_2", "tree_3"],
    "100011110": ["tree_1", "tree_2", "tree_3"],
    "100110011": ["tree_1", "tree_2", "tree_3"],
    "100110101": ["tree_1", "tree_2", "tree_3"],
    "100111001": ["tree_1", "tree_2", "tree_3"],
    "100111010": ["tree_1", "tree_2", "tree_3"],
    "100111100": ["tree_1", "tree_2", "tree_3"],
    "101010011": ["tree_1", "tree_2", "tree_3"],
    "101010101": ["tree_1", "tree_2", "tree_3"],
    "101010110": ["tree_1", "tree_2", "tree_3"],
    "101011001": ["tree_1", "tree_2", "tree_3"],
    "101011010": ["tree_1", "tree_2", "tree_3"],
    "101011100": ["tree_1", "tree_2", "tree_3"],
    "101110001": ["tree_1", "tree_2", "tree_3"],
    "101110010": ["tree_1", "tree_2", "tree_3"],
    "101110100": ["tree_1", "tree_2", "tree_3"],
    "101111000": ["tree_1", "tree_2", "tree_3"],
    "110010011": ["tree_1", "tree_2", "tree_3"],
    "110010101": ["tree_1", "tree_2", "tree_3"],
    "110010110": ["tree_1", "tree_2", "tree_3"],
    "110011001": ["tree_1", "tree_2", "tree_3"],
    "110011010": ["tree_1", "tree_2", "tree_3"],
    "110011100": ["tree_1", "tree_2", "tree_3"],
    "111010001": ["tree_1", "tree_2", "tree_3"],
    "111010010": ["tree_1", "tree_2", "tree_3"],
    "111010100": ["tree_1", "tree_2", "tree_3"],

    # 6 or more
    "001111101": ["tree_1", "tree_2", "tree_3"],
    "010111101": ["tree_1", "tree_2", "tree_3"],
    "011010111": ["tree_1", "tree_2", "tree_3"],
    "011110011": ["tree_1", "tree_2", "tree_3"],
    "011110101": ["tree_1", "tree_2", "tree_3"],
    "100111101": ["tree_1", "tree_2", "tree_3"],
    "101010111": ["tree_1", "tree_2", "tree_3"],
    "101011101": ["tree_1", "tree_2", "tree_3"],
    "101011110": ["tree_1", "tree_2", "tree_3"],
    "101110011": ["tree_1", "tree_2", "tree_3"],
    "101110101": ["tree_1", "tree_2", "tree_3"],
    "101111001": ["tree_1", "tree_2", "tree_3"],
    "101111010": ["tree_1", "tree_2", "tree_3"],
    "101111100": ["tree_1", "tree_2", "tree_3"],
    "101111101": ["tree_1", "tree_2", "tree_3"],
    "110010111": ["tree_1", "tree_2", "tree_3"],
    "110011101": ["tree_1", "tree_2", "tree_3"],
    "110011110": ["tree_1", "tree_2", "tree_3"],
    "111010011": ["tree_1", "tree_2", "tree_3"],
    "111010101": ["tree_1", "tree_2", "tree_3"],
    "111010110": ["tree_1", "tree_2", "tree_3"],
    "111010111": ["tree_1", "tree_2", "tree_3"],
}


def generate_chunk(
    terrain_noise: List[Tuple[float, PerlinNoise]],
    biome_noise: List[Tuple[float, PerlinNoise]],
    forest_threshold: float,
    land_heights: LandHeights,
    chunk: (int, int),
    tileset: Dict[Name, Tile],
    z: float = 0.0,
) -> List[Cell]:
    chunk_i, chunk_j = chunk
    chunk_i, chunk_j = chunk_i * CHUNK_SIZE, chunk_j * CHUNK_SIZE

    terrain_noise_values = [
        [
            sum(
                weight * n([i / CHUNK_SIZE, j / CHUNK_SIZE, z])
                for weight, n in terrain_noise
            )
            for j in range(chunk_j, chunk_j + CHUNK_SIZE + 3)
        ]
        for i in range(chunk_i, chunk_i + CHUNK_SIZE + 3)
    ]

    biome_noise_values = [
        [
            sum(
                weight * n([i / CHUNK_SIZE, j / CHUNK_SIZE, z])
                for weight, n in biome_noise
            )
            for j in range(chunk_j, chunk_j + CHUNK_SIZE + 2)
        ]
        for i in range(chunk_i, chunk_i + CHUNK_SIZE + 2)
    ]

    tlt = lambda x: to_land_type(x, land_heights=land_heights)

    cells = []
    incomplete, bad_tile = False, None
    for i in range(1, CHUNK_SIZE + 1):
        for j in range(1, CHUNK_SIZE + 1):
            nw = tlt(terrain_noise_values[i][j])
            ne = tlt(terrain_noise_values[i][j + 1])
            sw = tlt(terrain_noise_values[i + 1][j])
            se = tlt(terrain_noise_values[i + 1][j + 1])
            key = ''.join([nw.value, ne.value, sw.value, se.value])

            bg, fg = choice(TILEMAP.get(key, [("spell_red", None)]))

            valid = [LT.GRASS, LT.ROCK]
            forest = [
                (
                    biome_noise_values[a][b] > forest_threshold and
                    tlt(terrain_noise_values[a][b]) ==
                    tlt(terrain_noise_values[a][b + 1]) ==
                    tlt(terrain_noise_values[a + 1][b]) ==
                    tlt(terrain_noise_values[a + 1][b + 1]) and
                    tlt(terrain_noise_values[a][b]) in valid
                )
                for a, b in [
                    (i - 1, j - 1), (i - 1, j), (i - 1, j + 1),
                    (i, j - 1),     (i, j),     (i, j + 1),
                    (i + 1, j - 1), (i + 1, j), (i + 1, j + 1),
                ]
            ]

            if forest[4]:
                fkey = ''.join(map(str, map(int, forest)))
                fg = choice(FOREST_TILEMAP.get(fkey, ["spell_red"]))

            if key not in TILEMAP:
                incomplete, bad_tile = True, (nw, ne, sw, se)

            cells.append(Cell(
                i - 1, j - 1,
                background=tileset[bg],
                foreground=tileset.get(fg),
            ))

    if incomplete:
        warning(f"generation is incomplete with {bad_tile}")

    return cells


def take_screenshot(screen: pygame.surface.Surface):
    out = f"{time_ns()}.png"
    image = np.transpose(pygame.surfarray.array3d(screen), (1, 0, 2))
    Image.fromarray(image).save(out)
    info(f"window saved in [purple]{out}[/purple]")

    w, h = screen.get_size()
    pygame.draw.rect(screen, RED, (0, 0, w, h), width=10)
    pygame.display.flip()


def handle_events() -> (bool, bool, (int, int), bool, bool):
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (
            event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
        ):
            return False, False, None, False, False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F2:
                return True, True, None, False, False
            elif event.key == pygame.K_h:
                return True, False, (0, -1), False, False
            elif event.key == pygame.K_l:
                return True, False, (0, +1), False, False
            elif event.key == pygame.K_j:
                return True, False, (+1, 0), False, False
            elif event.key == pygame.K_k:
                return True, False, (-1, 0), False, False
            elif event.key == pygame.K_F3:
                return True, False, None, True, False
        elif event.type == pygame.WINDOWRESIZED:
            return True, False, None, False, True

    return True, False, None, False, False


def blit(
    screen: pygame.surface.Surface,
    chunks: Dict[Tuple[int, int], List[Cell]],
    animations: List[Animation],
    pos: (float, float),
    *,
    t: int,
    s: int,
    debug: bool = False,
):
    w, h = screen.get_size()
    dx, dy = pos

    for (pi, pj), cells in chunks.items():
        for c in cells:
            try:
                tile = get_animation_steps(c.background.id, animations)[
                    (t // ANIMATION_INV_SPEED) % ANIMATION_SEQUENCE_LEN
                ].tile
            except Exception:
                tile = c.background
            cell_pos = (
                w / 2 + (pj * CHUNK_SIZE + c.j) * s - dx,
                h / 2 + (pi * CHUNK_SIZE + c.i) * s - dy,
            )
            screen.blit(pygame.transform.scale(tile.image, (s, s)), cell_pos)
            if c.foreground is not None:
                screen.blit(
                    pygame.transform.scale(c.foreground.image, (s, s)),
                    cell_pos,
                )

    if debug:
        chunk_s = CHUNK_SIZE * s
        # draw a slightly transparent grid on top of the chunks
        for (pi, pj), _ in chunks.items():
            rect = (
                w / 2 + pj * chunk_s - dx,
                h / 2 + pi * chunk_s - dy,
                chunk_s, chunk_s
            )
            color = BLACK + (64,)
            shape_surf = pygame.Surface(
                pygame.Rect(rect).size, pygame.SRCALPHA
            )
            pygame.draw.rect(shape_surf, color, shape_surf.get_rect(), width=1)
            screen.blit(shape_surf, rect)

            text = font.render(f"({pi}, {pj})", False, color)
            screen.blit(text, rect[:2])

    pygame.draw.circle(screen, RED, (w / 2, h / 2), 10)


def blit_debug_pannel(
    screen: pygame.surface.Surface,
    font: pygame.font.SysFont,
    clock: pygame.time.Clock,
    chunks: Dict[Tuple[int, int], List[Cell]],
    chunks_to_load: List[Tuple[int, int]],
    *,
    pos: (int, int),
):
    msg = (
        f"running at {int(clock.get_fps())} FPS | "
        f"chunks: {len(chunks)} / {len(chunks_to_load)}"
    )
    text = font.render(msg, False, GREY, BLACK)
    x, y = pos
    screen.blit(text, (x, y - text.get_height()))


def to_chunk_space(pos: (float, float)) -> (int, int):
    x, y = pos
    return (
        int((x // tile_size) // CHUNK_SIZE),
        int((y // tile_size) // CHUNK_SIZE),
    )


def chunks_around(
    pos: (float, float), *, h: int, w: int
) -> List[Tuple[int, int]]:
    pj, pi = to_chunk_space(pos)
    h = h // 2 + 1
    w = w // 2 + 1
    return [(pi + i, pj + j) for i in range(-h, h) for j in range(-w, w)]


def is_number(obj: Any) -> bool:
    return isinstance(obj, float) or isinstance(obj, int)


def noise_as_json():
    def type_func(val: str) -> List[NoiseOctave]:
        try:
            noise = json.loads(val)
        except Exception:
            raise Exception("value given to --noise is not valid JSON")

        if not isinstance(noise, list):
            raise Exception("not a list")
        if len(noise) == 0:
            raise Exception("empty list")

        for i, x in enumerate(noise):
            if not isinstance(x, dict):
                raise Exception(
                    f"$.{i} should be a dict, found {type(x).__name__}"
                )

            expected = ["amplitude", "octaves"]
            if sorted(x.keys()) != expected:
                raise Exception(
                    f"$.{i} has bad keys, expected {expected}, found {list(x.keys())}"
                )
            if not is_number(x["amplitude"]):
                t = type(x['amplitude']).__name__
                raise Exception(
                    f"$.{i}.amplitude should be a number, found {t}"
                )
            if not is_number(x["octaves"]):
                t = type(x['octaves']).__name__
                raise Exception(
                    f"$.{i}.octaves should be a number, found {t}"
                )
        return noise
    return type_func


def land_heights_as_json():
    def type_func(val: str) -> LandHeights:
        try:
            lt = json.loads(val)
        except Exception:
            raise Exception("value given to --land-heights is not valid JSON")

        if not isinstance(lt, dict):
            raise Exception(f"should be a dict, found {type(lt).__name__}")

        expected = ["ROCK", "GRASS", "WATER"]
        if sorted(lt.keys()) != sorted(expected):
            raise Exception(
                f"bad keys, expected {expected}, found {list(lt.keys())}"
            )

        return {k: float(v) for k, v in lt.items()}
    return type_func


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--frame-rate", "-f", type=int, default=30)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--terrain-noise", type=noise_as_json(), required=True)
    parser.add_argument("--biome-noise", type=noise_as_json(), required=True)
    parser.add_argument("--forest-threshold", type=float, default=0.0)
    parser.add_argument("--land-heights", type=land_heights_as_json(), required=True)
    args = parser.parse_args()

    pygame.init()
    pygame.font.init()
    font = pygame.font.SysFont("mononokinerdfont", 30)
    tile_size = 48
    window_size = (1600, 900)
    screen = pygame.display.set_mode(window_size, pygame.RESIZABLE)
    clock = pygame.time.Clock()
    dt = 0

    tiles, animations, _ = load_tileset(Path("../../punyworld.json"))

    terrain_noise = [
        (n["amplitude"], PerlinNoise(octaves=n["octaves"], seed=args.seed))
        for n in args.terrain_noise
    ]
    biome_noise = [
        (n["amplitude"], PerlinNoise(octaves=n["octaves"], seed=args.seed))
        for n in args.biome_noise
    ]

    chunks_w, chunks_h = to_chunk_space(screen.get_size())

    w, h = window_size
    pos = (0, 0)
    chunks = {}

    chunks_to_load = chunks_around(pos, h=chunks_h, w=chunks_w)

    debug = False

    t = 0
    running = True
    while running:
        (
            running, screenshot, move, toggle_debug, window_resized
        ) = handle_events()

        if window_resized:
            info(f"resizing window to {screen.get_size()}")
            chunks_w, chunks_h = to_chunk_space(screen.get_size())

            for c in chunks_around(pos, h=chunks_h, w=chunks_w):
                if c not in chunks and c not in chunks_to_load:
                    chunks_to_load.append(c)

        if screenshot:
            take_screenshot(screen)

        if toggle_debug:
            debug = not debug

        if move is not None:
            mi, mj = move
            pos = (pos[0] + mj * 64, pos[1] + mi * 64)

            for c in chunks_around(pos, h=chunks_h, w=chunks_w):
                if c not in chunks and c not in chunks_to_load:
                    chunks_to_load.append(c)

        if len(chunks_to_load) > 0:
            new_chunk = chunks_to_load.pop(0)
            info(f"generating chunk {new_chunk}...", end=' ')
            t = time_ns()
            chunks[new_chunk] = generate_chunk(
                terrain_noise,
                biome_noise,
                args.forest_threshold,
                args.land_heights,
                new_chunk,
                tiles,
            )
            rich.print(f"done in {round((time_ns() - t) / 1_000_000, 2)} ms")

        screen.fill(BLACK)

        blit(
            screen,
            {
                c: chunks[c]
                for c in chunks_around(pos, h=chunks_h, w=chunks_w)
                if c in chunks
            },
            animations,
            pos,
            t=t,
            s=tile_size,
            debug=debug,
        )

        if debug:
            _, h = screen.get_size()
            blit_debug_pannel(
                screen, font, clock, chunks, chunks_to_load, pos=(10, h - 10)
            )

        pygame.display.flip()
        dt = clock.tick(args.frame_rate) / 1000

        t += 1

    pygame.quit()
