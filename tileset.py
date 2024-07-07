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
    north: str | None
    east: str | None
    west: str | None
    south: str | None
    transparent: bool
    animation: bool


@dataclass
class AnimationStep:
    id: int
    duration: int


@dataclass
class Animation:
    id: int
    animation: List[AnimationStep]


def load_tileset(tileset: Path) -> (Dict[str, Tile], List[Animation]):
    with open(tileset, 'r') as handle:
        metadata = json.load(handle)

    tilewidth = metadata["image"]["tile_width"]
    tileheight = metadata["image"]["tile_height"]
    nb_columns = metadata["image"]["columns"]
    image = pygame.image.load(
        tileset.parent.joinpath(metadata["image"]["source"])
    )

    tiles = {}
    for k, v in tqdm(metadata["tiles"].items(), desc="loading assets"):
        tile = pygame.Surface((tilewidth, tileheight))
        tile.blit(
            image,
            (0, 0),
            (
                v["id"] % nb_columns * tilewidth,
                v["id"] // nb_columns * tileheight,
                tilewidth,
                tileheight,
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

    animations = [
        Animation(
            id=a["id"],
            animation=[
                AnimationStep(id=b["id"], duration=b["duration"])
                for b in a["animation"]
            ]
        )
        for a in metadata["animations"]
    ]

    for a in animations:
        name = [k for k, v in tiles.items() if v.id == a.id][0]
        for i, b in enumerate(a.animation[1:], start=1):
            tile = pygame.Surface((tilewidth, tileheight))
            tile.blit(
                image,
                (0, 0),
                (
                    b.id % nb_columns * tilewidth,
                    b.id // nb_columns * tileheight,
                    tilewidth,
                    tileheight,
                )
            )
            tiles[f"{name}__animation_{i}"] = Tile(
                image=tile,
                id=b.id,
                north=None,
                east=None,
                west=None,
                south=None,
                transparent=False,
                animation=False,
            )

    return tiles, animations


@dataclass
class Neighbours:
    n: List[str]
    e: List[str]
    s: List[str]
    w: List[str]


def compute_neighbours(tile: Tile, tiles: Dict[str, Tile]) -> Neighbours:
    return Neighbours(
        n=[k for k, v in tiles.items() if v.south == tile.north and tile.north is not None],
        e=[k for k, v in tiles.items() if v.west == tile.east and tile.east is not None],
        s=[k for k, v in tiles.items() if v.north == tile.south and tile.south is not None],
        w=[k for k, v in tiles.items() if v.east == tile.west and tile.west is not None],
    )


def get_animation_steps(
    id: int, animations: List[Animation]
) -> List[AnimationStep]:
    matches = [x for x in animations if x.id == id]
    if len(matches) != 1:
        raise Exception(
            f"there should be exactly one animation with ID {id}, found {len(matches)}"
        )
    return matches[0].animation


def get_tile(id: int, tiles: Dict[str, Tile]) -> Tile:
    matches = [v for v in tiles.values() if v.id == id]
    if len(matches) != 1:
        raise Exception(
            f"there should be exactly one animation with ID {id}, found {len(matches)}"
        )
    return matches[0]
