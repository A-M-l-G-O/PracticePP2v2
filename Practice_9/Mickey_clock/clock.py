import pygame
import datetime
import math
import os


class MickeyClock:
    def __init__(self, screen, w, h):
        self.screen = screen
        self.w = w
        self.h = h
        self.cx = w // 2
        self.cy = h // 2

        hand_path = os.path.join(os.path.dirname(__file__), "images", "mickey_hand.png")
        if os.path.exists(hand_path):
            orig = pygame.image.load(hand_path).convert_alpha()
            self.hand = pygame.transform.scale(orig, (40, 120))
        else:
            self.hand = self._make_hand()

        self.font_big = pygame.font.SysFont("monospace", 64, bold=True)
        self.font_small = pygame.font.SysFont("monospace", 28)

    def _make_hand(self):
        surf = pygame.Surface((40, 120), pygame.SRCALPHA)
        pygame.draw.rect(surf, (30, 30, 30), (14, 20, 12, 90), border_radius=6)
        pygame.draw.circle(surf, (50, 50, 50), (20, 15), 15)
        return surf

    def _rotate_hand(self, angle_deg, length=120):
        rotated = pygame.transform.rotate(self.hand, -angle_deg)
        rect = rotated.get_rect()

        rad = math.radians(angle_deg - 90)
        offset_x = math.cos(rad) * (length / 2)
        offset_y = math.sin(rad) * (length / 2)

        rect.center = (self.cx + int(offset_x), self.cy + int(offset_y))
        return rotated, rect

    def draw(self):
        now = datetime.datetime.now()
        mins = now.minute
        secs = now.second

        min_angle = mins * 6 + secs * 0.1
        sec_angle = secs * 6

        self.screen.fill((255, 248, 220))

        pygame.draw.circle(self.screen, (200, 180, 140), (self.cx, self.cy), 180, 4)
        pygame.draw.circle(self.screen, (220, 200, 160), (self.cx, self.cy), 176)

        for i in range(60):
            a = math.radians(i * 6 - 90)
            r_out = 170
            r_in = 160 if i % 5 else 148
            x1 = self.cx + int(math.cos(a) * r_in)
            y1 = self.cy + int(math.sin(a) * r_in)
            x2 = self.cx + int(math.cos(a) * r_out)
            y2 = self.cy + int(math.sin(a) * r_out)
            w = 3 if i % 5 == 0 else 1
            pygame.draw.line(self.screen, (80, 60, 40), (x1, y1), (x2, y2), w)

        min_surf, min_rect = self._rotate_hand(min_angle, 100)
        sec_surf, sec_rect = self._rotate_hand(sec_angle, 120)

        self.screen.blit(min_surf, min_rect)
        self.screen.blit(sec_surf, sec_rect)

        pygame.draw.circle(self.screen, (30, 30, 30), (self.cx, self.cy), 8)

        time_str = f"{mins:02d}:{secs:02d}"
        t_surf = self.font_big.render(time_str, True, (60, 40, 20))
        self.screen.blit(t_surf, t_surf.get_rect(center=(self.cx, self.cy + 230)))

        label = self.font_small.render("Mickey's Clock  |  MM:SS", True, (120, 100, 70))
        self.screen.blit(label, label.get_rect(center=(self.cx, self.h - 30)))
