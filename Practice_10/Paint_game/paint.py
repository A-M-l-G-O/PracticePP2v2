import pygame
import sys
from pygame.locals import *

pygame.init()

W, H    = 900, 650
TOOL_H  = 80   
CANVAS_H = H - TOOL_H

pygame.display.set_caption("Paint")
screen = pygame.display.set_mode((W, H))
clock  = pygame.time.Clock()
font   = pygame.font.SysFont("Arial", 15, bold=True)


PALETTE = [
    (0,   0,   0),    # black
    (255, 255, 255),  # white
    (220, 50,  50),   # red
    (50,  180, 50),   # green
    (50,  50,  220),  # blue
    (255, 220, 0),    # yellow
    (255, 140, 0),    # orange
    (180, 0,   220),  # purple
    (0,   200, 200),  # cyan
    (255, 105, 180),  # pink
    (100, 60,  20),   # brown
    (140, 140, 140),  # gray
]

TOOLS = ["pencil", "rect", "circle", "eraser"]
TOOL_ICONS = {
    "pencil": "✏️",
    "rect":   "▭",
    "circle": "○",
    "eraser": "◻",
}

SIZES = [2, 5, 10, 20]

canvas  = pygame.Surface((W, CANVAS_H))
canvas.fill((255, 255, 255))

cur_color  = PALETTE[0]
cur_tool   = "pencil"
cur_size   = SIZES[1]
drawing    = False
start_pos  = None          
preview    = None          


def draw_toolbar():
    """Render the toolbar at the top of the screen."""
    pygame.draw.rect(screen, (230, 230, 230), (0, 0, W, TOOL_H))
    pygame.draw.line(screen, (160, 160, 160), (0, TOOL_H), (W, TOOL_H), 2)

    PAL_X = 10
    for i, col in enumerate(PALETTE):
        rx = PAL_X + i * 38
        ry = 10
        rw, rh = 30, 30
        pygame.draw.rect(screen, col, (rx, ry, rw, rh), border_radius=4)
        if col == cur_color:
            pygame.draw.rect(screen, (0, 0, 0), (rx - 2, ry - 2, rw + 4, rh + 4),
                             2, border_radius=5)
        rx2 = PAL_X + i * 38
        ry2 = 44
    for i, col in enumerate(PALETTE):
        row = i // 6
        col_idx = i % 6
        rx = PAL_X + col_idx * 38
        ry = 8 + row * 34
        pygame.draw.rect(screen, col, (rx, ry, 30, 28), border_radius=4)
        if col == cur_color:
            pygame.draw.rect(screen, (0, 0, 0),
                             (rx - 2, ry - 2, 34, 32), 2, border_radius=5)

    TOOL_X = PAL_X + 6 * 38 + 20
    for i, t in enumerate(TOOLS):
        tx = TOOL_X + i * 70
        active = (t == cur_tool)
        bg = (180, 220, 255) if active else (200, 200, 200)
        pygame.draw.rect(screen, bg, (tx, 10, 60, 55), border_radius=8)
        pygame.draw.rect(screen, (100, 100, 100), (tx, 10, 60, 55), 2, border_radius=8)
        lbl = font.render(t, True, (0, 0, 0))
        screen.blit(lbl, (tx + 30 - lbl.get_width() // 2, 46))
        cx, cy = tx + 30, 28
        if t == "pencil":
            pygame.draw.line(screen, (0, 0, 0), (cx - 8, cy + 8), (cx + 8, cy - 8), 3)
            pygame.draw.polygon(screen, (200, 160, 0),
                                [(cx + 6, cy - 10), (cx + 12, cy - 4),
                                 (cx + 8, cy - 8)])
        elif t == "rect":
            pygame.draw.rect(screen, (80, 80, 80), (cx - 10, cy - 8, 20, 16), 2)
        elif t == "circle":
            pygame.draw.circle(screen, (80, 80, 80), (cx, cy), 10, 2)
        elif t == "eraser":
            pygame.draw.rect(screen, (255, 200, 200), (cx - 10, cy - 8, 20, 16),
                             border_radius=3)
            pygame.draw.rect(screen, (180, 120, 120), (cx - 10, cy - 8, 20, 16),
                             2, border_radius=3)

    SZ_X = TOOL_X + len(TOOLS) * 70 + 20
    sz_lbl = font.render("Size:", True, (60, 60, 60))
    screen.blit(sz_lbl, (SZ_X, 8))
    for i, sz in enumerate(SIZES):
        bx = SZ_X + i * 44
        by = 28
        active = (sz == cur_size)
        pygame.draw.circle(screen, (80, 80, 80) if active else (160, 160, 160),
                           (bx + 15, by + 15), sz if sz <= 15 else 15)
        if active:
            pygame.draw.circle(screen, (0, 0, 0),
                               (bx + 15, by + 15),
                               (sz if sz <= 15 else 15) + 2, 2)
        s = font.render(str(sz), True, (0, 0, 0))
        screen.blit(s, (bx + 15 - s.get_width() // 2, by + 36))

    CLR_X = W - 80
    pygame.draw.rect(screen, (255, 100, 100), (CLR_X, 20, 65, 36), border_radius=8)
    clr = font.render("Clear", True, WHITE)
    WHITE = (255, 255, 255)
    screen.blit(clr, (CLR_X + 32 - clr.get_width() // 2, 30))


WHITE = (255, 255, 255)


def draw_toolbar(): 
    pygame.draw.rect(screen, (230, 230, 230), (0, 0, W, TOOL_H))
    pygame.draw.line(screen, (160, 160, 160), (0, TOOL_H), (W, TOOL_H), 2)

    PAL_X = 10
    for i, col in enumerate(PALETTE):
        row = i // 6
        ci  = i % 6
        rx  = PAL_X + ci * 38
        ry  = 8 + row * 34
        pygame.draw.rect(screen, col, (rx, ry, 30, 28), border_radius=4)
        if col == cur_color:
            pygame.draw.rect(screen, (0, 0, 0),
                             (rx - 2, ry - 2, 34, 32), 2, border_radius=5)

    TOOL_X = PAL_X + 6 * 38 + 20
    for i, t in enumerate(TOOLS):
        tx = TOOL_X + i * 70
        active = (t == cur_tool)
        bg = (180, 220, 255) if active else (200, 200, 200)
        pygame.draw.rect(screen, bg, (tx, 8, 62, 58), border_radius=8)
        pygame.draw.rect(screen, (100, 100, 100), (tx, 8, 62, 58), 2, border_radius=8)
        lbl = font.render(t, True, (0, 0, 0))
        screen.blit(lbl, (tx + 31 - lbl.get_width() // 2, 50))
        cx, cy = tx + 31, 28
        if t == "pencil":
            pygame.draw.line(screen, (0, 0, 0), (cx - 8, cy + 8), (cx + 6, cy - 6), 3)
        elif t == "rect":
            pygame.draw.rect(screen, (80, 80, 80), (cx - 10, cy - 8, 20, 16), 2)
        elif t == "circle":
            pygame.draw.circle(screen, (80, 80, 80), (cx, cy), 10, 2)
        elif t == "eraser":
            pygame.draw.rect(screen, (255, 200, 200),
                             (cx - 10, cy - 8, 20, 16), border_radius=3)
            pygame.draw.rect(screen, (180, 120, 120),
                             (cx - 10, cy - 8, 20, 16), 2, border_radius=3)

    SZ_X = TOOL_X + len(TOOLS) * 70 + 15
    sz_lbl = font.render("Size:", True, (60, 60, 60))
    screen.blit(sz_lbl, (SZ_X, 6))
    for i, sz in enumerate(SIZES):
        bx = SZ_X + i * 46
        by = 22
        active = (sz == cur_size)
        r = min(sz, 14)
        pygame.draw.circle(screen, (80, 80, 80) if active else (160, 160, 160),
                           (bx + 16, by + 15), r)
        if active:
            pygame.draw.circle(screen, (0, 0, 0), (bx + 16, by + 15), r + 2, 2)
        s = font.render(str(sz), True, (0, 0, 0))
        screen.blit(s, (bx + 16 - s.get_width() // 2, by + 36))

    CLR_X = W - 80
    pygame.draw.rect(screen, (255, 80, 80), (CLR_X, 22, 68, 32), border_radius=8)
    clr = font.render("Clear", True, WHITE)
    screen.blit(clr, (CLR_X + 34 - clr.get_width() // 2, 30))


def canvas_pos(mx, my):
    """Convert mouse pos to canvas-relative pos."""
    return mx, my - TOOL_H


def hit_palette(mx, my):
    PAL_X = 10
    for i, col in enumerate(PALETTE):
        row = i // 6
        ci  = i % 6
        rx  = PAL_X + ci * 38
        ry  = 8 + row * 34
        if rx <= mx <= rx + 30 and ry <= my <= ry + 28:
            return col
    return None


def hit_tool(mx, my):
    TOOL_X = 10 + 6 * 38 + 20
    for i, t in enumerate(TOOLS):
        tx = TOOL_X + i * 70
        if tx <= mx <= tx + 62 and 8 <= my <= 66:
            return t
    return None


def hit_size(mx, my):
    SZ_X = 10 + 6 * 38 + 20 + len(TOOLS) * 70 + 15
    for i, sz in enumerate(SIZES):
        bx = SZ_X + i * 46
        if bx <= mx <= bx + 32 and 22 <= my <= 60:
            return sz
    return None


def hit_clear(mx, my):
    CLR_X = W - 80
    return CLR_X <= mx <= CLR_X + 68 and 22 <= my <= 54


def draw_shape_preview(surf, tool, start, end, color, size):
    """Draw a live preview of rect/circle while dragging."""
    x1, y1 = start
    x2, y2 = end
    if tool == "rect":
        rx = min(x1, x2); ry = min(y1, y2)
        rw = abs(x2 - x1); rh = abs(y2 - y1)
        pygame.draw.rect(surf, color, (rx, ry, rw, rh), max(1, size))
    elif tool == "circle":
        cx = (x1 + x2) // 2; cy = (y1 + y2) // 2
        r  = int(((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5 // 2)
        if r > 0:
            pygame.draw.circle(surf, color, (cx, cy), r, max(1, size))



def main():
    global cur_color, cur_tool, cur_size, drawing, start_pos, preview, canvas

    prev_mouse = None

    while True:
        clock.tick(60)
        mx, my = pygame.mouse.get_pos()
        on_canvas = my >= TOOL_H

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()

            if event.type == MOUSEBUTTONDOWN and my < TOOL_H:
                col = hit_palette(mx, my)
                if col:
                    cur_color = col
                t = hit_tool(mx, my)
                if t:
                    cur_tool = t
                sz = hit_size(mx, my)
                if sz:
                    cur_size = sz
                if hit_clear(mx, my):
                    canvas.fill(WHITE)

            if event.type == MOUSEBUTTONDOWN and on_canvas:
                drawing = True
                cp = canvas_pos(mx, my)
                start_pos = cp
                if cur_tool in ("pencil", "eraser"):
                    prev_mouse = cp

            if event.type == MOUSEBUTTONUP and drawing:
                drawing = False
                cp = canvas_pos(mx, my)
                if cur_tool == "rect":
                    draw_shape_preview(canvas, "rect", start_pos, cp, cur_color, cur_size)
                elif cur_tool == "circle":
                    draw_shape_preview(canvas, "circle", start_pos, cp, cur_color, cur_size)
                prev_mouse = None
                start_pos  = None

        if drawing and on_canvas:
            cp = canvas_pos(mx, my)
            if cur_tool in ("pencil", "eraser"):
                col = WHITE if cur_tool == "eraser" else cur_color
                if prev_mouse:
                    pygame.draw.line(canvas, col, prev_mouse, cp, cur_size)
                pygame.draw.circle(canvas, col, cp, cur_size // 2)
                prev_mouse = cp

        screen.blit(canvas, (0, TOOL_H))

        if drawing and start_pos and cur_tool in ("rect", "circle"):
            cp = canvas_pos(mx, my)
            preview_surf = canvas.copy()
            draw_shape_preview(preview_surf, cur_tool, start_pos, cp, cur_color, cur_size)
            screen.blit(preview_surf, (0, TOOL_H))

        draw_toolbar()
        pygame.display.update()


main()
