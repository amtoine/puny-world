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

BLACK = (0, 0, 0)

LandType = Enum("LandType", ["ROCK", "GRASS", "BEACH", "WATER"])


@dataclass
class Cell:
    i: int
    j: int
    background: Tile
    foreground: Tile | None


def to_land_type(x: float) -> LandType:
    if x > 0.1:
        return LandType.ROCK
    elif x > 0.0:
        return LandType.GRASS
    elif x > -0.1:
        return LandType.BEACH
    else:
        return LandType.WATER


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

            if nw == ne == sw == se == LandType.GRASS:
                bg = tileset["grass_1"]
            elif nw == ne == sw == se == LandType.ROCK:
                bg = tileset["grass_1"]
            elif nw == ne == sw == se == LandType.BEACH:
                bg = tileset["sand_path"]
            elif nw == ne == sw == se == LandType.WATER:
                bg = tileset["water"]
            else:
                bg = tileset["spell_red"]
            fg = None
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
