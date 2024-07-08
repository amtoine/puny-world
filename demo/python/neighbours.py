import pygame
from pathlib import Path
from tileset import load_tileset, compute_neighbours


if __name__ == "__main__":
    tiles, _, _ = load_tileset(Path("metadata/punyworld.json"))

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
        if len(tile.n) > 0:
            screen.blit(
                pygame.transform.scale(tiles[tile.n[n]].image, (128, 128)),
                (width / 2, height / 2 - 128),
            )
        if len(tile.s) > 0:
            screen.blit(
                pygame.transform.scale(tiles[tile.s[s]].image, (128, 128)),
                (width / 2, height / 2 + 128),
            )
        if len(tile.w) > 0:
            screen.blit(
                pygame.transform.scale(tiles[tile.w[w]].image, (128, 128)),
                (width / 2 - 128, height / 2),
            )
        if len(tile.e) > 0:
            screen.blit(
                pygame.transform.scale(tiles[tile.e[e]].image, (128, 128)),
                (width / 2 + 128, height / 2),
            )

        pygame.display.flip()
        dt = clock.tick(frame_rate) / 1000

    pygame.quit()
