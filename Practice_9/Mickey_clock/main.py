import pygame
import sys
from clock import MickeyClock

W, H = 600, 600
FPS = 1


def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Mickey's Clock")
    clock_obj = MickeyClock(screen, W, H)
    tick = pygame.time.Clock()

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

        clock_obj.draw()
        pygame.display.flip()
        tick.tick(FPS)


if __name__ == "__main__":
    main()
