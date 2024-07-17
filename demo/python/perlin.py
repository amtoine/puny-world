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


def generate_cells(
    noise,
    w: int,
    h: int,
    tileset: Dict[Name, Tile],
    z: float = 0.0,
) -> List[Cell]:
    t = time_ns()

    print("[bold green]INFO[/bold green]: starting generating cells")

    noise_values = [
        [
            sum(weight * n([i / h, j / w, z]) for weight, n in noise)
            for j in range(w + 1)
        ]
        for i in range(h + 1)
    ]

    cells = []
    for i in range(h):
        for j in range(w):
            nw = to_land_type(noise_values[i][j])
            ne = to_land_type(noise_values[i][j + 1])
            sw = to_land_type(noise_values[i + 1][j])
            se = to_land_type(noise_values[i + 1][j + 1])
            key = hash_lt(nw, ne, sw, se)

            bg, fg = choice(TILEMAP.get(key, [("spell_red", None)]))
            bg = tileset[bg]
            if fg is not None:
                fg = tileset[fg]

            cells.append(Cell(i, j, background=bg, foreground=fg))

    print(f"[bold green]INFO[/bold green]: done in {(time_ns() - t) / 1000} ms")

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
    parser.add_argument("--noise", type=noise_as_json())
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

    cells = generate_cells(noise, args.map_width, args.map_height, tiles)

    t = 0
    running = True
    while running:
        running, regenerate_cells = handle_events()

        if regenerate_cells:
            print()
            z = t / args.change_with_time if args.change_with_time is not None else 0.0
            cells = generate_cells(noise, args.map_width, args.map_height, tiles, z=z)

        show(screen, cells, args.tile_size)

        dt = clock.tick(args.frame_rate) / 1000
        if args.show_fps:
            print(clock.get_fps(), end='\r')

        t += 1

    pygame.quit()
