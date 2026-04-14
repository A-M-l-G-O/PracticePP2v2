import pygame

RADIUS = 25
STEP = 20
COLOR = (220, 40, 40)
OUTLINE = (160, 20, 20)


class Ball:
    def __init__(self, screen_w, screen_h):
        self.sw = screen_w
        self.sh = screen_h
        self.x = screen_w // 2
        self.y = screen_h // 2

    def move(self, dx, dy):
        nx = self.x + dx * STEP
        ny = self.y + dy * STEP
        if RADIUS <= nx <= self.sw - RADIUS:
            self.x = nx
        if RADIUS <= ny <= self.sh - RADIUS:
            self.y = ny

    def draw(self, screen):
        pygame.draw.circle(screen, OUTLINE, (self.x, self.y), RADIUS + 2)
        pygame.draw.circle(screen, COLOR, (self.x, self.y), RADIUS)
        highlight = (self.x - RADIUS // 3, self.y - RADIUS // 3)
        pygame.draw.circle(screen, (255, 120, 120), highlight, RADIUS // 4)
