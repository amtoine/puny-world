import pygame
from pathlib import Path
from tileset import load_tileset, compute_neighbours

GRID_SIZE = 128

CANVA_SIZE = (3 * GRID_SIZE, 3 * GRID_SIZE)

FRAME_RATE = 60

BLACK = (0, 0, 0)

TILESET_PATH = "../../punyworld.json"


if __name__ == "__main__":
    tiles, _, _ = load_tileset(Path(TILESET_PATH))

    # "show indices"
    t, n, e, s, w = (0, 0, 0, 0, 0)

    pygame.init()
    screen = pygame.display.set_mode(CANVA_SIZE)
    clock = pygame.time.Clock()
    dt = 0

    running = True
    while running:
        # compute its neighbours
        tile = compute_neighbours(tiles[list(tiles.keys())[t]], tiles)
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            ):
                running = False
            elif event.type == pygame.KEYDOWN:
                # update the "show indices"
                if event.key == pygame.K_j:
                    if event.mod & pygame.KMOD_LSHIFT:
                        if len(tile.s) > 0:
                            s = (s - 1) % len(tile.s)
                    else:
                        if len(tile.s) > 0:
                            s = (s + 1) % len(tile.s)
                elif event.key == pygame.K_k:
                    if event.mod & pygame.KMOD_LSHIFT:
                        if len(tile.n) > 0:
                            n = (n - 1) % len(tile.n)
                    else:
                        if len(tile.n) > 0:
                            n = (n + 1) % len(tile.n)
                elif event.key == pygame.K_h:
                    if event.mod & pygame.KMOD_LSHIFT:
                        if len(tile.w) > 0:
                            w = (w - 1) % len(tile.w)
                    else:
                        if len(tile.w) > 0:
                            w = (w + 1) % len(tile.w)
                elif event.key == pygame.K_l:
                    if event.mod & pygame.KMOD_LSHIFT:
                        if len(tile.e) > 0:
                            e = (e - 1) % len(tile.e)
                    else:
                        if len(tile.e) > 0:
                            e = (e + 1) % len(tile.e)
                elif event.key == pygame.K_SPACE:
                    if event.mod & pygame.KMOD_LSHIFT:
                        t = (t - 1) % len(tiles.keys())
                        n, e, s, w = (0, 0, 0, 0)
                        print(list(tiles.keys())[t], tiles[list(tiles.keys())[t]].x)
                    else:
                        t = (t + 1) % len(tiles.keys())
                        n, e, s, w = (0, 0, 0, 0)
                        print(list(tiles.keys())[t], tiles[list(tiles.keys())[t]].x)

        screen.fill(BLACK)

        # show the tile and its neighbours
        width, height = screen.get_size()
        screen.blit(
            pygame.transform.scale(tiles[list(tiles.keys())[t]].image, (GRID_SIZE, GRID_SIZE)),
            (GRID_SIZE, GRID_SIZE),
        )
        if len(tile.n) > 0:
            screen.blit(
                pygame.transform.scale(tiles[tile.n[n]].image, (GRID_SIZE, GRID_SIZE)),
                (GRID_SIZE, 0),
            )
        if len(tile.s) > 0:
            screen.blit(
                pygame.transform.scale(tiles[tile.s[s]].image, (GRID_SIZE, GRID_SIZE)),
                (GRID_SIZE, 2 * GRID_SIZE),
            )
        if len(tile.w) > 0:
            screen.blit(
                pygame.transform.scale(tiles[tile.w[w]].image, (GRID_SIZE, GRID_SIZE)),
                (0, GRID_SIZE),
            )
        if len(tile.e) > 0:
            screen.blit(
                pygame.transform.scale(tiles[tile.e[e]].image, (GRID_SIZE, GRID_SIZE)),
                (2 * GRID_SIZE, GRID_SIZE),
            )

        pygame.display.flip()
        dt = clock.tick(FRAME_RATE) / 1000

    pygame.quit()
