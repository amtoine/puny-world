import pygame
from pathlib import Path
from tileset import load_tileset
from random import choice
from typing import List
import argparse
import numpy as np
from time import time_ns
from PIL import Image
from rich import print

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
DARK_GREY = (100, 100, 100)
GREEN = (0, 255, 0)

TILE_SUBSET = [
    ("grass_1", 1),
    ("grass_2", .1),
    ("grass_3", .1),
    ("grass_4", .1),
    ("grass_5", .1),
    ("grass_6", .1),
    ("grass_7", .1),
    ("grass_8", .1),
    ("grass_9", .1),
    ("rock_north_west", 0.1285),
    ("rock_north", 0.1285),
    ("rock_north_east", 0.1285),
    ("rock_west", 0.1285),
    ("rock_east", 0.1285),
    ("rock_south_west", 0.1285),
    ("rock_south", 0.1285),
    ("rock_south_east", 0.1285),
    ("rock_corner_north_west", 0.1285),
    ("rock_corner_north_east", 0.1285),
    ("rock_corner_south_west", 0.1285),
    ("rock_corner_south_east", 0.1285),
    ("rock_diag", 0.1285),
    ("rock_diag_anti", 0.1285),
    ("river_corner_north_west", 0.1111),
    ("river_north", 0.1111),
    ("river_corner_north_east", 0.1111),
    ("river_west", 0.1111),
    ("water", 0.1111),
    ("river_east", 0.1111),
    ("river_corner_south_west", 0.1111),
    ("river_south", 0.1111),
    ("river_corner_south_east", 0.1111),
    ("river_inv_corner_north_west", 0.1111),
    ("river_inv_corner_north_east", 0.1111),
    ("river_inv_corner_south_west", 0.1111),
    ("river_inv_corner_south_east", 0.1111),
    ("beach_corner_north_west", 0.1111),
    ("beach_north", 0.1111),
    ("beach_corner_north_east", 0.1111),
    ("beach_west", 0.1111),
    ("beach_water", 0.1111),
    ("beach_east", 0.1111),
    ("beach_corner_south_west", 0.1111),
    ("beach_south", 0.1111),
    ("beach_corner_south_east", 0.1111),
    ("beach_inv_corner_north_west", 0.1111),
    ("beach_inv_corner_north_east", 0.1111),
    ("beach_inv_corner_south_west", 0.1111),
    ("beach_inv_corner_south_east", 0.1111),
    ("sea_corner_north_west", 0.1111),
    ("sea_north", 0.1111),
    ("sea_corner_north_east", 0.1111),
    ("sea_west", 0.1111),
    ("sea_east", 0.1111),
    ("sea_corner_south_west", 0.1111),
    ("sea_south", 0.1111),
    ("sea_corner_south_east", 0.1111),
    ("sea_inv_corner_north_west", 0.1111),
    ("sea_inv_corner_north_east", 0.1111),
    ("sea_inv_corner_south_west", 0.1111),
    ("sea_inv_corner_south_east", 0.1111),
    ("ocean_corner_north_west", 0.1111),
    ("ocean_north", 0.1111),
    ("ocean_corner_north_east", 0.1111),
    ("ocean_west", 0.1111),
    ("ocean", 0.1111),
    ("ocean_east", 0.1111),
    ("ocean_corner_south_west", 0.1111),
    ("ocean_south", 0.1111),
    ("ocean_corner_south_east", 0.1111),
    ("ocean_inv_corner_north_west", 0.1111),
    ("ocean_inv_corner_north_east", 0.1111),
    ("ocean_inv_corner_south_west", 0.1111),
    ("ocean_inv_corner_south_east", 0.1111),
    ("waterfall", 0.1111),
    ("path_vert_north", 0.1111),
    ("path_vert", 0.1111),
    ("path_vert_south", 0.1111),
    ("path_spot", 0.1111),
    ("path_horiz_west", 0.1111),
    ("path_horiz", 0.1111),
    ("path_horiz_east", 0.1111),
    ("path_turn_north_west", 0.1111),
    ("path_three_cross_north", 0.1111),
    ("path_turn_north_east", 0.1111),
    ("path_three_cross_west", 0.1111),
    ("path_four_cross", 0.1111),
    ("path_three_cross_east", 0.1111),
    ("path_turn_south_west", 0.1111),
    ("path_three_cross_south", 0.1111),
    ("path_turn_south_east", 0.1111),
    ("path_start_north", 0.1111),
    ("path_start_west", 0.1111),
    ("path_start_east", 0.1111),
    ("path_start_south", 0.1111),
    ("path_corner_north_west", 0.1111),
    ("path_north", 0.1111),
    ("path_corner_north_east", 0.1111),
    ("path_west", 0.1111),
    ("path", 0.1111),
    ("path_east", 0.1111),
    ("path_corner_south_west", 0.1111),
    ("path_south", 0.1111),
    ("path_corner_south_east", 0.1111),
    ("path_inv_corner_north_west", 0.1111),
    ("path_inv_corner_north_east", 0.1111),
    ("path_inv_corner_south_west", 0.1111),
    ("path_inv_corner_south_east", 0.1111),
    ("path_diag", 0.1111),
    ("path_diag_anti", 0.1111),

    ("sand_path_vert_north", 0.1111),
    ("sand_path_vert", 0.1111),
    ("sand_path_vert_south", 0.1111),
    ("sand_path_spot", 0.1111),
    ("sand_path_horiz_west", 0.1111),
    ("sand_path_horiz", 0.1111),
    ("sand_path_horiz_east", 0.1111),
    ("sand_path_turn_north_west", 0.1111),
    ("sand_path_three_cross_north", 0.1111),
    ("sand_path_turn_north_east", 0.1111),
    ("sand_path_three_cross_west", 0.1111),
    ("sand_path_four_cross", 0.1111),
    ("sand_path_three_cross_east", 0.1111),
    ("sand_path_turn_south_west", 0.1111),
    ("sand_path_three_cross_south", 0.1111),
    ("sand_path_turn_south_east", 0.1111),
    ("sand_path_start_north", 0.1111),
    ("sand_path_start_west", 0.1111),
    ("sand_path_start_east", 0.1111),
    ("sand_path_start_south", 0.1111),
    ("sand_path_corner_north_west", 0.1111),
    ("sand_path_north", 0.1111),
    ("sand_path_corner_north_east", 0.1111),
    ("sand_path_west", 0.1111),
    ("sand_path", 0.1111),
    ("sand_path_east", 0.1111),
    ("sand_path_corner_south_west", 0.1111),
    ("sand_path_south", 0.1111),
    ("sand_path_corner_south_east", 0.1111),
    ("sand_path_inv_corner_north_west", 0.1111),
    ("sand_path_inv_corner_north_east", 0.1111),
    ("sand_path_inv_corner_south_west", 0.1111),
    ("sand_path_inv_corner_south_east", 0.1111),
    ("sand_path_diag", 0.1111),
    ("sand_path_diag_anti", 0.1111),
]


def error(msg: str):
    print(f"[bold red]ERROR[/bold red]: {msg}")


def info(msg: str):
    print(f"[bold green]INFO[/bold green]: {msg}")


def warning(msg: str):
    print(f"[bold yellow]WARNING[/bold yellow]: {msg}")


def handle_events() -> (bool, bool, bool):
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (
            event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
        ):
            return (False, False, False)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                return (True, True, False)
            elif event.key == pygame.K_RETURN:
                return (True, False, True)
    return (True, False, False)


def show(cells: List[dict], s: int, show_average_of_tile: bool, min_entropy: float | None):
    screen.fill(BLACK)

    for c in cells:
        if c["is_collapsed"]:
            if len(c["options"]) == 0:
                pygame.draw.rect(
                    screen,
                    RED,
                    (c["j"] * s, c["i"] * s, s, s),
                    width=1,
                )
            else:
                screen.blit(
                    pygame.transform.scale(
                        tiles[c["options"][0]].image,
                        (s, s),
                    ),
                    (c["j"] * s, c["i"] * s),
                )
        else:
            if len(c["options"]) > 0 and show_average_of_tile:
                screen.blit(
                    pygame.transform.scale(
                        average_images([tiles[opt].image for opt in c["options"]]),
                        (s, s),
                    ),
                    (c["j"] * s, c["i"] * s),
                )
            if c["entropy"] == 0:
                color = RED
            elif min_entropy is not None and c["entropy"] == min_entropy:
                color = GREEN
            elif c["entropy"] < 10:
                color = WHITE
            else:
                color = DARK_GREY

            text = font.render(str(round(c["entropy"], 1)), False, color)
            screen.blit(
                text,
                (
                    (c["j"] + .5) * s - text.get_width() / 2,
                    (c["i"] + .5) * s - text.get_height() / 2,
                ),
            )

    pygame.display.flip()


def entropy(cell: dict) -> float:
    p = np.array([weights[opt] for opt in cell["options"]])
    p = p / p.sum()
    return -np.log2(p).sum()


def collapse(
    cell: dict, cells: List[dict], w: int, h: int, use_information_entropy: bool
) -> (bool, int, int):
    assert len(cell["options"]) > 0, "cell shouldn't be inconsistent"

    p = np.array([weights[opt] for opt in cell["options"]])
    p = p / p.sum()
    cell["options"] = np.random.choice(cell["options"], 1, p=p)
    cell["is_collapsed"] = True
    cell["entropy"] = 0

    stack = [cell]
    while len(stack) > 0:
        curr = stack.pop()
        i, j = curr["i"], curr["j"]
        for ni, nj, dir, opposite in [
            (i - 1, j, 'n', 's'),
            (i + 1, j, 's', 'n'),
            (i, j - 1, 'w', 'e'),
            (i, j + 1, 'e', 'w'),
        ]:
            if 0 <= ni < h and 0 <= nj < w:
                n = ni * w + nj
                if cells[n]["entropy"] == 0:
                    continue

                before = len(cells[n]["options"])
                connectors = [tiles[opt].get_type(dir) for opt in curr["options"]]
                options = [
                    opt
                    for opt in cells[n]["options"]
                    if tiles[opt].get_type(opposite) in connectors
                ]

                cells[n]["options"] = options
                if len(cells[n]["options"]) < before:
                    stack.append(cells[n])

                if use_information_entropy:
                    cells[n]["entropy"] = entropy(cells[n])
                else:
                    cells[n]["entropy"] = len(cells[n]["options"])

                if len(cells[n]["options"]) == 0:
                    return True, ni, nj

    return False, None, None


def wave_function_collapse(
    w: int,
    h: int,
    s: int,
    show_average_of_tile: bool,
    use_information_entropy: bool,
    frame_rate: int = 30,
    interactive: bool = True,
) -> (List[dict], bool, float):
    dt = None
    running = True
    valid = False

    nb_retries = 0
    t = time_ns()

    while not valid and running:
        nb_retries += 1
        cells = [
            {
                "i": i,
                "j": j,
                "options": list(tiles.keys()),
                "is_collapsed": False,
                "entropy": None,
            }
            for i in range(h) for j in range(w)
        ]

        for i, c in enumerate(cells):
            cells[i]["entropy"] = entropy(c) if use_information_entropy else len(c["options"])

        min_entropy = float("inf")
        while running:
            if interactive:
                running, *_ = handle_events()

            # pick non-collapsed cell with least entropy
            non_collapsed = list(filter(lambda c: not c["is_collapsed"], cells))
            # FIXME: should backtrack here instead of breaking out of the algorithm
            if len(non_collapsed) == 0:
                break
            min_entropy = min(non_collapsed, key=lambda c: c["entropy"])["entropy"]
            cell = choice(list(filter(
                lambda c: c["entropy"] == min_entropy,
                non_collapsed,
            )))

            is_inconsistent, ni, nj = collapse(cell, cells, w, h, use_information_entropy)
            if is_inconsistent:
                error(f"found an inconsistency in cell ({ni}, {nj})")
                break

            if interactive:
                show(cells, s, show_average_of_tile, min_entropy)
                dt = clock.tick(frame_rate) / 1000

        if len([c for c in cells if not c["is_collapsed"]]) == 0:
            valid = True

    warning(f"retries: {nb_retries}, t: {time_ns() - t}")

    return cells, running, dt


def average_images(images: List[pygame.surface.Surface]) -> pygame.surface.Surface:
    output = pygame.Surface(images[0].get_size())

    pygame.surfarray.blit_array(
        output,
        sum(
            pygame.surfarray.array3d(image).astype(int) for image in images
        ) // len(images),
    )

    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--map-width", "-W", type=int, required=True)
    parser.add_argument("--map-height", "-H", type=int, required=True)
    parser.add_argument("--tile-size", "-s", type=int, required=True)
    parser.add_argument("--frame-rate", "-f", type=int, default=30)
    parser.add_argument("--show-average", "-a", action="store_true")
    parser.add_argument("--non-interactive", "-I", action="store_true")
    parser.add_argument("--use-information-entropy", action="store_true")
    parser.add_argument("--analyze-algorithm", "-A", action="store_true")
    parser.add_argument("--nb-measurements", "-n", type=int, default=10)
    args = parser.parse_args()

    tiles, _, _ = load_tileset(Path("../../punyworld.json"))
    tiles = {k: tiles[k] for k, _ in TILE_SUBSET}
    weights = {k: w for k, w in TILE_SUBSET}

    if args.analyze_algorithm:
        for _ in range(args.nb_measurements):
            _ = wave_function_collapse(
                args.map_width,
                args.map_height,
                args.tile_size,
                args.show_average,
                args.use_information_entropy,
                frame_rate=args.frame_rate,
                interactive=False,
            )
        exit(0)

    pygame.init()
    pygame.font.init()
    font = pygame.font.SysFont('Comic Sans MS', int(.5 * args.tile_size))
    screen = pygame.display.set_mode((
        args.map_width * args.tile_size,
        args.map_height * args.tile_size,
    ))
    clock = pygame.time.Clock()
    dt = 0

    running = True
    rerun = False
    cells = []

    while running:
        running, rerun, snapshot = handle_events()
        if snapshot:
            out = f"{time_ns()}.png"
            image = np.transpose(pygame.surfarray.array3d(screen), (1, 0, 2))
            Image.fromarray(image).save(out)
            info(f"window saved in [purple]{out}[/purple]")
        if rerun:
            cells, running, dt = wave_function_collapse(
                args.map_width,
                args.map_height,
                args.tile_size,
                args.show_average,
                args.use_information_entropy,
                frame_rate=args.frame_rate,
                interactive=not args.non_interactive,
            )
        show(cells, args.tile_size, args.show_average, min_entropy=None)
        dt = clock.tick(args.frame_rate) / 1000

    pygame.quit()
