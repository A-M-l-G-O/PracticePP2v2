import pygame
import random

W, H = 400, 600
FPS  = 60

WHITE  = (255, 255, 255)
BLACK  = (0,   0,   0)
RED    = (220, 50,  50)
BLUE   = (50,  50,  220)
GRAY   = (100, 100, 100)
DKGRAY = (60,  60,  60)
YELLOW = (255, 220, 0)
GREEN  = (50,  200, 50)
ORANGE = (255, 140, 0)
PURPLE = (180, 0,   220)
CYAN   = (0,   220, 220)

ROAD_COLOR  = (80,  80,  80)
LINE_COLOR  = (240, 240, 240)
ROAD_LEFT   = 80
ROAD_RIGHT  = 320
ROAD_W      = ROAD_RIGHT - ROAD_LEFT

LANE_W       = ROAD_W // 3
LANE_CENTERS = [
    ROAD_LEFT + LANE_W // 2,
    ROAD_LEFT + LANE_W + LANE_W // 2,
    ROAD_LEFT + LANE_W * 2 + LANE_W // 2,
]

CAR_COLORS = {
    "Blue":   (50,  50,  220),
    "Red":    (220, 50,  50),
    "Green":  (50,  180, 50),
    "Purple": (160, 0,   200),
    "Orange": (240, 120, 0),
}


def _wheels(surf, r):
    """Draw four wheels on a car rect."""
    for wx, wy in [(r.x - 4, r.y + 8), (r.right - 8, r.y + 8),
                   (r.x - 4, r.bottom - 22), (r.right - 8, r.bottom - 22)]:
        pygame.draw.rect(surf, BLACK, (wx, wy, 12, 14), border_radius=3)


class PlayerCar:
    CW, CH = 40, 70

    def __init__(self, color=BLUE):
        self.color = color
        self.rect  = pygame.Rect(W // 2 - self.CW // 2,
                                 H - self.CH - 20, self.CW, self.CH)
        self.base_speed    = 5
        self.nitro_timer   = 0
        self.shield_active = False
        self.shield_hit    = False

    @property
    def speed(self):
        return self.base_speed * 2 if self.nitro_timer > 0 else self.base_speed

    def update(self, keys):
        if keys[pygame.K_LEFT] and self.rect.left > ROAD_LEFT + 5:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < ROAD_RIGHT - 5:
            self.rect.x += self.speed
        if self.nitro_timer > 0:
            self.nitro_timer -= 1

    def draw(self, surf):
        r = self.rect
        if self.shield_active:
            pygame.draw.rect(surf, CYAN,
                             r.inflate(10, 10), border_radius=10, width=3)
        pygame.draw.rect(surf, self.color, r, border_radius=6)
        pygame.draw.rect(surf, (180, 220, 255),
                         (r.x + 6, r.y + 10, r.w - 12, 18), border_radius=3)
        if self.nitro_timer > 0:
            flame = [(r.centerx - 8, r.bottom),
                     (r.centerx,     r.bottom + 18),
                     (r.centerx + 8, r.bottom)]
            pygame.draw.polygon(surf, ORANGE, flame)
        _wheels(surf, r)


class EnemyCar:
    CW, CH = 40, 70
    COLORS = [(220, 50, 50), (200, 100, 0), (150, 0, 200), (0, 180, 100)]

    def __init__(self, speed, player_rect=None):
        self.color = random.choice(self.COLORS)
        x = _safe_x(self.CW, player_rect, top_spawn=True)
        self.rect  = pygame.Rect(x, -self.CH, self.CW, self.CH)
        self.speed = speed

    def update(self):
        self.rect.y += self.speed

    def draw(self, surf):
        r = self.rect
        pygame.draw.rect(surf, self.color, r, border_radius=6)
        pygame.draw.rect(surf, (255, 220, 150),
                         (r.x + 6, r.y + 10, r.w - 12, 18), border_radius=3)
        _wheels(surf, r)

    def off_screen(self):
        return self.rect.top > H


class OilSpill:
    W, H_OBJ = 50, 25
    SLOW_FRAMES = 120

    def __init__(self, speed, player_rect=None):
        x = _safe_x(self.W, player_rect, top_spawn=True)
        self.rect  = pygame.Rect(x, -self.H_OBJ, self.W, self.H_OBJ)
        self.speed = speed
        self.active = True

    def update(self):
        self.rect.y += self.speed

    def draw(self, surf):
        if not self.active:
            return
        pygame.draw.ellipse(surf, (30, 30, 60), self.rect)
        for i, c in enumerate([(200, 0, 200, 80), (0, 200, 200, 80)]):
            pygame.draw.ellipse(surf, c[:3],
                                self.rect.inflate(-i * 10, -i * 4), 2)

    def off_screen(self):
        return self.rect.top > H


class Pothole:
    SIZE = 30

    def __init__(self, speed, player_rect=None):
        x = _safe_x(self.SIZE, player_rect, top_spawn=True)
        self.rect  = pygame.Rect(x, -self.SIZE, self.SIZE, self.SIZE)
        self.speed = speed

    def update(self):
        self.rect.y += self.speed

    def draw(self, surf):
        pygame.draw.ellipse(surf, (40, 30, 20), self.rect)
        pygame.draw.ellipse(surf, (20, 15, 10), self.rect, 2)

    def off_screen(self):
        return self.rect.top > H


class SpeedBump:
    def __init__(self, speed, player_rect=None):
        self.rect  = pygame.Rect(ROAD_LEFT, -12, ROAD_W, 12)
        self.speed = speed

    def update(self):
        self.rect.y += self.speed

    def draw(self, surf):
        pygame.draw.rect(surf, YELLOW, self.rect)
        for x in range(self.rect.left, self.rect.right, 20):
            pygame.draw.rect(surf, BLACK, (x, self.rect.y, 10, self.rect.h))

    def off_screen(self):
        return self.rect.top > H


class NitroStrip:
    def __init__(self, speed, player_rect=None):
        self.rect  = pygame.Rect(ROAD_LEFT, -12, ROAD_W, 12)
        self.speed = speed

    def update(self):
        self.rect.y += self.speed

    def draw(self, surf):
        pygame.draw.rect(surf, (0, 240, 80), self.rect)
        for x in range(self.rect.left + 10, self.rect.right, 40):
            pts = [(x, self.rect.bottom), (x + 10, self.rect.top),
                   (x + 20, self.rect.bottom)]
            pygame.draw.polygon(surf, WHITE, pts)

    def off_screen(self):
        return self.rect.top > H


class Coin:
    R = 12
    VALUE_TABLE = [(10, 5), (25, 3), (50, 1)]

    def __init__(self, speed, player_rect=None):
        x = _safe_x(self.R * 2, player_rect, top_spawn=True)
        self.rect  = pygame.Rect(x, -self.R * 2, self.R * 2, self.R * 2)
        self.speed = speed
        self.angle = 0
        values, weights = zip(*self.VALUE_TABLE)
        self.value = random.choices(values, weights=weights)[0]
        self.color = {10: YELLOW, 25: (192, 192, 192), 50: (255, 215, 0)}[self.value]

    def update(self):
        self.rect.y += self.speed
        self.angle = (self.angle + 4) % 360

    def draw(self, surf):
        cx, cy = self.rect.centerx, self.rect.centery
        scale = abs(pygame.math.Vector2(1, 0).rotate(self.angle).x)
        hw = max(2, int(self.R * scale))
        pygame.draw.ellipse(surf, self.color,
                            (cx - hw, cy - self.R, hw * 2, self.R * 2))
        pygame.draw.ellipse(surf, (150, 120, 0),
                            (cx - hw, cy - self.R, hw * 2, self.R * 2), 2)
        if scale > 0.5:
            f = pygame.font.SysFont("Arial", 9, bold=True)
            t = f.render(str(self.value), True, BLACK)
            surf.blit(t, (cx - t.get_width() // 2, cy - t.get_height() // 2))

    def off_screen(self):
        return self.rect.top > H


class PowerUp:
    SIZE = 28
    TIMEOUT = FPS * 7

    KINDS = {
        "Nitro":  {"color": ORANGE,          "label": "N"},
        "Shield": {"color": CYAN,            "label": "S"},
        "Repair": {"color": (100, 220, 100), "label": "R"},
    }

    def __init__(self, speed, player_rect=None):
        self.kind  = random.choice(list(self.KINDS.keys()))
        x = _safe_x(self.SIZE, player_rect, top_spawn=True)
        self.rect  = pygame.Rect(x, -self.SIZE, self.SIZE, self.SIZE)
        self.speed = speed
        self.life  = self.TIMEOUT
        self.font  = pygame.font.SysFont("Arial", 14, bold=True)

    def update(self):
        self.rect.y += self.speed
        self.life  -= 1

    def draw(self, surf):
        info = self.KINDS[self.kind]
        pulse = abs(pygame.time.get_ticks() % 1000 - 500) / 500
        r_size = int(4 + pulse * 6)
        pygame.draw.rect(surf, info["color"],
                         self.rect.inflate(r_size, r_size), border_radius=8, width=2)
        pygame.draw.rect(surf, info["color"], self.rect, border_radius=6)
        t = self.font.render(info["label"], True, BLACK)
        surf.blit(t, (self.rect.centerx - t.get_width() // 2,
                      self.rect.centery - t.get_height() // 2))

    def off_screen(self):
        return self.rect.top > H or self.life <= 0


def _safe_x(obj_w: int, player_rect, top_spawn: bool = True) -> int:
    for _ in range(10):
        x = random.randint(ROAD_LEFT + 5, ROAD_RIGHT - obj_w - 5)
        if player_rect is None:
            return x
        if top_spawn:
            return x
        if not pygame.Rect(x, 0, obj_w, 40).colliderect(player_rect):
            return x
    return ROAD_LEFT + 5