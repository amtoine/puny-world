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
    x: str | None
    transparent: bool
    animation: bool

    def get_type(self, dir: str) -> str | None:
        if dir == 'n' or dir == "north":
            return ''.join([self.x[0], self.x[1], self.x[2]])
        if dir == 'e' or dir == "east":
            return ''.join([self.x[2], self.x[3], self.x[4]])
        if dir == 's' or dir == "south":
            return ''.join([self.x[6], self.x[5], self.x[4]])
        if dir == 'w' or dir == "west":
            return ''.join([self.x[0], self.x[7], self.x[6]])


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
    return surface.subsurface(
        pygame.Rect(id % cols * size[0], id // cols * size[1], *size)
    )


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
            x=v["x"],
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
                        x=None,
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
        n=[k for k, v in tiles.items() if tile.x[0] == v.x[6] and tile.x[1] == v.x[5] and tile.x[2] == v.x[4]],  # noqa: E501
        e=[k for k, v in tiles.items() if tile.x[2] == v.x[0] and tile.x[3] == v.x[7] and tile.x[4] == v.x[6]],  # noqa: E501
        s=[k for k, v in tiles.items() if tile.x[6] == v.x[0] and tile.x[5] == v.x[1] and tile.x[4] == v.x[2]],  # noqa: E501
        w=[k for k, v in tiles.items() if tile.x[0] == v.x[2] and tile.x[7] == v.x[3] and tile.x[6] == v.x[4]],  # noqa: E501
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
