import pygame
import json
from typing import List, Dict
from dataclasses import dataclass
from tqdm import tqdm
from pathlib import Path


@ dataclass
class Tile:
    image: pygame.surface.Surface
    id: int
    north: str
    east: str
    west: str
    south: str
    transparent: bool
    animation: bool


def load_tileset(tileset: Path) -> (List[Tile], list):
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
            id=v["id"],
            north=v["n"],
            east=v["e"],
            west=v["w"],
            south=v["s"],
            transparent=v["transparent"],
            animation=v["animation"],
        )

    for a in metadata["animations"]:
        id = a["id"]
        name = [k for k, v in tiles.items() if v.id == id][0]
        for i, b in enumerate(a["animation"][1:], start=1):
            tile = pygame.Surface((tilesize, tilesize))
            tile.blit(
                image,
                (0, 0),
                (
                    b["id"] % nb_columns * tilesize,
                    b["id"] // nb_columns * tilesize,
                    tilesize,
                    tilesize,
                )
            )
            tiles[f"{name}__animation_{i}"] = Tile(
                image=tile,
                id=b["id"],
                north=None,
                east=None,
                west=None,
                south=None,
                transparent=None,
                animation=False,
            )

    return tiles, metadata["animations"]


def compute_neighbours(tile: Tile, tiles: List[Tile]) -> Dict[str, List[str]]:
    return {
        'n': [k for k, v in tiles.items() if v.south == tile.north and tile.north is not None],
        'e': [k for k, v in tiles.items() if v.west == tile.east and tile.east is not None],
        's': [k for k, v in tiles.items() if v.north == tile.south and tile.south is not None],
        'w': [k for k, v in tiles.items() if v.east == tile.west and tile.west is not None],
    }
