import pygame
import sys
import random

from constants    import *
from persistence  import load_settings, save_score, DIFFICULTY_PARAMS
from racer        import PlayerCar, EnemyCar, Coin, OilSpill, Pothole, SpeedBump, NitroStrip, PowerUp
from ui           import (draw_road, draw_hud, game_over_screen,
                          leaderboard_screen, main_menu, settings_screen,
                          username_screen)

pygame.init()
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Racer  –  TSIS 3")
clock  = pygame.time.Clock()


NITRO_DURATION  = FPS * 4   # 4 s
SHIELD_INFINITE = -1        # no timer — lasts until hit


def apply_powerup(kind, player, active_pu_ref):
    """Apply collected power-up to player; returns (active_name, timer_frames)."""
    if kind == "Nitro":
        player.nitro_timer = NITRO_DURATION
        return "Nitro", NITRO_DURATION
    elif kind == "Shield":
        player.shield_active = True
        return "Shield", SHIELD_INFINITE
    elif kind == "Repair":
        # Repair: instant — just award bonus score (game loop handles it)
        return "Repair", FPS * 1   # show for 1 s then clear
    return None, 0


def run_game(username: str, settings: dict) -> str:
    """Run one game session. Returns 'retry' or 'menu'."""

    diff       = settings.get("difficulty", "Normal")
    params     = DIFFICULTY_PARAMS[diff]
    car_color  = CAR_COLORS[settings.get("car_color", "Blue")]

    player        = PlayerCar(color=car_color)
    enemies       = []
    coins         = []
    obstacles     = []   
    powerups      = []

    score         = 0
    coin_count    = 0
    distance      = 0     
    road_offset   = 0

    base_speed    = params["base_speed"]
    enemy_interval= params["enemy_interval"]
    coin_interval = params["coin_interval"]
    obs_interval  = 200
    pu_interval   = 400

    enemy_timer = coin_timer = obs_timer = pu_timer_spawn = 0

    active_pu_name  = None
    active_pu_timer = 0

    slow_timer = 0

    game_active = True

    while True:
        clock.tick(FPS)
        keys = pygame.event.get()

        for event in keys:
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

        pressed = pygame.key.get_pressed()

        if not game_active:
            draw_road(screen, road_offset)
            for e in enemies: e.draw(screen)
            for c in coins:   c.draw(screen)
            for o in obstacles: o.draw(screen)
            for p in powerups:  p.draw(screen)
            player.draw(screen)
            draw_hud(screen, score, coin_count, distance,
                     active_pu_name, active_pu_timer, player.shield_active)
            pygame.display.update()

            save_score(username, score, distance, coin_count)
            action = game_over_screen(screen, clock, score, distance, coin_count)
            return action

        speed = base_speed + score // 300
        if slow_timer > 0:
            speed = max(1, speed // 2)
            slow_timer -= 1

        road_offset += speed
        distance = int(road_offset / 10)

        player.update(pressed)

        if active_pu_timer > 0:
            active_pu_timer -= 1
            if active_pu_timer == 0:
                active_pu_name = None
        if player.nitro_timer == 0 and active_pu_name == "Nitro":
            active_pu_name = None

        enemy_timer += 1
        eff_interval = max(25, enemy_interval - score // 150)
        if enemy_timer >= eff_interval:
            enemies.append(EnemyCar(speed, player.rect))
            enemy_timer = 0

        coin_timer += 1
        if coin_timer >= coin_interval:
            coins.append(Coin(speed, player.rect))
            coin_timer = 0

        obs_timer += 1
        obs_eff = max(80, obs_interval - score // 200)
        if obs_timer >= obs_eff:
            kind = random.choices(
                [OilSpill, Pothole, SpeedBump, NitroStrip],
                weights=[4, 3, 2, 1]
            )[0]
            obstacles.append(kind(speed, player.rect))
            obs_timer = 0

        pu_timer_spawn += 1
        if pu_timer_spawn >= pu_interval:
            powerups.append(PowerUp(speed, player.rect))
            pu_timer_spawn = 0

        for e in enemies[:]:
            e.update()
            if e.off_screen():
                enemies.remove(e)
                score += 10
            elif e.rect.colliderect(player.rect):
                if player.shield_active:
                    player.shield_active = False
                    active_pu_name  = None
                    active_pu_timer = 0
                    enemies.remove(e)
                else:
                    game_active = False

        for c in coins[:]:
            c.update()
            if c.off_screen():
                coins.remove(c)
            elif c.rect.colliderect(player.rect):
                coins.remove(c)
                coin_count += 1
                score      += c.value

        for o in obstacles[:]:
            o.update()
            if o.off_screen():
                obstacles.remove(o)
            elif o.rect.colliderect(player.rect):
                if isinstance(o, NitroStrip):
                    player.nitro_timer = FPS * 2
                    active_pu_name  = "Nitro"
                    active_pu_timer = FPS * 2
                    obstacles.remove(o)
                elif isinstance(o, SpeedBump):
                    slow_timer = FPS * 2
                    obstacles.remove(o)
                elif isinstance(o, OilSpill):
                    slow_timer = FPS * 2
                    obstacles.remove(o)
                elif isinstance(o, Pothole):
                    if player.shield_active:
                        player.shield_active = False
                        active_pu_name = None
                        obstacles.remove(o)
                    else:
                        game_active = False

        for p in powerups[:]:
            p.update()
            if p.off_screen():
                powerups.remove(p)
            elif p.rect.colliderect(player.rect):
                kind = p.kind
                powerups.remove(p)
                if kind == "Repair":
                    if obstacles:
                        obstacles.pop(0)
                    score += 100
                    active_pu_name  = "Repair"
                    active_pu_timer = FPS
                else:
                    active_pu_name, active_pu_timer = apply_powerup(kind, player, None)

        score += 1

        draw_road(screen, road_offset)
        for o in obstacles: o.draw(screen)
        for e in enemies:   e.draw(screen)
        for c in coins:     c.draw(screen)
        for p in powerups:  p.draw(screen)
        player.draw(screen)
        draw_hud(screen, score, coin_count, distance,
                 active_pu_name, active_pu_timer, player.shield_active)
        pygame.display.update()


def main():
    settings = load_settings()
    username = username_screen(screen, clock)

    while True:
        action = main_menu(screen, clock)

        if action == "leaderboard":
            leaderboard_screen(screen, clock)

        elif action == "settings":
            settings = settings_screen(screen, clock)

        elif action == "play":
            while True:
                result = run_game(username, settings)
                if result == "retry":
                    continue
                break  


if __name__ == "__main__":
    main()
