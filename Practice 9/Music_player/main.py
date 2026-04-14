import pygame
import sys
import os
from player import MusicPlayer

W, H = 600, 400
FPS = 30
MUSIC_DIR = os.path.join(os.path.dirname(__file__), "music")

BG = (18, 18, 28)
ACCENT = (255, 80, 120)
WHITE = (240, 240, 240)
GRAY = (130, 130, 150)
DARK = (35, 35, 50)


def draw_ui(screen, player, fonts):
    f_big, f_med, f_sm = fonts
    screen.fill(BG)

    pygame.draw.rect(screen, DARK, (40, 40, W - 80, H - 80), border_radius=20)

    title = f_big.render("♪  Music Player", True, ACCENT)
    screen.blit(title, title.get_rect(center=(W // 2, 90)))

    track = f_med.render(player.current_name(), True, WHITE)
    screen.blit(track, track.get_rect(center=(W // 2, 160)))

    status = "▶  Playing" if player.is_playing() else "⏹  Stopped"
    col = (80, 220, 120) if player.is_playing() else GRAY
    s_surf = f_sm.render(status, True, col)
    screen.blit(s_surf, s_surf.get_rect(center=(W // 2, 205)))

    elapsed = f_sm.render(f"Elapsed: {player.elapsed_str()}", True, GRAY)
    screen.blit(elapsed, elapsed.get_rect(center=(W // 2, 235)))

    idx_info = f_sm.render(
        f"Track {player.current_idx() + 1} / {player.track_count() or '—'}",
        True, GRAY
    )
    screen.blit(idx_info, idx_info.get_rect(center=(W // 2, 260)))

    controls = [
        ("P", "Play"),
        ("S", "Stop"),
        ("N", "Next"),
        ("B", "Back"),
        ("Q", "Quit"),
    ]
    gap = (W - 80) // len(controls)
    for i, (key, label) in enumerate(controls):
        x = 40 + gap * i + gap // 2
        y = 320
        pygame.draw.circle(screen, ACCENT, (x, y), 24)
        k_surf = f_med.render(key, True, BG)
        screen.blit(k_surf, k_surf.get_rect(center=(x, y)))
        l_surf = f_sm.render(label, True, GRAY)
        screen.blit(l_surf, l_surf.get_rect(center=(x, y + 36)))


def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Music Player")

    fonts = (
        pygame.font.SysFont("monospace", 30, bold=True),
        pygame.font.SysFont("monospace", 22, bold=True),
        pygame.font.SysFont("monospace", 16),
    )

    player = MusicPlayer(MUSIC_DIR)
    tick = pygame.time.Clock()

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_p:
                    player.play()
                elif e.key == pygame.K_s:
                    player.stop()
                elif e.key == pygame.K_n:
                    player.next()
                elif e.key == pygame.K_b:
                    player.prev()
                elif e.key in (pygame.K_q, pygame.K_ESCAPE):
                    pygame.quit()
                    sys.exit()

        draw_ui(screen, player, fonts)
        pygame.display.flip()
        tick.tick(FPS)


if __name__ == "__main__":
    main()
