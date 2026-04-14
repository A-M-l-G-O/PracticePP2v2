import pygame
import random
import sys
from pygame.locals import *

pygame.init()

W, H = 400, 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (220, 50,  50)
BLUE  = (50,  50, 220)
GRAY  = (100, 100, 100)
DKGRAY= (60,  60,  60)
YELLOW= (255, 220, 0)
GREEN = (50, 200, 50)
ROAD_COLOR = (80, 80, 80)
LINE_COLOR = (240, 240, 240)

screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Racer")
clock = pygame.time.Clock()
font  = pygame.font.SysFont("Arial", 22, bold=True)
big_font = pygame.font.SysFont("Arial", 48, bold=True)

ROAD_LEFT  = 80
ROAD_RIGHT = 320
ROAD_W     = ROAD_RIGHT - ROAD_LEFT  


class PlayerCar:
    W, H = 40, 70
    def __init__(self):
        self.x = W // 2 - self.W // 2
        self.y = H - self.H - 20
        self.speed = 5
        self.rect = pygame.Rect(self.x, self.y, self.W, self.H)

    def move(self, keys):
        if keys[K_LEFT]  and self.rect.left  > ROAD_LEFT + 5:
            self.rect.x -= self.speed
        if keys[K_RIGHT] and self.rect.right < ROAD_RIGHT - 5:
            self.rect.x += self.speed

    def draw(self, surf):
        r = self.rect # Body
        pygame.draw.rect(surf, BLUE, r, border_radius=6) # Windshield
        pygame.draw.rect(surf, (180, 220, 255),
                         (r.x+6, r.y+10, r.w-12, 18), border_radius=3) # Wheels
        for wx, wy in [(r.x-4, r.y+8), (r.right-8, r.y+8),
                       (r.x-4, r.bottom-22), (r.right-8, r.bottom-22)]:
            pygame.draw.rect(surf, BLACK, (wx, wy, 12, 14), border_radius=3)


class EnemyCar:
    W, H = 40, 70
    COLORS = [(220,50,50),(200,100,0),(150,0,200),(0,180,100)]

    def __init__(self, speed):
        self.color = random.choice(self.COLORS)
        self.rect  = pygame.Rect(
            random.randint(ROAD_LEFT + 5, ROAD_RIGHT - self.W - 5),
            -self.H, self.W, self.H)
        self.speed = speed

    def update(self):
        self.rect.y += self.speed

    def draw(self, surf):
        r = self.rect
        pygame.draw.rect(surf, self.color, r, border_radius=6)
        pygame.draw.rect(surf, (255,220,150),
                         (r.x+6, r.y+10, r.w-12, 18), border_radius=3)
        for wx, wy in [(r.x-4, r.y+8), (r.right-8, r.y+8),
                       (r.x-4, r.bottom-22), (r.right-8, r.bottom-22)]:
            pygame.draw.rect(surf, BLACK, (wx, wy, 12, 14), border_radius=3)

    def off_screen(self):
        return self.rect.top > H


class Coin:

    R = 12

    def __init__(self, speed):
        self.rect = pygame.Rect(
            random.randint(ROAD_LEFT + self.R + 5, ROAD_RIGHT - self.R - 5),
            -self.R * 2, self.R * 2, self.R * 2)
        self.speed = speed
        self.angle = 0 

    def update(self):
        self.rect.y += self.speed
        self.angle  = (self.angle + 4) % 360

    def draw(self, surf):
        cx, cy = self.rect.centerx, self.rect.centery
        scale = abs(pygame.math.Vector2(1, 0).rotate(self.angle).x)
        hw = max(2, int(self.R * scale))
        pygame.draw.ellipse(surf, YELLOW,
                            (cx - hw, cy - self.R, hw * 2, self.R * 2))
        pygame.draw.ellipse(surf, (200, 160, 0),
                            (cx - hw, cy - self.R, hw * 2, self.R * 2), 2)

    def off_screen(self):
        return self.rect.top > H



def draw_road(surf, offset):
    surf.fill(GREEN)
    pygame.draw.rect(surf, ROAD_COLOR, (ROAD_LEFT, 0, ROAD_W, H))
    dash_h = 40
    gap    = 20
    total  = dash_h + gap
    start  = (-offset % total) - total
    for y in range(int(start), H, total):
        pygame.draw.rect(surf, LINE_COLOR,
                         (W // 2 - 3, y, 6, dash_h))
    pygame.draw.line(surf, WHITE, (ROAD_LEFT,  0), (ROAD_LEFT,  H), 4)
    pygame.draw.line(surf, WHITE, (ROAD_RIGHT, 0), (ROAD_RIGHT, H), 4)



def draw_hud(surf, score, coins):
    s = font.render(f"Score: {score}", True, WHITE)
    surf.blit(s, (ROAD_LEFT + 8, 10))
    pygame.draw.circle(surf, YELLOW, (ROAD_RIGHT - 50, 20), 10)
    c = font.render(f"x {coins}", True, WHITE)
    surf.blit(c, (ROAD_RIGHT - 35, 10))


def game_over_screen(surf, score, coins):
    overlay = pygame.Surface((W, H), SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    surf.blit(overlay, (0, 0))
    msg1 = big_font.render("GAME OVER", True, RED)
    msg2 = font.render(f"Score: {score}   Coins: {coins}", True, WHITE)
    msg3 = font.render("Press R to restart or Q to quit", True, GRAY)
    surf.blit(msg1, (W//2 - msg1.get_width()//2, H//2 - 80))
    surf.blit(msg2, (W//2 - msg2.get_width()//2, H//2))
    surf.blit(msg3, (W//2 - msg3.get_width()//2, H//2 + 50))
    pygame.display.update()



def main():
    player        = PlayerCar()
    enemies       = []
    coins         = []
    score         = 0
    coin_count    = 0
    enemy_timer   = 0
    coin_timer    = 0
    enemy_interval= 90   
    coin_interval = 150  
    road_offset   = 0
    base_speed    = 4
    game_active   = True

    while True:
        clock.tick(FPS)
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if not game_active and event.type == KEYDOWN:
                if event.key == K_r:
                    main(); return  
                if event.key == K_q:
                    pygame.quit(); sys.exit()

        if not game_active:
            game_over_screen(screen, score, coin_count)
            continue

        speed = base_speed + score // 200

        road_offset += speed
        player.move(keys)

        enemy_timer += 1
        if enemy_timer >= max(30, enemy_interval - score // 100):
            enemies.append(EnemyCar(speed))
            enemy_timer = 0

        coin_timer += 1
        if coin_timer >= coin_interval:
            coins.append(Coin(speed))
            coin_timer = 0

        for e in enemies[:]:
            e.update()
            if e.off_screen():
                enemies.remove(e)
                score += 10
            elif e.rect.colliderect(player.rect):
                game_active = False

        for c in coins[:]:
            c.update()
            if c.off_screen():
                coins.remove(c)
            elif c.rect.colliderect(player.rect):
                coins.remove(c)
                coin_count += 1
                score      += 50

        draw_road(screen, road_offset)
        for e in enemies: e.draw(screen)
        for c in coins:   c.draw(screen)
        player.draw(screen)
        draw_hud(screen, score, coin_count)
        pygame.display.update()


main()
