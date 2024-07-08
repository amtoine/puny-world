import pygame
from pathlib import Path
from tileset import load_tileset
from PIL import Image
import numpy as np
import argparse
import os

RENDERING_GRID_WIDTH = 8
RENDERING_TILE_SIZE = 128

CANVA_SIZE = (
    RENDERING_GRID_WIDTH * RENDERING_TILE_SIZE,
    RENDERING_GRID_WIDTH * RENDERING_TILE_SIZE,
)
FRAME_RATE = 60

NB_MS_IN_SEC = 1_000

BLACK = (0, 0, 0)

ANIMATION_INV_SPEED = 15


def run(characters):
    pygame.init()
    screen = pygame.display.set_mode(CANVA_SIZE)
    clock = pygame.time.Clock()

    curr = 0
    print(list(characters.keys())[curr])

    t = 0
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if event.mod & pygame.KMOD_LSHIFT:
                        curr = (curr + 1) % len(list(characters.keys()))
                    else:
                        curr = (curr - 1) % len(list(characters.keys()))
                    print(list(characters.keys())[curr])

        screen.fill(BLACK)

        for i, (k, v) in enumerate(characters[list(characters.keys())[curr]].items()):
            screen.blit(
                pygame.transform.scale(
                    v[t // ANIMATION_INV_SPEED % len(v)],
                    (RENDERING_TILE_SIZE, RENDERING_TILE_SIZE),
                ),
                (
                    (i % RENDERING_GRID_WIDTH) * RENDERING_TILE_SIZE,
                    (i // RENDERING_GRID_WIDTH) * RENDERING_TILE_SIZE,
                ),
            )

        pygame.display.flip()
        clock.tick(FRAME_RATE)
        t += 1

    pygame.quit()


def generate_gif(characters, output_dir: str):
    screen = pygame.surface.Surface(CANVA_SIZE)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for name, character in characters.items():
        frames = []
        print(f"recording frames for {name}... ", end='', flush=True)

        for t in range(100):
            screen.fill(BLACK)

            for i, (k, v) in enumerate(character.items()):
                screen.blit(
                    pygame.transform.scale(
                        v[t // ANIMATION_INV_SPEED % len(v)],
                        (RENDERING_TILE_SIZE, RENDERING_TILE_SIZE),
                    ),
                    (
                        (i % RENDERING_GRID_WIDTH) * RENDERING_TILE_SIZE,
                        (i // RENDERING_GRID_WIDTH) * RENDERING_TILE_SIZE,
                    ),
                )

            frames.append(np.transpose(pygame.surfarray.array3d(screen), (1, 0, 2)))

        print("done")
        print("generating GIF... ", end='', flush=True)
        imgs = [Image.fromarray(img) for img in frames]
        output = f"{output_dir}/{name}.gif"
        imgs[0].save(
            output,
            save_all=True,
            append_images=imgs[1:],
            duration=1_000/FRAME_RATE,
            loop=0,
        )
        print("done")
        print(f"GIF written in {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--generate-gif", "-g", action="store_true")
    parser.add_argument("--output-dir", "-o", type=str, default="out/")
    args = parser.parse_args()

    _, _, characters = load_tileset(Path("../../punyworld.json"))

    if not args.generate_gif:
        run(characters)
    else:
        generate_gif(characters, args.output_dir)
