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
    tile: pygame.surface.Surface


@dataclass
class Animation:
    id: int
    animation: List[AnimationStep]


Name = str
Character = Dict[Name, List[pygame.surface.Surface]]


def cut(
    surface: pygame.surface.Surface, id: int, /, size: (int, int), cols: int
) -> pygame.surface.Surface:
    tile = pygame.Surface(size)
    tile.blit(
        surface,
        (0, 0),
        (id % cols * size[0], id // cols * size[1], *size)
    )
    return tile


def load_tileset(
    tileset: Path
) -> (Dict[Name, Tile], List[Animation], Dict[Name, Character]):
    with open(tileset, 'r') as handle:
        metadata = json.load(handle)

    overworld = metadata["overworld"]

    tilewidth = overworld["image"]["tile_width"]
    tileheight = overworld["image"]["tile_height"]
    nb_columns = overworld["image"]["columns"]
    image = pygame.image.load(
        tileset.parent.joinpath(overworld["image"]["source"])
    )

    tiles = {}
    for k, v in tqdm(overworld["tiles"].items(), desc="loading world assets"):
        tiles[k] = Tile(
            image=cut(
                image, v["id"], size=(tilewidth, tileheight), cols=nb_columns
            ),
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
                AnimationStep(
                    id=b["id"],
                    duration=b["duration"],
                    tile=Tile(
                        image=cut(
                            image, b["id"], size=(tilewidth, tileheight), cols=nb_columns
                        ),
                        id=b["id"],
                        north=None,
                        east=None,
                        west=None,
                        south=None,
                        transparent=False,
                        animation=False,
                    )
                )
                for b in a["animation"]
            ]
        )
        for a in overworld["animations"]
    ]

    characters = {}
    for name, character in tqdm(
        metadata["characters"].items(),
        desc="loading character assets",
    ):
        image = pygame.image.load(
            tileset.parent.joinpath(character["image"]["source"])
        )
        size = (
            character["image"]["tile_width"], character["image"]["tile_height"]
        )
        cols = character["image"]["columns"]
        characters[name] = {
            k: [cut(image, i, size=size, cols=cols) for i in ids]
            for k, ids in character["animations"].items()
        }

    return tiles, animations, characters


@dataclass
class Neighbours:
    n: List[Name]
    e: List[Name]
    s: List[Name]
    w: List[Name]


def compute_neighbours(tile: Tile, tiles: Dict[Name, Tile]) -> Neighbours:
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


def get_tile(id: int, tiles: Dict[Name, Tile]) -> Tile:
    matches = [v for v in tiles.values() if v.id == id]
    if len(matches) != 1:
        raise Exception(
            f"there should be exactly one animation with ID {id}, found {len(matches)}"
        )
    return matches[0]
