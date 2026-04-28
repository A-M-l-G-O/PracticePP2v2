import pygame
import sys
from datetime import datetime
from pygame.locals import *

from tools import flood_fill, draw_shape_preview

pygame.init()

W, H      = 960, 680
TOOL_H    = 82
CANVAS_H  = H - TOOL_H
WHITE     = (255, 255, 255)
BG        = (225, 225, 228)

screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Paint  —  TSIS 2")
clock  = pygame.time.Clock()
font   = pygame.font.SysFont("Arial", 14, bold=True)
font_s = pygame.font.SysFont("Arial", 12)

PALETTE = [
    (0,   0,   0),    (255, 255, 255),
    (220, 50,  50),   (50,  180, 50),
    (50,  50,  220),  (255, 220, 0),
    (255, 140, 0),    (180, 0,   220),
    (0,   200, 200),  (255, 105, 180),
    (100, 60,  20),   (140, 140, 140),
]

TOOLS = ["pencil", "line", "rect", "circle", "fill", "text", "eraser"]
SIZES = [2, 5, 10, 20]                  

canvas = pygame.Surface((W, CANVAS_H))
canvas.fill(WHITE)

cur_color  = PALETTE[0]
cur_tool   = "pencil"
cur_size   = SIZES[1]
drawing    = False
start_pos  = None

text_active   = False   
text_pos      = None     
text_buffer   = ""      
text_font     = pygame.font.SysFont("Arial", 22)

PAL_X   = 10
PAL_COLS = 6
TOOL_X  = PAL_X + PAL_COLS * 38 + 16
SZ_X    = TOOL_X + len(TOOLS) * 64 + 12
CLR_X   = W - 80


def canvas_pos(mx, my):
    return mx, my - TOOL_H


def hit_palette(mx, my):
    for i, col in enumerate(PALETTE):
        row = i // PAL_COLS
        ci  = i % PAL_COLS
        rx  = PAL_X + ci * 38
        ry  = 8 + row * 34
        if rx <= mx <= rx + 30 and ry <= my <= ry + 28:
            return col
    return None


def hit_tool(mx, my):
    for i, t in enumerate(TOOLS):
        tx = TOOL_X + i * 64
        if tx <= mx <= tx + 58 and 8 <= my <= 70:
            return t
    return None


def hit_size(mx, my):
    for i, sz in enumerate(SIZES):
        bx = SZ_X + i * 46
        if bx <= mx <= bx + 36 and 22 <= my <= 62:
            return sz
    return None


def hit_clear(mx, my):
    return CLR_X <= mx <= CLR_X + 68 and 22 <= my <= 54


def draw_toolbar():
    pygame.draw.rect(screen, BG, (0, 0, W, TOOL_H))
    pygame.draw.line(screen, (160, 160, 160), (0, TOOL_H), (W, TOOL_H), 2)

    for i, col in enumerate(PALETTE):
        row = i // PAL_COLS
        ci  = i % PAL_COLS
        rx  = PAL_X + ci * 38
        ry  = 8 + row * 34
        pygame.draw.rect(screen, col, (rx, ry, 30, 28), border_radius=4)
        if col == cur_color:
            pygame.draw.rect(screen, (0, 0, 0), (rx - 2, ry - 2, 34, 32), 2, border_radius=5)

    for i, t in enumerate(TOOLS):
        tx     = TOOL_X + i * 64
        active = (t == cur_tool)
        bg     = (180, 210, 255) if active else (205, 205, 205)
        pygame.draw.rect(screen, bg, (tx, 8, 58, 60), border_radius=8)
        pygame.draw.rect(screen, (110, 110, 110), (tx, 8, 58, 60), 2, border_radius=8)
        lbl = font_s.render(t, True, (0, 0, 0))
        screen.blit(lbl, (tx + 29 - lbl.get_width() // 2, 54))
        cx, cy = tx + 29, 30
        if t == "pencil":
            pygame.draw.line(screen, (0, 0, 0), (cx - 8, cy + 8), (cx + 6, cy - 6), 3)
        elif t == "line":
            pygame.draw.line(screen, (60, 60, 60), (cx - 10, cy + 8), (cx + 10, cy - 8), 3)
        elif t == "rect":
            pygame.draw.rect(screen, (80, 80, 80), (cx - 10, cy - 8, 20, 16), 2)
        elif t == "circle":
            pygame.draw.circle(screen, (80, 80, 80), (cx, cy), 10, 2)
        elif t == "fill":
            pygame.draw.circle(screen, cur_color, (cx, cy), 9)
            pygame.draw.circle(screen, (60, 60, 60), (cx, cy), 9, 2)
            lf = font_s.render("F", True, (255, 255, 255) if sum(cur_color) < 380 else (0, 0, 0))
            screen.blit(lf, (cx - lf.get_width() // 2, cy - lf.get_height() // 2))
        elif t == "text":
            lt = font.render("A", True, (60, 60, 60))
            screen.blit(lt, (cx - lt.get_width() // 2, cy - lt.get_height() // 2))
        elif t == "eraser":
            pygame.draw.rect(screen, (255, 200, 200), (cx - 10, cy - 8, 20, 16), border_radius=3)
            pygame.draw.rect(screen, (180, 120, 120), (cx - 10, cy - 8, 20, 16), 2, border_radius=3)

    sz_lbl = font_s.render("Size (1-4):", True, (60, 60, 60))
    screen.blit(sz_lbl, (SZ_X, 6))
    for i, sz in enumerate(SIZES):
        bx     = SZ_X + i * 46
        by     = 22
        active = (sz == cur_size)
        r      = min(sz, 14)
        pygame.draw.circle(screen, (80, 80, 80) if active else (170, 170, 170),
                           (bx + 16, by + 15), r)
        if active:
            pygame.draw.circle(screen, (0, 0, 0), (bx + 16, by + 15), r + 2, 2)
        s = font_s.render(str(i + 1), True, (0, 0, 0))
        screen.blit(s, (bx + 16 - s.get_width() // 2, by + 36))

    pygame.draw.rect(screen, (235, 80, 80), (CLR_X, 22, 68, 32), border_radius=8)
    clr = font.render("Clear", True, WHITE)
    screen.blit(clr, (CLR_X + 34 - clr.get_width() // 2, 30))

    hint = font_s.render("Ctrl+S = save", True, (110, 110, 110))
    screen.blit(hint, (CLR_X - hint.get_width() - 8, 36))


def render_text_cursor(surf, pos, text, col):
    """Blit text + blinking cursor onto *surf* at canvas position *pos*."""
    rendered = text_font.render(text + "|", True, col)
    surf.blit(rendered, pos)


def commit_text():
    """Permanently draw the text_buffer onto the canvas."""
    global text_active, text_buffer, text_pos
    if text_buffer and text_pos:
        rendered = text_font.render(text_buffer, True, cur_color)
        canvas.blit(rendered, text_pos)
    text_active  = False
    text_buffer  = ""
    text_pos     = None


def cancel_text():
    global text_active, text_buffer, text_pos
    text_active = False
    text_buffer = ""
    text_pos    = None


def save_canvas():
    ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"canvas_{ts}.png"
    pygame.image.save(canvas, filename)
    print(f"[Saved] {filename}")
    # Brief on-screen notification
    notif = font.render(f"Saved: {filename}", True, (0, 120, 0))
    screen.blit(notif, (10, H - 24))
    pygame.display.update()
    pygame.time.delay(1200)


def main():
    global cur_color, cur_tool, cur_size, drawing, start_pos
    global text_active, text_buffer, text_pos

    prev_mouse = None

    while True:
        clock.tick(60)
        mx, my = pygame.mouse.get_pos()
        on_canvas = my >= TOOL_H

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN:
                if event.key == K_s and (pygame.key.get_mods() & KMOD_CTRL):
                    save_canvas()
                    continue

                if not text_active:
                    if event.key == K_1: cur_size = SIZES[0]
                    elif event.key == K_2: cur_size = SIZES[1]
                    elif event.key == K_3: cur_size = SIZES[2]
                    elif event.key == K_4: cur_size = SIZES[3]

                if text_active:
                    if event.key == K_RETURN:
                        commit_text()
                    elif event.key == K_ESCAPE:
                        cancel_text()
                    elif event.key == K_BACKSPACE:
                        text_buffer = text_buffer[:-1]
                    else:
                        if event.unicode and event.unicode.isprintable():
                            text_buffer += event.unicode

            if event.type == MOUSEBUTTONDOWN and my < TOOL_H:
                col = hit_palette(mx, my)
                if col:
                    cur_color = col
                t = hit_tool(mx, my)
                if t:
                    cur_tool = t
                    if t != "text":
                        cancel_text()
                sz = hit_size(mx, my)
                if sz:
                    cur_size = sz
                if hit_clear(mx, my):
                    canvas.fill(WHITE)
                    cancel_text()

            if event.type == MOUSEBUTTONDOWN and on_canvas:
                cp = canvas_pos(mx, my)

                if cur_tool == "fill":
                    flood_fill(canvas, cp[0], cp[1], cur_color)

                elif cur_tool == "text":
                    if text_active:
                        commit_text()
                    text_active = True
                    text_pos    = cp
                    text_buffer = ""

                else:
                    cancel_text()
                    drawing   = True
                    start_pos = cp
                    if cur_tool in ("pencil", "eraser"):
                        prev_mouse = cp

            if event.type == MOUSEBUTTONUP and drawing:
                drawing = False
                cp      = canvas_pos(mx, my)
                if cur_tool in ("rect", "circle", "line"):
                    draw_shape_preview(canvas, cur_tool, start_pos, cp,
                                       cur_color, cur_size)
                prev_mouse = None
                start_pos  = None

        if drawing and on_canvas:
            cp = canvas_pos(mx, my)
            if cur_tool in ("pencil", "eraser"):
                col = WHITE if cur_tool == "eraser" else cur_color
                if prev_mouse:
                    pygame.draw.line(canvas, col, prev_mouse, cp, cur_size)
                pygame.draw.circle(canvas, col, cp, max(1, cur_size // 2))
                prev_mouse = cp

        screen.blit(canvas, (0, TOOL_H))

        if drawing and start_pos and cur_tool in ("rect", "circle", "line"):
            cp           = canvas_pos(mx, my)
            preview_surf = canvas.copy()
            draw_shape_preview(preview_surf, cur_tool, start_pos, cp,
                               cur_color, cur_size)
            screen.blit(preview_surf, (0, TOOL_H))

        if text_active and text_pos:
            tx, ty = text_pos
            render_text_cursor(screen, (tx, ty + TOOL_H), text_buffer, cur_color)

        draw_toolbar()
        pygame.display.update()


main()
