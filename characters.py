import pygame
from pathlib import Path
from tileset import load_characters

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


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode(CANVA_SIZE)
    clock = pygame.time.Clock()
    dt = 0

    characters = load_characters(
        dir=Path("assets").joinpath("puny-characters")
    )

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
        dt = clock.tick(FRAME_RATE) / NB_MS_IN_SEC
        t += 1

    pygame.quit()
