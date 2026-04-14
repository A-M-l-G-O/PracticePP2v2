import pygame
import sys
from ball import Ball

W, H = 600, 600
FPS = 60
BG = (245, 245, 245)
GRID = (220, 220, 220)


def draw_grid(screen):
    for x in range(0, W, 40):
        pygame.draw.line(screen, GRID, (x, 0), (x, H))
    for y in range(0, H, 40):
        pygame.draw.line(screen, GRID, (0, y), (W, y))


def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Moving Ball")
    font = pygame.font.SysFont("monospace", 18)
    ball = Ball(W, H)
    tick = pygame.time.Clock()

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif e.key == pygame.K_UP:
                    ball.move(0, -1)
                elif e.key == pygame.K_DOWN:
                    ball.move(0, 1)
                elif e.key == pygame.K_LEFT:
                    ball.move(-1, 0)
                elif e.key == pygame.K_RIGHT:
                    ball.move(1, 0)

        screen.fill(BG)
        draw_grid(screen)
        ball.draw(screen)

        info = font.render(f"Pos: ({ball.x}, {ball.y})  |  Arrow keys to move  |  ESC to quit", True, (100, 100, 100))
        screen.blit(info, (10, H - 26))

        pygame.display.flip()
        tick.tick(FPS)


if __name__ == "__main__":
    main()
