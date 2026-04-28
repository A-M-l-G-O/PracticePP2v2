"""Entry point: manages all screens and ties everything together."""

import sys
import json
import datetime
import pygame
from pygame.locals import *

import db
from game import GameState, build_border_walls
from config import (
    CELL, COLS, ROWS, W, H, HUD_H,
    BLACK, WHITE, RED, YELLOW, GRAY, DK_GRAY,
    WALL_C, BG, POISON, PURPLE, CYAN, ORANGE, OBS_C, DK_GRN,
    UP, DOWN, LEFT, RIGHT,
)

# ── init ────────────────────────────────────────────────────────────────────
pygame.init()
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Snake — TSIS 4")
clock = pygame.font.SysFont("Arial", 22, bold=True)  
clock_ = pygame.time.Clock()

FONT       = pygame.font.SysFont("Arial", 22, bold=True)
BIG_FONT   = pygame.font.SysFont("Arial", 46, bold=True)
SMALL_FONT = pygame.font.SysFont("Arial", 17)

SETTINGS_FILE = "settings.json"

def load_settings():
    try:
        with open(SETTINGS_FILE) as f:
            return json.load(f)
    except Exception:
        return {"snake_color": [50, 200, 50], "grid_overlay": True, "sound": False}


def save_settings(s):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(s, f, indent=4)

def grid_to_px(col, row):
    return col * CELL, row * CELL + HUD_H


def draw_cell(surf, col, row, color, radius=4):
    x, y = grid_to_px(col, row)
    pygame.draw.rect(surf, color,
                     (x + 1, y + 1, CELL - 2, CELL - 2),
                     border_radius=radius)


def draw_button(surf, rect, text, bg=(70, 70, 70), fg=WHITE, hover=False):
    colour = (100, 100, 100) if hover else bg
    pygame.draw.rect(surf, colour, rect, border_radius=8)
    pygame.draw.rect(surf, WHITE,  rect, 2, border_radius=8)
    lbl = FONT.render(text, True, fg)
    surf.blit(lbl, lbl.get_rect(center=rect.center))


def overlay(surf, alpha=170):
    o = pygame.Surface((W, H), SRCALPHA)
    o.fill((0, 0, 0, alpha))
    surf.blit(o, (0, 0))


def center_text(surf, text, y, font=None, color=WHITE):
    font = font or FONT
    lbl = font.render(text, True, color)
    surf.blit(lbl, (W // 2 - lbl.get_width() // 2, y))


def draw_hud(surf, state: GameState):
    pygame.draw.rect(surf, DK_GRAY, (0, 0, W, HUD_H))
    surf.blit(FONT.render(f"Score: {state.score}", True, WHITE), (20, 8))
    surf.blit(FONT.render(f"Level: {state.level}", True, YELLOW), (20, 32))
    pb_lbl = SMALL_FONT.render(f"Best: {state.personal_best}", True, GRAY)
    surf.blit(pb_lbl, (W // 2 - pb_lbl.get_width() // 2, HUD_H // 2 - 8))
    if state.active_effect:
        kind = state.active_effect["kind"]
        colours = {"speed": PURPLE, "slow": CYAN, "shield": ORANGE}
        eff_col = colours.get(kind, WHITE)
        eff_lbl = SMALL_FONT.render(f"[{kind.upper()}]", True, eff_col)
        surf.blit(eff_lbl, (W - eff_lbl.get_width() - 10, 8))
    if state.shield_active:
        surf.blit(SMALL_FONT.render("🛡 SHIELD", True, ORANGE), (W - 100, 30))


def render_game(surf, state: GameState):
    surf.fill(BG)
    settings = state.settings

    if settings.get("grid_overlay", True):
        for r in range(ROWS):
            for c in range(COLS):
                if (c + r) % 2 == 0:
                    pygame.draw.rect(surf, (25, 25, 25),
                                     (c * CELL, r * CELL + HUD_H, CELL, CELL))

    for (c, r) in state.border_walls:
        draw_cell(surf, c, r, WALL_C, radius=0)

    for (c, r) in state.obstacles:
        draw_cell(surf, c, r, OBS_C, radius=2)

    for food in state.foods:
        fx, fy = grid_to_px(*food.pos)
        cx, cy = fx + CELL // 2, fy + CELL // 2
        if food.KIND == "poison":
            pygame.draw.circle(surf, POISON, (cx, cy), CELL // 2 - 2)
            pygame.draw.circle(surf, WHITE, (cx, cy), 4, 2)
        else:
            col = YELLOW if food.points > 10 else RED
            pygame.draw.circle(surf, col, (cx, cy), CELL // 2 - 2)
            if food.lifetime_ms:
                elapsed = pygame.time.get_ticks() - food.spawn_tick
                frac = max(0, 1 - elapsed / food.lifetime_ms)
                alpha_surf = pygame.Surface((CELL, CELL), SRCALPHA)
                alpha_surf.fill((255, 255, 0, int(frac * 200)))
                surf.blit(alpha_surf, (fx, fy))

    if state.powerup:
        px, py = grid_to_px(*state.powerup.pos)
        cx, cy = px + CELL // 2, py + CELL // 2
        pu_colours = {"speed": PURPLE, "slow": CYAN, "shield": ORANGE}
        pygame.draw.rect(surf, pu_colours[state.powerup.kind],
                         (px + 2, py + 2, CELL - 4, CELL - 4), border_radius=5)
        letter = {"speed": "S", "slow": "W", "shield": "🛡"}[state.powerup.kind]
        lbl = SMALL_FONT.render(letter, True, WHITE)
        surf.blit(lbl, lbl.get_rect(center=(cx, cy)))

    snake_head_col = tuple(settings.get("snake_color", [50, 200, 50]))
    snake_body_col = tuple(min(255, c + 40) for c in snake_head_col)
    for i, (c, r) in enumerate(state.snake):
        color = snake_head_col if i == 0 else snake_body_col
        draw_cell(surf, c, r, color)
        if i == 0:
            ex, ey = grid_to_px(c, r)
            pygame.draw.circle(surf, WHITE, (ex + 6,  ey + 6),  3)
            pygame.draw.circle(surf, WHITE, (ex + 14, ey + 6),  3)
            pygame.draw.circle(surf, BLACK, (ex + 7,  ey + 7),  2)
            pygame.draw.circle(surf, BLACK, (ex + 15, ey + 7),  2)

    draw_hud(surf, state)

    now = pygame.time.get_ticks()
    if state.level_up_flash and now < state.level_up_flash:
        center_text(surf, f"  LEVEL {state.level}! ", H // 2 - 24, BIG_FONT, YELLOW)
        center_text(surf, "Speed increased!", H // 2 + 30, FONT, WHITE)


def screen_main_menu(settings, player_state):
    """Returns (action, username, player_id, personal_best)
       action ∈ {"play", "leaderboard", "settings", "quit"}
    """
    username    = player_state.get("username", "")
    input_active = True
    db_ok        = player_state.get("db_ok", False)

    btn_play = pygame.Rect(W // 2 - 110, 290, 220, 48)
    btn_lb   = pygame.Rect(W // 2 - 110, 350, 220, 48)
    btn_set  = pygame.Rect(W // 2 - 110, 410, 220, 48)
    btn_quit = pygame.Rect(W // 2 - 110, 470, 220, 48)

    while True:
        mx, my = pygame.mouse.get_pos()
        screen.fill(BG)
        center_text(screen, "🐍  SNAKE", 60, BIG_FONT, YELLOW)
        center_text(screen, "Enter username:", 160, FONT, GRAY)

        box_rect = pygame.Rect(W // 2 - 130, 190, 260, 44)
        pygame.draw.rect(screen, (40, 40, 40), box_rect, border_radius=6)
        pygame.draw.rect(screen, YELLOW if input_active else GRAY,
                         box_rect, 2, border_radius=6)
        uname_lbl = FONT.render(username + ("|" if input_active else ""), True, WHITE)
        screen.blit(uname_lbl, (box_rect.x + 10, box_rect.y + 10))

        if not db_ok:
            center_text(screen, "⚠ DB offline — scores won't be saved",
                        245, SMALL_FONT, RED)

        for rect, label in [(btn_play, "▶  Play"),
                             (btn_lb,   "🏆 Leaderboard"),
                             (btn_set,  "⚙  Settings"),
                             (btn_quit, "✕  Quit")]:
            draw_button(screen, rect, label, hover=rect.collidepoint(mx, my))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == QUIT:
                return "quit", username, None, 0
            if event.type == MOUSEBUTTONDOWN:
                input_active = box_rect.collidepoint(mx, my)
                if btn_play.collidepoint(mx, my):
                    if not username:
                        username = "Player"
                    pid, pb = _resolve_player(username, db_ok)
                    return "play", username, pid, pb
                if btn_lb.collidepoint(mx, my):
                    return "leaderboard", username, None, 0
                if btn_set.collidepoint(mx, my):
                    return "settings", username, None, 0
                if btn_quit.collidepoint(mx, my):
                    return "quit", username, None, 0
            if event.type == KEYDOWN and input_active:
                if event.key == K_BACKSPACE:
                    username = username[:-1]
                elif event.key == K_RETURN:
                    input_active = False
                elif len(username) < 20 and event.unicode.isprintable():
                    username += event.unicode


def _resolve_player(username, db_ok):
    if not db_ok:
        return None, 0
    pid = db.get_or_create_player(username)
    pb  = db.get_personal_best(pid) if pid else 0
    return pid, pb


def screen_game_over(state: GameState):
    """Returns "retry" or "menu"."""
    overlay(screen, 160)
    center_text(screen, "GAME OVER", H // 2 - 120, BIG_FONT, RED)
    center_text(screen, f"Score: {state.score}   Level: {state.level}",
                H // 2 - 50, FONT, WHITE)
    center_text(screen, f"Personal Best: {state.personal_best}",
                H // 2 - 10, FONT, YELLOW)

    btn_retry = pygame.Rect(W // 2 - 130, H // 2 + 50, 120, 44)
    btn_menu  = pygame.Rect(W // 2 + 10,  H // 2 + 50, 120, 44)

    while True:
        mx, my = pygame.mouse.get_pos()
        draw_button(screen, btn_retry, "Retry",     hover=btn_retry.collidepoint(mx, my))
        draw_button(screen, btn_menu,  "Main Menu", hover=btn_menu.collidepoint(mx, my))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_r:
                    return "retry"
                if event.key == K_ESCAPE:
                    return "menu"
            if event.type == MOUSEBUTTONDOWN:
                if btn_retry.collidepoint(mx, my):
                    return "retry"
                if btn_menu.collidepoint(mx, my):
                    return "menu"


def screen_leaderboard():
    rows = db.get_top10()
    btn_back = pygame.Rect(W // 2 - 80, H - 65, 160, 44)

    while True:
        mx, my = pygame.mouse.get_pos()
        screen.fill(BG)
        center_text(screen, "🏆 Top 10 Leaderboard", 20, BIG_FONT, YELLOW)

        if not rows:
            center_text(screen, "No data (DB offline or empty)", 200, FONT, GRAY)
        else:
            headers = ["#", "Username", "Score", "Level", "Date"]
            col_xs  = [30, 80, 280, 380, 440]
            header_y = 95
            for i, h in enumerate(headers):
                lbl = SMALL_FONT.render(h, True, YELLOW)
                screen.blit(lbl, (col_xs[i], header_y))
            pygame.draw.line(screen, GRAY, (20, 115), (W - 20, 115), 1)

            for rank, uname, score, level, ts in rows:
                y = 122 + (rank - 1) * 34
                row_color = YELLOW if rank == 1 else WHITE
                vals = [str(rank), uname[:14], str(score), str(level),
                        ts.strftime("%d/%m/%y") if isinstance(ts, datetime.datetime) else str(ts)]
                for i, v in enumerate(vals):
                    screen.blit(SMALL_FONT.render(v, True, row_color), (col_xs[i], y))

        draw_button(screen, btn_back, "← Back", hover=btn_back.collidepoint(mx, my))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if event.type == KEYDOWN and event.key in (K_ESCAPE, K_BACKSPACE):
                return
            if event.type == MOUSEBUTTONDOWN and btn_back.collidepoint(mx, my):
                return


def screen_settings(settings):
    """Mutates settings dict in place and saves to disk. Returns when done."""
    snake_col   = list(settings.get("snake_color", [50, 200, 50]))
    grid_on     = settings.get("grid_overlay", True)
    sound_on    = settings.get("sound", False)

    PRESET_COLORS = [
        ([50, 200, 50],  "Green"),
        ([50, 150, 255], "Blue"),
        ([255, 100, 50], "Orange"),
        ([220, 50, 220], "Purple"),
        ([255, 220, 0],  "Yellow"),
    ]

    btn_save = pygame.Rect(W // 2 - 80, H - 65, 160, 44)
    color_rects = [
        pygame.Rect(60 + i * 110, 260, 90, 36)
        for i in range(len(PRESET_COLORS))
    ]
    btn_grid  = pygame.Rect(W // 2 - 80, 330, 160, 40)
    btn_sound = pygame.Rect(W // 2 - 80, 385, 160, 40)

    while True:
        mx, my = pygame.mouse.get_pos()
        screen.fill(BG)
        center_text(screen, "⚙  Settings", 30, BIG_FONT, YELLOW)

        center_text(screen, "Snake Color:", 210, FONT, WHITE)
        for i, (col, name) in enumerate(PRESET_COLORS):
            selected = (col == snake_col)
            pygame.draw.rect(screen, tuple(col), color_rects[i], border_radius=6)
            if selected:
                pygame.draw.rect(screen, WHITE, color_rects[i], 3, border_radius=6)
            lbl = SMALL_FONT.render(name, True, WHITE)
            screen.blit(lbl, lbl.get_rect(centerx=color_rects[i].centerx,
                                           top=color_rects[i].bottom + 4))

        draw_button(screen, btn_grid,
                    f"Grid Overlay: {'ON' if grid_on else 'OFF'}",
                    bg=(30, 100, 30) if grid_on else (80, 40, 40),
                    hover=btn_grid.collidepoint(mx, my))
        draw_button(screen, btn_sound,
                    f"Sound: {'ON' if sound_on else 'OFF'}",
                    bg=(30, 100, 30) if sound_on else (80, 40, 40),
                    hover=btn_sound.collidepoint(mx, my))

        draw_button(screen, btn_save, "Save & Back", hover=btn_save.collidepoint(mx, my))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                for i, rect in enumerate(color_rects):
                    if rect.collidepoint(mx, my):
                        snake_col = list(PRESET_COLORS[i][0])
                if btn_grid.collidepoint(mx, my):
                    grid_on = not grid_on
                if btn_sound.collidepoint(mx, my):
                    sound_on = not sound_on
                if btn_save.collidepoint(mx, my):
                    settings["snake_color"]  = snake_col
                    settings["grid_overlay"] = grid_on
                    settings["sound"]        = sound_on
                    save_settings(settings)
                    return
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                return


def run_game(settings, player_id, personal_best):
    state = GameState(settings, player_id=player_id, personal_best=personal_best)

    while True:
        clock_.tick(state.fps)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_UP:    state.set_direction(UP)
                if event.key == K_DOWN:  state.set_direction(DOWN)
                if event.key == K_LEFT:  state.set_direction(LEFT)
                if event.key == K_RIGHT: state.set_direction(RIGHT)

        alive = state.tick()
        render_game(screen, state)
        pygame.display.flip()

        if not alive:
            if state.score > state.personal_best:
                state.personal_best = state.score
            if player_id:
                db.save_session(player_id, state.score, state.level)
            return state


def main():
    settings = load_settings()
    db_ok    = db.init_db()
    player_state = {"username": "", "db_ok": db_ok}

    while True:
        action, username, player_id, personal_best = screen_main_menu(
            settings, player_state
        )
        player_state["username"] = username

        if action == "quit":
            pygame.quit(); sys.exit()

        elif action == "leaderboard":
            screen_leaderboard()

        elif action == "settings":
            screen_settings(settings)

        elif action == "play":
            while True:
                state = run_game(settings, player_id, personal_best)
                personal_best = state.personal_best
                choice = screen_game_over(state)
                if choice == "retry":
                    continue
                break  


if __name__ == "__main__":
    main()