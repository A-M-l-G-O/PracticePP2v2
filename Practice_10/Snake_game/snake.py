import pygame
import random
import sys
from pygame.locals import *

pygame.init()


CELL  = 20
COLS  = 30
ROWS  = 25
W     = COLS * CELL
H     = ROWS * CELL + 60 
HUD_H = 60

pygame.display.set_caption("Snake")
screen = pygame.display.set_mode((W, H))
clock  = pygame.time.Clock()
font   = pygame.font.SysFont("Arial", 22, bold=True)
big_font = pygame.font.SysFont("Arial", 48, bold=True)

BLACK  = (0,   0,   0)
WHITE  = (255, 255, 255)
GREEN  = (50,  200, 50)
DK_GRN = (30,  140, 30)
RED    = (220, 50,  50)
YELLOW = (255, 220, 0)
GRAY   = (130, 130, 130)
DK_GRAY= (50,  50,  50)
WALL   = (80,  80,  80)
BG     = (20,  20,  20)

UP    = (0, -1)
DOWN  = (0,  1)
LEFT  = (-1, 0)
RIGHT = (1,  0)


LEVELS = [
    (3,  8),
    (4, 11),
    (5, 14),
    (6, 17),
    (7, 20),
]


def grid_to_px(col, row):
    """Top-left pixel of a cell (accounting for HUD)."""
    return col * CELL, row * CELL + HUD_H


def draw_cell(surf, col, row, color, radius=4):
    x, y = grid_to_px(col, row)
    pygame.draw.rect(surf, color,
                     (x + 1, y + 1, CELL - 2, CELL - 2),
                     border_radius=radius)


def random_free_pos(snake_body, walls):
    """Return a (col, row) not on the snake or a wall."""
    while True:
        pos = (random.randint(0, COLS - 1), random.randint(0, ROWS - 1))
        if pos not in snake_body and pos not in walls:
            return pos


def build_walls():
    """Border walls as a set of (col, row)."""
    w = set()
    for c in range(COLS):
        w.add((c, 0))
        w.add((c, ROWS - 1))
    for r in range(ROWS):
        w.add((0, r))
        w.add((COLS - 1, r))
    return w


def draw_hud(surf, score, level):
    pygame.draw.rect(surf, DK_GRAY, (0, 0, W, HUD_H))
    sc = font.render(f"Score: {score}", True, WHITE)
    lv = font.render(f"Level: {level}", True, YELLOW)
    surf.blit(sc, (20, HUD_H // 2 - sc.get_height() // 2))
    surf.blit(lv, (W - lv.get_width() - 20, HUD_H // 2 - lv.get_height() // 2))


def message_screen(surf, lines, colors=None):
    overlay = pygame.Surface((W, H), SRCALPHA)
    overlay.fill((0, 0, 0, 170))
    surf.blit(overlay, (0, 0))
    total_h = len(lines) * 60
    start_y = H // 2 - total_h // 2
    for i, line in enumerate(lines):
        color = (colors[i] if colors and i < len(colors) else WHITE)
        txt = big_font.render(line, True, color) if i == 0 else font.render(line, True, color)
        surf.blit(txt, (W // 2 - txt.get_width() // 2, start_y + i * 60))
    pygame.display.update()


def main():
    walls = build_walls()

    mid_c, mid_r = COLS // 2, ROWS // 2
    snake  = [(mid_c - i, mid_r) for i in range(3)]  
    direction   = RIGHT
    next_dir    = RIGHT

    food = random_free_pos(snake, walls)
    score        = 0
    level        = 1
    food_in_level= 0
    food_needed, fps = LEVELS[0]
    game_active  = True

    while True:
        clock.tick(fps)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if event.type == KEYDOWN:
                if not game_active:
                    if event.key == K_r: main(); return
                    if event.key == K_q: pygame.quit(); sys.exit()
                else:
                    if event.key == K_UP    and direction != DOWN:  next_dir = UP
                    if event.key == K_DOWN  and direction != UP:    next_dir = DOWN
                    if event.key == K_LEFT  and direction != RIGHT: next_dir = LEFT
                    if event.key == K_RIGHT and direction != LEFT:  next_dir = RIGHT

        if not game_active:
            message_screen(screen,
                           ["GAME OVER",
                            f"Score: {score}  Level: {level}",
                            "R = restart   Q = quit"],
                           [RED, WHITE, GRAY])
            continue

        direction = next_dir
        head = (snake[0][0] + direction[0], snake[0][1] + direction[1])

        if head in walls:
            game_active = False
            continue

        if head in snake:
            game_active = False
            continue

        snake.insert(0, head)

        if head == food:
            score        += 10 * level
            food_in_level += 1
            if food_in_level >= food_needed and level < len(LEVELS):
                level        += 1
                food_in_level = 0
                food_needed, fps = LEVELS[level - 1]
                message_screen(screen,
                               [f"LEVEL {level}!", "Speed increased!"],
                               [YELLOW, WHITE])
                pygame.time.wait(800)
            food = random_free_pos(snake, walls)
        else:
            snake.pop()

        screen.fill(BG)

        for r in range(ROWS):
            for c in range(COLS):
                if (c + r) % 2 == 0:
                    pygame.draw.rect(screen, (25, 25, 25),
                                     (c * CELL, r * CELL + HUD_H, CELL, CELL))

        for (c, r) in walls:
            draw_cell(screen, c, r, WALL, radius=0)

        fx, fy = grid_to_px(*food)
        pygame.draw.circle(screen, RED,
                           (fx + CELL // 2, fy + CELL // 2), CELL // 2 - 2)

        for i, (c, r) in enumerate(snake):
            color = DK_GRN if i == 0 else GREEN
            draw_cell(screen, c, r, color)
            if i == 0: 
                ex, ey = grid_to_px(c, r)
                pygame.draw.circle(screen, WHITE, (ex + 6,  ey + 6),  3)
                pygame.draw.circle(screen, WHITE, (ex + 14, ey + 6),  3)
                pygame.draw.circle(screen, BLACK, (ex + 7,  ey + 7),  2)
                pygame.draw.circle(screen, BLACK, (ex + 15, ey + 7),  2)

        draw_hud(screen, score, level)
        pygame.display.update()


main()
