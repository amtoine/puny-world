import pygame
import json
from tqdm import tqdm
from typing import List
from dataclasses import dataclass
from pathlib import Path


@ dataclass
class Tile:
    image: pygame.surface.Surface
    north: str
    east: str
    west: str
    south: str
    transparent: bool
    animation: bool


def load_tileset(tileset: Path) -> (List[dict], list):
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
            north=v["n"],
            east=v["e"],
            west=v["w"],
            south=v["s"],
            transparent=v["transparent"],
            animation=v["animation"],
        )

    return tiles, metadata["animations"]


if __name__ == "__main__":
    tiles, _ = load_tileset(Path("metadata/punyworld-overworld-tiles.json"))

    # "show indices"
    t, n, e, s, w = (0, 0, 0, 0, 0)

    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    clock = pygame.time.Clock()
    frame_rate = 60
    dt = 0

    running = True
    while running:
        # compute its neighbours
        tile = tiles[list(tiles.keys())[t]]
        tile = {
            'n': [k for k, v in tiles.items() if v.south == tile.north and tile.north is not None],
            'e': [k for k, v in tiles.items() if v.west == tile.east and tile.east is not None],
            's': [k for k, v in tiles.items() if v.north == tile.south and tile.south is not None],
            'w': [k for k, v in tiles.items() if v.east == tile.west and tile.west is not None],
        }
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                running = False
            elif event.type == pygame.KEYDOWN:
                # update the "show indices"
                if event.key == pygame.K_j:
                    if event.mod & pygame.KMOD_LSHIFT:
                        if len(tile['s']) > 0:
                            s = (s - 1) % len(tile['s'])
                    else:
                        if len(tile['s']) > 0:
                            s = (s + 1) % len(tile['s'])
                elif event.key == pygame.K_k:
                    if event.mod & pygame.KMOD_LSHIFT:
                        if len(tile['n']) > 0:
                            n = (n - 1) % len(tile['n'])
                    else:
                        if len(tile['n']) > 0:
                            n = (n + 1) % len(tile['n'])
                elif event.key == pygame.K_h:
                    if event.mod & pygame.KMOD_LSHIFT:
                        if len(tile['w']) > 0:
                            w = (w - 1) % len(tile['w'])
                    else:
                        if len(tile['w']) > 0:
                            w = (w + 1) % len(tile['w'])
                elif event.key == pygame.K_l:
                    if event.mod & pygame.KMOD_LSHIFT:
                        if len(tile['e']) > 0:
                            e = (e - 1) % len(tile['e'])
                    else:
                        if len(tile['e']) > 0:
                            e = (e + 1) % len(tile['e'])
                elif event.key == pygame.K_SPACE:
                    if event.mod & pygame.KMOD_LSHIFT:
                        t = (t - 1) % len(tiles.keys())
                        n, e, s, w = (0, 0, 0, 0)
                        print(list(tiles.keys())[t])
                    else:
                        t = (t + 1) % len(tiles.keys())
                        n, e, s, w = (0, 0, 0, 0)
                        print(list(tiles.keys())[t])

        screen.fill((0, 0, 0))

        # show the tile and its neighbours
        width, height = screen.get_size()
        screen.blit(
            pygame.transform.scale(tiles[list(tiles.keys())[t]].image, (128, 128)),
            (width / 2, height / 2),
        )
        if len(tile['n']) > 0:
            screen.blit(
                pygame.transform.scale(tiles[tile['n'][n]].image, (128, 128)),
                (width / 2, height / 2 - 128),
            )
        if len(tile['s']) > 0:
            screen.blit(
                pygame.transform.scale(tiles[tile['s'][s]].image, (128, 128)),
                (width / 2, height / 2 + 128),
            )
        if len(tile['w']) > 0:
            screen.blit(
                pygame.transform.scale(tiles[tile['w'][w]].image, (128, 128)),
                (width / 2 - 128, height / 2),
            )
        if len(tile['e']) > 0:
            screen.blit(
                pygame.transform.scale(tiles[tile['e'][e]].image, (128, 128)),
                (width / 2 + 128, height / 2),
            )

        pygame.display.flip()
        dt = clock.tick(frame_rate) / 1000

    pygame.quit()
