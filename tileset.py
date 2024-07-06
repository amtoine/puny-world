import pygame
import json
from typing import List
from dataclasses import dataclass
from tqdm import tqdm
from pathlib import Path


@ dataclass
class Tile:
    image: pygame.surface.Surface
    north: str
    east: str
    west: str
    south: str
    transparent: bool
    animation: bool


def load_tileset(tileset: Path) -> (List[dict], list):
    with open(tileset, 'r') as handle:
        metadata = json.load(handle)

    tilesize = metadata["image"]["tilesize"]
    nb_columns = metadata["image"]["width"] // tilesize
    image = pygame.image.load(
        tileset.parent.joinpath(metadata["image"]["source"])
    )

    tiles = {}
    for k, v in tqdm(metadata["tiles"].items(), desc="loading assets"):
        tile = pygame.Surface((tilesize, tilesize))
        tile.blit(
            image,
            (0, 0),
            (
                v["id"] % nb_columns * tilesize,
                v["id"] // nb_columns * tilesize,
                tilesize,
                tilesize,
            )
        )
        tiles[k] = Tile(
            image=tile,
            north=v["n"],
            east=v["e"],
            west=v["w"],
            south=v["s"],
            transparent=v["transparent"],
            animation=v["animation"],
        )

    return tiles, metadata["animations"]
