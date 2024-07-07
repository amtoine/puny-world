import pygame
from pathlib import Path
from tileset import load_tileset, get_tile, get_animation_steps

RENDERING_GRID_WIDTH = 10
RENDERING_TILE_SIZE = 92

CANVA_SIZE = (1280, 720)
FRAME_RATE = 60

NB_MS_IN_SEC = 1_000

BLACK = (0, 0, 0)

TILESET = Path("metadata/punyworld-overworld-tiles.json")

ANIMATION_SEQUENCE_LEN = 4
ANIMATION_INV_SPEED = 10


if __name__ == "__main__":
    tiles, animations = load_tileset(TILESET)
    animated = {k: v for k, v in tiles.items() if v.animation}

    pygame.init()
    screen = pygame.display.set_mode(CANVA_SIZE)
    clock = pygame.time.Clock()
    dt = 0

    t = 0
    running = True
    while running:
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

        pygame.display.flip()
        dt = clock.tick(FRAME_RATE) / NB_MS_IN_SEC
        t += 1

    pygame.quit()
