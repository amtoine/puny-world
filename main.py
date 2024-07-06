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

    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    clock = pygame.time.Clock()
    frame_rate = 60
    dt = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                running = False

        screen.fill((0, 0, 0))
        w, h = screen.get_size()
        screen.blit(
            pygame.transform.scale(tiles["grass_2"].image, (128, 128)),
            (w / 2, h / 2),
        )
        pygame.display.flip()
        dt = clock.tick(frame_rate) / 1000

    pygame.quit()
