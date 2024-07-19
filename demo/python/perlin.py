from perlin_noise import PerlinNoise
from typing import List, Any, Dict
import pygame
import argparse
from dataclasses import dataclass
from rich import print
from time import time_ns
import json
from tileset import load_tileset, Tile, Name
from pathlib import Path
from enum import Enum
from random import choice
from tqdm import trange

BLACK = (0, 0, 0)

# values need to be sorted from highest to lowest
LAND_TYPES = {
    "ROCK": 0.1,
    "GRASS": 0.0,
    "WATER": float("-inf"),
}
LandType = Enum("LandType", list(LAND_TYPES.keys()))


@dataclass
class Cell:
    i: int
    j: int
    background: Tile
    foreground: Tile | None


def to_land_type(x: float) -> LandType:
    for k, v in LAND_TYPES.items():
        if x > v:
            return LandType._member_map_[k]


def hash_lt(nw: LandType, ne: LandType, sw: LandType, se: LandType) -> int:
    n = len(LAND_TYPES.keys())
    return nw.value + n * ne.value + n ** 2 * sw.value + n ** 3 * se.value


LT = LandType
TILEMAP = {
    # iiii
    hash_lt(LT.GRASS, LT.GRASS, LT.GRASS, LT.GRASS): [
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
    hash_lt(LT.WATER, LT.WATER, LT.WATER, LT.WATER): [("water", None)],
    hash_lt(LT.ROCK, LT.ROCK, LT.ROCK, LT.ROCK): [("grass_1", None)],

    # iiij
    hash_lt(LT.GRASS, LT.GRASS, LT.GRASS, LT.WATER): [("river_corner_north_west", None)],  # noqa: E501
    hash_lt(LT.GRASS, LT.GRASS, LT.WATER, LT.GRASS): [("river_corner_north_east", None)],  # noqa: E501
    hash_lt(LT.GRASS, LT.WATER, LT.GRASS, LT.GRASS): [("river_corner_south_west", None)],  # noqa: E501
    hash_lt(LT.WATER, LT.GRASS, LT.GRASS, LT.GRASS): [("river_corner_south_east", None)],  # noqa: E501

    hash_lt(LT.WATER, LT.WATER, LT.WATER, LT.GRASS): [("river_inv_corner_south_east", None)],  # noqa: E501
    hash_lt(LT.WATER, LT.WATER, LT.GRASS, LT.WATER): [("river_inv_corner_south_west", None)],  # noqa: E501
    hash_lt(LT.WATER, LT.GRASS, LT.WATER, LT.WATER): [("river_inv_corner_north_east", None)],  # noqa: E501
    hash_lt(LT.GRASS, LT.WATER, LT.WATER, LT.WATER): [("river_inv_corner_north_west", None)],  # noqa: E501

    hash_lt(LT.GRASS, LT.GRASS, LT.GRASS, LT.ROCK): [("rock_north_west", None)],  # noqa: E501
    hash_lt(LT.GRASS, LT.GRASS, LT.ROCK, LT.GRASS): [("rock_north_east", None)],  # noqa: E501
    hash_lt(LT.GRASS, LT.ROCK, LT.GRASS, LT.GRASS): [("rock_south_west", None)],  # noqa: E501
    hash_lt(LT.ROCK, LT.GRASS, LT.GRASS, LT.GRASS): [("rock_south_east", None)],  # noqa: E501

    hash_lt(LT.WATER, LT.WATER, LT.WATER, LT.ROCK): [("water", "rock_north_west_2")],  # noqa: E501
    hash_lt(LT.WATER, LT.WATER, LT.ROCK, LT.WATER): [("water", "rock_north_east_2")],  # noqa: E501
    hash_lt(LT.WATER, LT.ROCK, LT.WATER, LT.WATER): [("water", "rock_south_west_2")],  # noqa: E501
    hash_lt(LT.ROCK, LT.WATER, LT.WATER, LT.WATER): [("water", "rock_south_east_2")],  # noqa: E501

    hash_lt(LT.ROCK, LT.ROCK, LT.ROCK, LT.WATER): [("water", "rock_corner_south_east_2")],  # noqa: E501
    hash_lt(LT.ROCK, LT.ROCK, LT.WATER, LT.ROCK): [("water", "rock_corner_south_west_2")],  # noqa: E501
    hash_lt(LT.ROCK, LT.WATER, LT.ROCK, LT.ROCK): [("water", "rock_corner_north_east_2")],  # noqa: E501
    hash_lt(LT.WATER, LT.ROCK, LT.ROCK, LT.ROCK): [("water", "rock_corner_north_west_2")],  # noqa: E501

    hash_lt(LT.ROCK, LT.ROCK, LT.ROCK, LT.GRASS): [("rock_corner_south_east", None)],  # noqa: E501
    hash_lt(LT.ROCK, LT.ROCK, LT.GRASS, LT.ROCK): [("rock_corner_south_west", None)],  # noqa: E501
    hash_lt(LT.ROCK, LT.GRASS, LT.ROCK, LT.ROCK): [("rock_corner_north_east", None)],  # noqa: E501
    hash_lt(LT.GRASS, LT.ROCK, LT.ROCK, LT.ROCK): [("rock_corner_north_west", None)],  # noqa: E501

    # iijj
    hash_lt(LT.WATER, LT.GRASS, LT.GRASS, LT.WATER): [("river_diag_anti", None)],  # noqa: E501
    hash_lt(LT.GRASS, LT.WATER, LT.WATER, LT.GRASS): [("river_diag", None)],
    hash_lt(LT.GRASS, LT.GRASS, LT.WATER, LT.WATER): [("river_north", None)],
    hash_lt(LT.GRASS, LT.WATER, LT.GRASS, LT.WATER): [("river_west", None)],
    hash_lt(LT.WATER, LT.GRASS, LT.WATER, LT.GRASS): [("river_east", None)],
    hash_lt(LT.WATER, LT.WATER, LT.GRASS, LT.GRASS): [("river_south", None)],

    hash_lt(LT.WATER, LT.ROCK, LT.ROCK, LT.WATER): [("water", "rock_diag_anti_2")],  # noqa: E501
    hash_lt(LT.ROCK, LT.WATER, LT.WATER, LT.ROCK): [("water", "rock_diag_2")],
    hash_lt(LT.ROCK, LT.ROCK, LT.WATER, LT.WATER): [("water", "rock_south_2")],
    hash_lt(LT.ROCK, LT.WATER, LT.ROCK, LT.WATER): [("water", "rock_east_2")],
    hash_lt(LT.WATER, LT.ROCK, LT.WATER, LT.ROCK): [("water", "rock_west_2")],
    hash_lt(LT.WATER, LT.WATER, LT.ROCK, LT.ROCK): [("water", "rock_north_2")],

    hash_lt(LT.ROCK, LT.GRASS, LT.GRASS, LT.ROCK): [("rock_diag", None)],
    hash_lt(LT.GRASS, LT.ROCK, LT.ROCK, LT.GRASS): [("rock_diag_anti", None)],
    hash_lt(LT.GRASS, LT.GRASS, LT.ROCK, LT.ROCK): [("rock_north", None)],
    hash_lt(LT.GRASS, LT.ROCK, LT.GRASS, LT.ROCK): [("rock_west", None)],
    hash_lt(LT.ROCK, LT.GRASS, LT.ROCK, LT.GRASS): [("rock_east", None)],
    hash_lt(LT.ROCK, LT.ROCK, LT.GRASS, LT.GRASS): [("rock_south", None)],

    # iijk
    hash_lt(LT.WATER, LT.WATER, LT.GRASS, LT.ROCK): [("river_south", "rock_north_west_2")],  # noqa: E501
    hash_lt(LT.GRASS, LT.WATER, LT.ROCK, LT.WATER): [("river_west", "rock_north_east_2")],  # noqa: E501
    hash_lt(LT.ROCK, LT.GRASS, LT.WATER, LT.WATER): [("river_north", "rock_south_east_2")],  # noqa: E501
    hash_lt(LT.WATER, LT.ROCK, LT.WATER, LT.GRASS): [("river_east", "rock_south_west_2")],  # noqa: E501

    hash_lt(LT.WATER, LT.WATER, LT.ROCK, LT.GRASS): [("river_south", "rock_north_east_2")],  # noqa: E501
    hash_lt(LT.ROCK, LT.WATER, LT.GRASS, LT.WATER): [("river_west", "rock_south_east_2")],  # noqa: E501
    hash_lt(LT.GRASS, LT.ROCK, LT.WATER, LT.WATER): [("river_north", "rock_south_west_2")],  # noqa: E501
    hash_lt(LT.WATER, LT.GRASS, LT.WATER, LT.ROCK): [("river_east", "rock_north_west_2")],  # noqa: E501

    hash_lt(LT.ROCK, LT.ROCK, LT.WATER, LT.GRASS): [("river_east", "rock_south_2")],  # noqa: E501
    hash_lt(LT.WATER, LT.ROCK, LT.GRASS, LT.ROCK): [("river_corner_south_east", "rock_west_2")],  # noqa: E501
    hash_lt(LT.GRASS, LT.WATER, LT.ROCK, LT.ROCK): [("river_west", "rock_north_2")],  # noqa: E501
    hash_lt(LT.ROCK, LT.GRASS, LT.ROCK, LT.WATER): [("river_corner_north_west", "rock_east_2")],  # noqa: E501

    hash_lt(LT.ROCK, LT.ROCK, LT.GRASS, LT.WATER): [("river_corner_north_west", "rock_south_2")],  # noqa: E501
    hash_lt(LT.GRASS, LT.ROCK, LT.WATER, LT.ROCK): [("river_corner_north_east", "rock_west_2")],  # noqa: E501
    hash_lt(LT.WATER, LT.GRASS, LT.ROCK, LT.ROCK): [("river_east", "rock_north_2")],  # noqa: E501
    hash_lt(LT.ROCK, LT.WATER, LT.ROCK, LT.GRASS): [("river_south", "rock_east_2")],  # noqa: E501

    hash_lt(LT.GRASS, LT.GRASS, LT.WATER, LT.ROCK): [("river_corner_north_east", "rock_north_west_2")],  # noqa: E501
    hash_lt(LT.WATER, LT.GRASS, LT.ROCK, LT.GRASS): [("river_corner_south_east", "rock_north_east_2")],  # noqa: E501
    hash_lt(LT.ROCK, LT.WATER, LT.GRASS, LT.GRASS): [("river_corner_south_west", "rock_south_east_2")],  # noqa: E501
    hash_lt(LT.GRASS, LT.ROCK, LT.GRASS, LT.WATER): [("river_corner_north_west", "rock_south_west_2")],  # noqa: E501

    hash_lt(LT.GRASS, LT.GRASS, LT.ROCK, LT.WATER): [("river_corner_north_west", "rock_north_east_2")],  # noqa: E501
    hash_lt(LT.ROCK, LT.GRASS, LT.WATER, LT.GRASS): [("river_corner_north_east", "rock_south_east_2")],  # noqa: E501
    hash_lt(LT.WATER, LT.ROCK, LT.GRASS, LT.GRASS): [("river_corner_south_east", "rock_south_west_2")],  # noqa: E501
    hash_lt(LT.GRASS, LT.WATER, LT.GRASS, LT.ROCK): [("river_corner_south_west", "rock_north_west_2")],  # noqa: E501

    hash_lt(LT.GRASS, LT.WATER, LT.ROCK, LT.GRASS): [("river_corner_south_west", "rock_north_east_2")],  # noqa: E501
    hash_lt(LT.ROCK, LT.GRASS, LT.GRASS, LT.WATER): [("river_corner_north_west", "rock_south_east_2")],  # noqa: E501
    hash_lt(LT.GRASS, LT.ROCK, LT.WATER, LT.GRASS): [("river_corner_north_east", "rock_south_west_2")],  # noqa: E501
    hash_lt(LT.WATER, LT.GRASS, LT.GRASS, LT.ROCK): [("river_corner_south_east", "rock_north_west_2")],  # noqa: E501

    hash_lt(LT.WATER, LT.GRASS, LT.ROCK, LT.WATER): [("river_inv_corner_north_east", "rock_north_east_2")],  # noqa: E501
    hash_lt(LT.ROCK, LT.WATER, LT.WATER, LT.GRASS): [("river_inv_corner_south_east", "rock_south_east_2")],  # noqa: E501
    hash_lt(LT.WATER, LT.ROCK, LT.GRASS, LT.WATER): [("river_inv_corner_south_west", "rock_south_west_2")],  # noqa: E501
    hash_lt(LT.GRASS, LT.WATER, LT.WATER, LT.ROCK): [("river_inv_corner_north_west", "rock_north_west_2")],  # noqa: E501

    hash_lt(LT.ROCK, LT.WATER, LT.GRASS, LT.ROCK): [("river_corner_south_west", "rock_diag_2")],  # noqa: E501
    hash_lt(LT.GRASS, LT.ROCK, LT.ROCK, LT.WATER): [("river_corner_north_west", "rock_diag_anti_2")],  # noqa: E501
    hash_lt(LT.ROCK, LT.GRASS, LT.WATER, LT.ROCK): [("river_corner_north_east", "rock_diag_2")],  # noqa: E501
    hash_lt(LT.WATER, LT.ROCK, LT.ROCK, LT.GRASS): [("river_corner_south_east", "rock_diag_anti_2")],  # noqa: E501
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


def generate_cells(
    noise,
    noise_on_top,
    w: int,
    h: int,
    tileset: Dict[Name, Tile],
    z: float = 0.0,
) -> List[Cell]:
    t = time_ns()

    print("[bold green]INFO[/bold green]: starting generating cells")

    noise_values = [
        [
            sum(
                weight * n([i / (h + 1), j / (w + 1), z])
                for weight, n in noise
            )
            for j in range(w + 2)
        ]
        for i in trange(h + 2)
    ]

    noise_on_top_values = [
        [
            sum(
                weight * n([i / (h + 1), j / (w + 1), z])
                for weight, n in noise_on_top
            )
            for j in range(w + 2)
        ]
        for i in trange(h + 2)
    ]

    cells = []
    incomplete, bad_tile = False, None
    for i in range(1, h):
        for j in range(1, w):
            nw = to_land_type(noise_values[i][j])
            ne = to_land_type(noise_values[i][j + 1])
            sw = to_land_type(noise_values[i + 1][j])
            se = to_land_type(noise_values[i + 1][j + 1])
            key = hash_lt(nw, ne, sw, se)

            bg, fg = choice(TILEMAP.get(key, [("spell_red", None)]))

            valid = [LT.GRASS, LT.ROCK]
            forest = [
                (
                    noise_on_top_values[a][b] > 0.0 and
                    to_land_type(noise_values[a][b]) ==
                    to_land_type(noise_values[a][b + 1]) ==
                    to_land_type(noise_values[a + 1][b]) ==
                    to_land_type(noise_values[a + 1][b + 1]) and
                    to_land_type(noise_values[a][b]) in valid
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
                i, j,
                background=tileset[bg],
                foreground=tileset.get(fg),
            ))

    print(f"[bold green]INFO[/bold green]: done in {(time_ns() - t) / 1_000_000} ms")
    if incomplete:
        print(f"[bold yellow]WARNING[/bold yellow]: generation is incomplete with {bad_tile}")

    return cells


def handle_events() -> (bool, bool):
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (
            event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
        ):
            return False, None
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                return True, True

    return True, False


def show(screen: pygame.surface.Surface, cells: List[Cell], s: int):
    screen.fill(BLACK)

    for c in cells:
        screen.blit(
            pygame.transform.scale(c.background.image, (s, s)),
            (c.j * s, c.i * s),
        )
        if c.foreground is not None:
            screen.blit(
                pygame.transform.scale(c.foreground.image, (s, s)),
                (c.j * s, c.i * s),
            )

    pygame.display.flip()


def is_number(obj: Any):
    return isinstance(obj, float) or isinstance(obj, int)


def noise_as_json():
    def type_func(val: str) -> dict:
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--map-width", "-W", type=int, required=True)
    parser.add_argument("--map-height", "-H", type=int, required=True)
    parser.add_argument("--tile-size", "-s", type=int, required=True)
    parser.add_argument("--frame-rate", "-f", type=int, default=30)
    parser.add_argument("--change-with-time", "-t", type=float)
    parser.add_argument("--show-fps", action="store_true")
    parser.add_argument("--seed", type=int)
    parser.add_argument("--noise", type=noise_as_json(), required=True)
    parser.add_argument("--noise-on-top", type=noise_as_json(), required=True)
    args = parser.parse_args()

    pygame.init()
    pygame.font.init()
    screen = pygame.display.set_mode((
        args.map_width * args.tile_size,
        args.map_height * args.tile_size,
    ))
    clock = pygame.time.Clock()
    dt = 0

    tiles, _, _ = load_tileset(Path("../../punyworld.json"))

    noise = [
        (n["amplitude"], PerlinNoise(octaves=n["octaves"], seed=args.seed))
        for n in args.noise
    ]
    noise_on_top = [
        (n["amplitude"], PerlinNoise(octaves=n["octaves"], seed=args.seed))
        for n in args.noise_on_top
    ]

    cells = generate_cells(noise, noise_on_top, args.map_width, args.map_height, tiles)

    t = 0
    running = True
    while running:
        running, regenerate_cells = handle_events()

        if regenerate_cells:
            print()
            z = t / args.change_with_time if args.change_with_time is not None else 0.0
            cells = generate_cells(noise, noise_on_top, args.map_width, args.map_height, tiles, z=z)

        show(screen, cells, args.tile_size)

        dt = clock.tick(args.frame_rate) / 1000
        if args.show_fps:
            print(clock.get_fps(), end='\r')

        t += 1

    pygame.quit()
