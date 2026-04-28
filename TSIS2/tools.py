import pygame
from collections import deque


def flood_fill(surface: pygame.Surface, start_x: int, start_y: int, fill_color):
    """
    BFS flood-fill on *surface* starting at (start_x, start_y).
    Fills contiguous pixels that exactly match the color at the start pixel
    with *fill_color*.  No extra libraries needed — uses get_at / set_at.
    """
    w, h = surface.get_size()
    if not (0 <= start_x < w and 0 <= start_y < h):
        return

    target_color = surface.get_at((start_x, start_y))[:3]   # ignore alpha
    fill_rgb      = fill_color[:3] if len(fill_color) > 2 else fill_color

    if target_color == fill_rgb:
        return  

    surface.lock()
    queue   = deque()
    queue.append((start_x, start_y))
    visited = set()
    visited.add((start_x, start_y))

    while queue:
        x, y = queue.popleft()
        if surface.get_at((x, y))[:3] != target_color:
            continue
        surface.set_at((x, y), fill_rgb)
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in visited:
                visited.add((nx, ny))
                queue.append((nx, ny))

    surface.unlock()


def draw_shape_preview(surf, tool, start, end, color, size):
    """
    Draw a live / final preview of rect, circle, or line onto *surf*.
    *start* and *end* are canvas-relative coordinates.
    """
    x1, y1 = start
    x2, y2 = end
    if tool == "rect":
        rx = min(x1, x2); ry = min(y1, y2)
        rw = abs(x2 - x1); rh = abs(y2 - y1)
        if rw > 0 and rh > 0:
            pygame.draw.rect(surf, color, (rx, ry, rw, rh), max(1, size))
    elif tool == "circle":
        cx = (x1 + x2) // 2; cy = (y1 + y2) // 2
        r  = int(((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5 // 2)
        if r > 0:
            pygame.draw.circle(surf, color, (cx, cy), r, max(1, size))
    elif tool == "line":
        pygame.draw.line(surf, color, (x1, y1), (x2, y2), max(1, size))
