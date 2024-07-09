import pygame
from pathlib import Path
from tileset import load_tileset, compute_neighbours
from random import choice
from typing import List
import argparse
import numpy as np
from time import time_ns
from PIL import Image

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

TILE_SUBSET = [
    ("grass_1", 50),
    ("grass_2", 50),
    ("grass_3", 50),
    ("grass_4", 50),
    ("grass_5", 50),
    ("grass_6", 50),
    ("grass_7", 50),
    ("grass_8", 50),
    ("grass_9", 50),
    ("path_vert_north", 1),
    ("path_vert", 1),
    ("path_vert_south", 1),
    ("path_spot", 1),
    ("path_horiz_west", 1),
    ("path_horiz", 1),
    ("path_horiz_east", 1),
    ("path_turn_north_west", 1),
    ("path_three_cross_north", 1),
    ("path_turn_north_east", 1),
    ("path_three_cross_west", 1),
    ("path_four_cross", 1),
    ("path_three_cross_east", 1),
    ("path_turn_south_west", 1),
    ("path_three_cross_south", 1),
    ("path_turn_south_east", 1),
    ("path_start_north", 1),
    ("path_start_west", 1),
    ("path_start_east", 1),
    ("path_start_south", 1),
    ("path_corner_north_west", 1),
    ("path_north", 1),
    ("path_corner_north_east", 1),
    ("path_west", 1),
    ("path", 1),
    ("path_east", 1),
    ("path_corner_south_west", 1),
    ("path_south", 1),
    ("path_corner_south_east", 1),
    ("path_inv_corner_north_west", 1),
    ("path_inv_corner_north_east", 1),
    ("path_inv_corner_south_west", 1),
    ("path_inv_corner_south_east", 1),
    ("path_diag", 1),
    ("path_diag_anti", 1),
    ("rock_north_west", 1),
    ("rock_north", 1),
    ("rock_north_east", 1),
    ("rock_west", 1),
    ("rock_east", 1),
    ("rock_south_west", 1),
    ("rock_south", 1),
    ("rock_south_east", 1),
    ("rock_corner_north_west", 1),
    ("rock_corner_north_east", 1),
    ("rock_corner_south_west", 1),
    ("rock_corner_south_east", 1),
    ("rock_diag", 1),
    ("rock_diag_anti", 1),
    ("stair_south", 1),
    ("stair_east", 1),
    ("stair_west", 1),
    ("stair_north", 1),
    ("path_slope_south", 1),
    ("path_slope_east", 1),
    ("path_slope_west", 1),
    ("path_slope_north", 1),
    ("rock_entrance_1_1", 1),
    ("rock_entrance_2_1", 1),
    ("river_vert_north", 1),
    ("river_vert", 1),
    ("river_vert_south", 1),
    ("river_spot", 1),
    ("river_horiz_west", 1),
    ("river_horiz", 1),
    ("river_horiz_east", 1),
    ("river_turn_north_west", 1),
    ("river_three_cross_north", 1),
    ("river_turn_north_east", 1),
    ("river_three_cross_west", 1),
    ("river_four_cross", 1),
    ("river_three_cross_east", 1),
    ("river_turn_south_west", 1),
    ("river_three_cross_south", 1),
    ("river_turn_south_east", 1),
    ("river_start_north", 1),
    ("river_start_west", 1),
    ("river_start_east", 1),
    ("river_start_south", 1),
    ("river_island", 1),
    ("river_corner_north_west", 1),
    ("river_north", 1),
    ("river_corner_north_east", 1),
    ("river_west", 1),
    ("water", 1),
    ("river_east", 1),
    ("river_corner_south_west", 1),
    ("river_south", 1),
    ("river_corner_south_east", 1),
    ("river_inv_corner_north_west", 1),
    ("river_inv_corner_north_east", 1),
    ("river_inv_corner_south_west", 1),
    ("river_inv_corner_south_east", 1),
]


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


def show(cells: List[dict], s: int, show_average_of_tile: bool):
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
            text = font.render(str(round(c["entropy"], 1)), False, WHITE)
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
    if len(cell["options"]) > 0:
        p = np.array([weights[opt] for opt in cell["options"]])
        p = p / p.sum()
        cell["options"] = np.random.choice(cell["options"], 1, p=p)
    cell["is_collapsed"] = True

    is_inconsistent, ii, ij = False, None, None
    if len(cell["options"]) > 0:
        # update the neighbours
        neighbours = compute_neighbours(tiles[cell["options"][0]], tiles)
        i, j = cell["i"], cell["j"]
        for ni, nj, c in [
            (i - 1, j, neighbours.n),
            (i + 1, j, neighbours.s),
            (i, j - 1, neighbours.w),
            (i, j + 1, neighbours.e),
        ]:
            if 0 <= ni < h and 0 <= nj < w:
                n = ni * w + nj
                cells[n]["options"] = list(
                    set(cells[n]["options"]) & set(c)
                )
                if use_information_entropy:
                    cells[n]["entropy"] = entropy(cells[n])
                else:
                    cells[n]["entropy"] = len(cells[n]["options"])
                if len(cells[n]["options"]) == 0:
                    is_inconsistent, ii, ij = True, ni, nj

    return is_inconsistent, ii, ij


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
            non_collapsed = list(filter(lambda c: not c["is_collapsed"] and len(c["options"]) > 0, cells))
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
                print(f"found an inconsistency in cell ({ni}, {nj})")
                break

            if interactive:
                show(cells, s, show_average_of_tile)
                dt = clock.tick(frame_rate) / 1000

        if len([c for c in cells if not c["is_collapsed"]]) == 0:
            valid = True

    print(f"retries: {nb_retries}, t: {time_ns() - t}")

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
            print(f"window save in `{out}`")
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
        show(cells, args.tile_size, args.show_average)
        dt = clock.tick(args.frame_rate) / 1000

    pygame.quit()
