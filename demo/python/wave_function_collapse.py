import pygame
from pathlib import Path
from tileset import load_tileset, compute_neighbours
from random import choice
from typing import List
import argparse

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

TILE_SUBSET = [
    "grass_1",
    "grass_2",
    "grass_3",
    "grass_4",
    "grass_5",
    "grass_6",
    "grass_7",
    "grass_8",
    "grass_9",
    "path_vert_north",
    "path_vert",
    "path_vert_south",
    "path_spot",
    "path_horiz_west",
    "path_horiz",
    "path_horiz_east",
    "path_turn_north_west",
    "path_three_cross_north",
    "path_turn_north_east",
    "path_three_cross_west",
    "path_four_cross",
    "path_three_cross_east",
    "path_turn_south_west",
    "path_three_cross_south",
    "path_turn_south_east",
    "path_start_north",
    "path_start_west",
    "path_start_east",
    "path_start_south",
    "path_corner_north_west",
    "path_north",
    "path_corner_north_east",
    "path_west",
    "path",
    "path_east",
    "path_corner_south_west",
    "path_south",
    "path_corner_south_east",
    "path_inv_corner_north_west",
    "path_inv_corner_north_east",
    "path_inv_corner_south_west",
    "path_inv_corner_south_east",
    "path_diag",
    "path_diag_anti",
    "rock_north_west",
    "rock_north",
    "rock_north_east",
    "rock_west",
    "rock_east",
    "rock_south_west",
    "rock_south",
    "rock_south_east",
    "rock_corner_north_west",
    "rock_corner_north_east",
    "rock_corner_south_west",
    "rock_corner_south_east",
    "rock_diag",
    "rock_diag_anti",
    "stair_south",
    "stair_east",
    "stair_west",
    "stair_north",
    "path_slope_south",
    "path_slope_east",
    "path_slope_west",
    "path_slope_north",
    "rock_entrance_1_1",
    "rock_entrance_2_1",
    "river_vert_north",
    "river_vert",
    "river_vert_south",
    "river_spot",
    "river_horiz_west",
    "river_horiz",
    "river_horiz_east",
    "river_turn_north_west",
    "river_three_cross_north",
    "river_turn_north_east",
    "river_three_cross_west",
    "river_four_cross",
    "river_three_cross_east",
    "river_turn_south_west",
    "river_three_cross_south",
    "river_turn_south_east",
    "river_start_north",
    "river_start_west",
    "river_start_east",
    "river_start_south",
    "river_island",
    "river_corner_north_west",
    "river_north",
    "river_corner_north_east",
    "river_west",
    "water",
    "river_east",
    "river_corner_south_west",
    "river_south",
    "river_corner_south_east",
    "river_inv_corner_north_west",
    "river_inv_corner_north_east",
    "river_inv_corner_south_west",
    "river_inv_corner_south_east",
]


def handle_events() -> (bool, bool):
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (
            event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
        ):
            return (False, False)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                return (True, True)
    return (True, False)


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
            text = font.render(str(c["entropy"]), False, WHITE)
            screen.blit(
                text,
                (
                    (c["j"] + .5) * s - text.get_width() / 2,
                    (c["i"] + .5) * s - text.get_height() / 2,
                ),
            )

    pygame.display.flip()


def entropy(cell: dict) -> float:
    return len(cell["options"])


def wave_function_collapse(
    w: int,
    h: int,
    s: int,
    show_average_of_tile: bool,
    frame_rate: int = 30,
    interactive: bool = True,
) -> (List[dict], bool, float):
    dt = None
    running = True
    valid = False

    while not valid and running:
        cells = [
            {
                "i": i,
                "j": j,
                "options": list(tiles.keys()),
                "is_collapsed": False,
                "entropy": len(list(tiles.keys())),
            }
            for i in range(h) for j in range(w)
        ]

        min_entropy = float("inf")
        while min_entropy > 0 and running:
            running, _ = handle_events()

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

            # collapse the cell
            if len(cell["options"]) > 0:
                cell["options"] = [choice(cell["options"])]
            cell["is_collapsed"] = True

            if len(cell["options"]) > 0:
                is_inconsistent, ii, ij = False, None, None
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
                        cells[n]["entropy"] = entropy(cells[n])
                        if cells[n]["entropy"] == 0:
                            is_inconsistent, ii, ij = True, ni, nj
                if is_inconsistent:
                    print(f"found an inconsistency in cell ({ni}, {nj})")
                    break

            if interactive:
                show(cells, s, show_average_of_tile)
                dt = clock.tick(frame_rate) / 1000

        if len([c for c in cells if not c["is_collapsed"]]) == 0:
            valid = True

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
    args = parser.parse_args()

    tiles, _, _ = load_tileset(Path("../../punyworld.json"))
    tiles = {k: tiles[k] for k in TILE_SUBSET}

    pygame.init()
    pygame.font.init()
    font = pygame.font.SysFont('Comic Sans MS', int(15 / 23 * args.tile_size))
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
        running, rerun = handle_events()
        if rerun:
            cells, running, dt = wave_function_collapse(
                args.map_width,
                args.map_height,
                args.tile_size,
                args.show_average,
                frame_rate=args.frame_rate,
                interactive=not args.non_interactive,
            )
        show(cells, args.tile_size, args.show_average)
        dt = clock.tick(args.frame_rate) / 1000

    pygame.quit()
