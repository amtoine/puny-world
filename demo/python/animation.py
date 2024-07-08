import pygame
from pathlib import Path
from tileset import load_tileset, get_tile, get_animation_steps
from PIL import Image
import numpy as np
import argparse

RENDERING_GRID_WIDTH = 10
RENDERING_TILE_SIZE = 92

CANVA_SIZE = (1280, 720)
FRAME_RATE = 60

NB_MS_IN_SEC = 1_000

BLACK = (0, 0, 0)

TILESET = "../../punyworld.json"

ANIMATION_SEQUENCE_LEN = 4
ANIMATION_INV_SPEED = 10


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--generate-gif", "-g", action="store_true")
    parser.add_argument("--output", "-o", type=str, default="out.gif")
    args = parser.parse_args()

    tiles, animations, _ = load_tileset(Path(TILESET))
    animated = {k: v for k, v in tiles.items() if v.animation}

    quotient = len(animated) // RENDERING_GRID_WIDTH
    remainder = len(animated) % RENDERING_GRID_WIDTH
    h = quotient + (remainder != 0)
    w = (len(animated) - remainder) // quotient

    window_size = (w * RENDERING_TILE_SIZE, h * RENDERING_TILE_SIZE)
    if not args.generate_gif:
        pygame.init()
        screen = pygame.display.set_mode(window_size)
    else:
        screen = pygame.surface.Surface(window_size)
        frames = []
    clock = pygame.time.Clock()
    dt = 0

    if args.generate_gif:
        print("recording frames... ", end='')

    t = 0
    running = True
    while running:
        if not args.generate_gif:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (
                    event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
                ):
                    running = False

        screen.fill(BLACK)

        for i, (k, v) in enumerate(animated.items()):
            id = get_animation_steps(v.id, animations)[
                (t // ANIMATION_INV_SPEED) % ANIMATION_SEQUENCE_LEN
            ].id
            screen.blit(
                pygame.transform.scale(
                    get_tile(id, tiles).image,
                    (RENDERING_TILE_SIZE, RENDERING_TILE_SIZE),
                ),
                (
                    (i % RENDERING_GRID_WIDTH) * RENDERING_TILE_SIZE,
                    (i // RENDERING_GRID_WIDTH) * RENDERING_TILE_SIZE,
                ),
            )

        if args.generate_gif:
            frames.append(np.transpose(pygame.surfarray.array3d(screen), (1, 0, 2)))
            if t > 4 * ANIMATION_INV_SPEED:
                break
        else:
            pygame.display.flip()
            dt = clock.tick(FRAME_RATE) / NB_MS_IN_SEC
        t += 1

    if args.generate_gif:
        print("done")
        print("generating GIF... ", end='', flush=True)
        imgs = [Image.fromarray(img) for img in frames]
        imgs[0].save(
            args.output,
            save_all=True,
            append_images=imgs[1:],
            duration=1_000/FRAME_RATE,
            loop=0,
        )
        print("done")
        print(f"GIF written in {args.output}")

    pygame.quit()
