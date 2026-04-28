import pygame
import sys
from racer import (W, H, FPS, WHITE, BLACK, RED, GRAY, DKGRAY, YELLOW,
                   GREEN, ORANGE, CYAN, ROAD_COLOR, LINE_COLOR,
                   ROAD_LEFT, ROAD_RIGHT, ROAD_W, CAR_COLORS)
from persistence import load_leaderboard, load_settings, save_settings


pygame.font.init()

_font_sm = None
_font_md = None
_font_lg = None
_font_xl = None


def _fonts():
    global _font_sm, _font_md, _font_lg, _font_xl
    if _font_sm is None:
        _font_sm = pygame.font.SysFont("Arial", 18, bold=True)
        _font_md = pygame.font.SysFont("Arial", 22, bold=True)
        _font_lg = pygame.font.SysFont("Arial", 32, bold=True)
        _font_xl = pygame.font.SysFont("Arial", 52, bold=True)


class Button:
    def __init__(self, rect, text, color=DKGRAY, text_color=WHITE):
        self.rect        = pygame.Rect(rect)
        self.text        = text
        self.color       = color
        self.hover_color = tuple(min(c + 40, 255) for c in color)
        self.text_color  = text_color

    def draw(self, surf):
        _fonts()
        mouse = pygame.mouse.get_pos()
        col = self.hover_color if self.rect.collidepoint(mouse) else self.color
        pygame.draw.rect(surf, col, self.rect, border_radius=8)
        pygame.draw.rect(surf, WHITE, self.rect, 2, border_radius=8)
        t = _font_md.render(self.text, True, self.text_color)
        surf.blit(t, (self.rect.centerx - t.get_width() // 2,
                      self.rect.centery - t.get_height() // 2))

    def clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN and
                event.button == 1 and
                self.rect.collidepoint(event.pos))


def _draw_bg(surf):
    surf.fill((20, 20, 40))
    pygame.draw.rect(surf, ROAD_COLOR, (ROAD_LEFT, 0, ROAD_W, H))
    pygame.draw.line(surf, WHITE, (ROAD_LEFT, 0), (ROAD_LEFT, H), 3)
    pygame.draw.line(surf, WHITE, (ROAD_RIGHT, 0), (ROAD_RIGHT, H), 3)


def username_screen(surf, clock) -> str:
    _fonts()
    name = ""
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name.strip():
                    return name.strip()
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif len(name) < 16 and event.unicode.isprintable():
                    name += event.unicode

        _draw_bg(surf)
        title = _font_lg.render("Enter Your Name", True, YELLOW)
        surf.blit(title, (W // 2 - title.get_width() // 2, 160))

        box = pygame.Rect(W // 2 - 120, 240, 240, 44)
        pygame.draw.rect(surf, DKGRAY, box, border_radius=8)
        pygame.draw.rect(surf, YELLOW, box, 2, border_radius=8)
        t = _font_md.render(name + "|", True, WHITE)
        surf.blit(t, (box.x + 10, box.y + 10))

        hint = _font_sm.render("Press ENTER to continue", True, GRAY)
        surf.blit(hint, (W // 2 - hint.get_width() // 2, 310))

        pygame.display.update()
        clock.tick(FPS)


def main_menu(surf, clock) -> str:
    """Returns: 'play' | 'leaderboard' | 'settings' | 'quit'"""
    _fonts()
    btn_play  = Button((W // 2 - 100, 220, 200, 48), "▶  Play",   color=(30, 120, 30))
    btn_board = Button((W // 2 - 100, 285, 200, 48), "🏆 Leaderboard")
    btn_set   = Button((W // 2 - 100, 350, 200, 48), "⚙  Settings")
    btn_quit  = Button((W // 2 - 100, 415, 200, 48), "✕  Quit",   color=(120, 30, 30))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if btn_play.clicked(event):  return "play"
            if btn_board.clicked(event): return "leaderboard"
            if btn_set.clicked(event):   return "settings"
            if btn_quit.clicked(event):
                pygame.quit(); sys.exit()

        _draw_bg(surf)
        title = _font_xl.render("RACER", True, YELLOW)
        surf.blit(title, (W // 2 - title.get_width() // 2, 110))
        sub = _font_sm.render("Dodge, collect, survive!", True, GRAY)
        surf.blit(sub, (W // 2 - sub.get_width() // 2, 175))

        for btn in (btn_play, btn_board, btn_set, btn_quit):
            btn.draw(surf)
        pygame.display.update()
        clock.tick(FPS)


def settings_screen(surf, clock) -> dict:
    _fonts()
    settings = load_settings()
    btn_back = Button((W // 2 - 80, 530, 160, 42), "← Back")

    color_names = list(CAR_COLORS.keys())
    diff_names  = ["Easy", "Normal", "Hard"]

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos

                if pygame.Rect(W // 2 + 20, 175, 120, 34).collidepoint(mx, my):
                    settings["sound"] = not settings["sound"]
                    save_settings(settings)

                if pygame.Rect(W // 2 + 20, 250, 120, 34).collidepoint(mx, my):
                    idx = (color_names.index(settings["car_color"]) + 1) % len(color_names)
                    settings["car_color"] = color_names[idx]
                    save_settings(settings)

                if pygame.Rect(W // 2 + 20, 325, 120, 34).collidepoint(mx, my):
                    idx = (diff_names.index(settings["difficulty"]) + 1) % len(diff_names)
                    settings["difficulty"] = diff_names[idx]
                    save_settings(settings)

            if btn_back.clicked(event):
                return settings

        _draw_bg(surf)
        title = _font_lg.render("Settings", True, YELLOW)
        surf.blit(title, (W // 2 - title.get_width() // 2, 80))

        def _row(label, value, y, val_color=WHITE):
            lbl = _font_md.render(label, True, GRAY)
            surf.blit(lbl, (ROAD_LEFT + 10, y + 6))
            box = pygame.Rect(W // 2 + 20, y, 120, 34)
            pygame.draw.rect(surf, DKGRAY, box, border_radius=6)
            pygame.draw.rect(surf, WHITE, box, 1, border_radius=6)
            v = _font_md.render(str(value), True, val_color)
            surf.blit(v, (box.centerx - v.get_width() // 2,
                          box.centery - v.get_height() // 2))

        _row("Sound",      "ON" if settings["sound"] else "OFF", 175,
             GREEN if settings["sound"] else RED)
        col_rgb = CAR_COLORS[settings["car_color"]]
        _row("Car Color",  settings["car_color"], 250, col_rgb)
        diff_colors = {"Easy": GREEN, "Normal": YELLOW, "Hard": RED}
        _row("Difficulty", settings["difficulty"], 325,
             diff_colors[settings["difficulty"]])

        hint = _font_sm.render("Click value to cycle options", True, GRAY)
        surf.blit(hint, (W // 2 - hint.get_width() // 2, 390))

        btn_back.draw(surf)
        pygame.display.update()
        clock.tick(FPS)


def leaderboard_screen(surf, clock):
    _fonts()
    btn_back = Button((W // 2 - 80, 540, 160, 42), "← Back")
    board = load_leaderboard()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if btn_back.clicked(event):
                return

        _draw_bg(surf)
        title = _font_lg.render("🏆 Top 10", True, YELLOW)
        surf.blit(title, (W // 2 - title.get_width() // 2, 30))

        hdr = _font_sm.render(f"{'#':<3} {'Name':<14} {'Score':>6}  {'Dist':>5}  {'Coins':>5}", True, GRAY)
        surf.blit(hdr, (ROAD_LEFT - 10, 90))
        pygame.draw.line(surf, GRAY, (ROAD_LEFT - 10, 112), (ROAD_RIGHT + 10, 112), 1)

        medal = {0: "🥇", 1: "🥈", 2: "🥉"}
        for i, entry in enumerate(board[:10]):
            rank_str = medal.get(i, f"{i+1}.")
            row = (f"{rank_str:<3} {entry['name']:<14} "
                   f"{entry['score']:>6}  {entry['distance']:>5}m  {entry['coins']:>4}c")
            color = [YELLOW, (192, 192, 192), (205, 127, 50)][i] if i < 3 else WHITE
            t = _font_sm.render(row, True, color)
            surf.blit(t, (ROAD_LEFT - 10, 120 + i * 36))

        if not board:
            empty = _font_md.render("No scores yet — play first!", True, GRAY)
            surf.blit(empty, (W // 2 - empty.get_width() // 2, 200))

        btn_back.draw(surf)
        pygame.display.update()
        clock.tick(FPS)


def game_over_screen(surf, clock, score, distance, coins) -> str:
    """Returns 'retry' or 'menu'."""
    _fonts()
    btn_retry = Button((W // 2 - 110, 370, 200, 48), "↺  Retry",   color=(30, 100, 30))
    btn_menu  = Button((W // 2 - 110, 435, 200, 48), "⌂  Main Menu")

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if btn_retry.clicked(event): return "retry"
            if btn_menu.clicked(event):  return "menu"

        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surf.blit(overlay, (0, 0))

        title = _font_xl.render("GAME OVER", True, RED)
        surf.blit(title, (W // 2 - title.get_width() // 2, 130))

        for i, line in enumerate([
            f"Score:    {score}",
            f"Distance: {distance} m",
            f"Coins:    {coins}",
        ]):
            t = _font_md.render(line, True, WHITE)
            surf.blit(t, (W // 2 - t.get_width() // 2, 230 + i * 38))

        btn_retry.draw(surf)
        btn_menu.draw(surf)
        pygame.display.update()
        clock.tick(FPS)


def draw_hud(surf, score, coins, distance, active_pu, pu_timer, shield):
    _fonts()
    s = _font_md.render(f"Score: {score}", True, WHITE)
    surf.blit(s, (ROAD_LEFT + 4, 8))

    pygame.draw.circle(surf, YELLOW, (ROAD_RIGHT - 60, 20), 10)
    c = _font_md.render(f"x{coins}", True, WHITE)
    surf.blit(c, (ROAD_RIGHT - 45, 8))

    d = _font_sm.render(f"{distance}m", True, (180, 255, 180))
    surf.blit(d, (W // 2 - d.get_width() // 2, 8))

    if active_pu:
        pu_colors = {"Nitro": ORANGE, "Shield": CYAN, "Repair": GREEN}
        col = pu_colors.get(active_pu, WHITE)
        secs = max(0, pu_timer // FPS)
        pu_text = f"{active_pu}  {secs}s" if pu_timer > 0 else active_pu
        bar = _font_sm.render(pu_text, True, col)
        bx = W // 2 - bar.get_width() // 2 - 6
        pygame.draw.rect(surf, (0, 0, 0, 160),
                         (bx - 2, H - 34, bar.get_width() + 16, 26),
                         border_radius=5)
        surf.blit(bar, (bx + 6, H - 30))

    if shield:
        si = _font_sm.render("🛡 Shield", True, CYAN)
        surf.blit(si, (ROAD_LEFT + 4, H - 30))


def draw_road(surf, offset):
    surf.fill((34, 100, 34))
    pygame.draw.rect(surf, ROAD_COLOR, (ROAD_LEFT, 0, ROAD_W, H))
    dash_h, gap = 40, 20
    total = dash_h + gap
    start = (-offset % total) - total
    for y in range(int(start), H, total):
        pygame.draw.rect(surf, LINE_COLOR, (W // 2 - 3, y, 6, dash_h))
    for lx in [ROAD_LEFT + ROAD_W // 3, ROAD_LEFT + 2 * ROAD_W // 3]:
        for y in range(int(start), H, total):
            pygame.draw.rect(surf, (160, 160, 160), (lx - 1, y, 2, dash_h))
    pygame.draw.line(surf, WHITE, (ROAD_LEFT,  0), (ROAD_LEFT,  H), 4)
    pygame.draw.line(surf, WHITE, (ROAD_RIGHT, 0), (ROAD_RIGHT, H), 4)