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
                AnimationStep(id=b["id"], duration=b["duration"])
                for b in a["animation"]
            ]
        )
        for a in overworld["animations"]
    ]

    for a in animations:
        name = [k for k, v in tiles.items() if v.id == a.id][0]
        for i, b in enumerate(a.animation[1:], start=1):
            tiles[f"{name}__animation_{i}"] = Tile(
                image=cut(
                    image, b.id, size=(tilewidth, tileheight), cols=nb_columns
                ),
                id=b.id,
                north=None,
                east=None,
                west=None,
                south=None,
                transparent=False,
                animation=False,
            )

    characters = {}
    for name, character in metadata["characters"].items():
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


def load_character(name: str, dir: Path) -> Character:
    image = pygame.image.load(dir.joinpath(f"{name}.png"))
    character = {
        "idle_s": [0, 1],
        "walk_s": [2, 3],
        "sword_s": [4, 5, 6],
        "bow_s": [7, 8, 9, 10, 11],
        "stave_s": [12, 13, 14],
        "throw_s": [15, 16, 17],
        "hurt_s": [18, 19, 20],
        "dead_s": [21, 22, 23],
        "idle_se": [24, 25],
        "walk_se": [26, 27],
        "sword_se": [28, 29, 30],
        "bow_se":  [31, 32, 33, 34, 35],
        "stave_se": [36, 37, 38],
        "throw_se": [39, 40, 41],
        "hurt_se": [42, 43, 44],
        "dead_se": [45, 46, 47],
        "idle_e": [48, 49],
        "walk_e": [50, 51],
        "sword_e": [52, 53, 54],
        "bow_e":  [55, 56, 57, 58, 59],
        "stave_e": [60, 61, 62],
        "throw_e": [63, 64, 65],
        "hurt_e": [66, 67, 68],
        "dead_e": [69, 70, 71],
        "idle_ne": [72, 73],
        "walk_ne": [74, 75],
        "sword_ne": [76, 77, 78],
        "bow_ne":  [79, 80, 81, 82, 83],
        "stave_ne": [84, 85, 86],
        "throw_ne": [87, 88, 89],
        "hurt_ne": [90, 91, 92],
        "dead_ne": [93, 94, 95],
        "idle_n": [96, 97],
        "walk_n": [98, 99],
        "sword_n": [100, 101, 102],
        "bow_n":  [103, 104, 105, 106, 107],
        "stave_n": [108, 109, 110],
        "throw_n": [111, 112, 113],
        "hurt_n": [114, 115, 116],
        "dead_n": [117, 118, 119],
        "idle_nw": [120, 121],
        "walk_nw": [122, 123],
        "sword_nw": [124, 125, 126],
        "bow_nw":  [127, 128, 129, 130, 131],
        "stave_nw": [132, 133, 134],
        "throw_nw": [135, 136, 137],
        "hurt_nw": [138, 139, 140],
        "dead_nw": [141, 142, 143],
        "idle_w": [144, 145],
        "walk_w": [146, 147],
        "sword_w": [148, 149, 150],
        "bow_w":  [151, 152, 153, 154, 155],
        "stave_w": [156, 157, 158],
        "throw_w": [159, 160, 161],
        "hurt_w": [162, 163, 164],
        "dead_w": [165, 166, 167],
        "idle_sw": [168, 169],
        "walk_sw": [170, 171],
        "sword_sw": [172, 173, 174],
        "bow_sw":  [175, 176, 177, 178, 179],
        "stave_sw": [180, 181, 182],
        "throw_sw": [183, 184, 185],
        "hurt_sw": [186, 187, 188],
        "dead_sw": [189, 190, 191],
    }

    return {
        k: [cut(image, i, size=(32, 32), cols=24) for i in v]
        for k, v in character.items()
    }


def load_characters(dir: Path) -> Dict[Name, Character]:
    characters = [
        "Archer-Green",
        "Soldier-Yellow",
        "Warrior-Red",
        "Orc-Peon-Red",
        "Mage-Cyan",
        "Archer-Purple",
        "Human-Worker-Red",
        "Soldier-Blue",
        "Mage-Red",
        "Human-Soldier-Cyan",
        "Human-Worker-Cyan",
        "Character-Base",
        "Orc-Soldier-Red",
        "Warrior-Blue",
        "Orc-Grunt",
        "Soldier-Red",
        "Orc-Soldier-Cyan",
        "Orc-Peon-Cyan",
        "Human-Soldier-Red",
    ]
    return {
        k: load_character(k, dir)
        for k in tqdm(characters, desc="loading character assets")
    }
