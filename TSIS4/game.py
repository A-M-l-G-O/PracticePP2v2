import random
import pygame

from config import (
    CELL, COLS, ROWS, HUD_H,
    UP, DOWN, LEFT, RIGHT,
    LEVELS, OBSTACLES_PER_LEVEL,
    POWERUP_FIELD_TIME, POWERUP_EFFECT_TIME,
)

def build_border_walls():
    w = set()
    for c in range(COLS):
        w.add((c, 0)); w.add((c, ROWS - 1))
    for r in range(ROWS):
        w.add((0, r)); w.add((COLS - 1, r))
    return w


def random_free_pos(snake_body, all_walls, extra_blocked=None):
    blocked = all_walls | set(snake_body)
    if extra_blocked:
        blocked |= extra_blocked
    interior = [
        (c, r) for c in range(1, COLS - 1) for r in range(1, ROWS - 1)
        if (c, r) not in blocked
    ]
    if not interior:
        return None
    return random.choice(interior)


class Food:
    """Normal food with a point weight. Optional disappear timer."""
    KIND = "normal"

    def __init__(self, pos, points=10, lifetime_ms=None):
        self.pos = pos
        self.points = points
        self.spawn_tick = pygame.time.get_ticks()
        self.lifetime_ms = lifetime_ms   

    def expired(self):
        if self.lifetime_ms is None:
            return False
        return pygame.time.get_ticks() - self.spawn_tick > self.lifetime_ms


class PoisonFood(Food):
    KIND = "poison"

    def __init__(self, pos):
        super().__init__(pos, points=0, lifetime_ms=10_000)


class PowerUp:
    def __init__(self, kind, pos):
        self.kind = kind       
        self.pos = pos
        self.spawn_tick = pygame.time.get_ticks()

    def field_expired(self):
        return pygame.time.get_ticks() - self.spawn_tick > POWERUP_FIELD_TIME


def build_obstacles(level, snake_body, border_walls, existing_obs):
    """Add OBSTACLES_PER_LEVEL new obstacle cells, avoiding the snake."""
    obs = set(existing_obs)
    attempts = 0
    target = len(obs) + OBSTACLES_PER_LEVEL
    while len(obs) < target and attempts < 1000:
        attempts += 1
        pos = (random.randint(2, COLS - 3), random.randint(2, ROWS - 3))
        if pos in border_walls or pos in obs:
            continue
        head = snake_body[0]
        if abs(pos[0] - head[0]) <= 2 and abs(pos[1] - head[1]) <= 2:
            continue
        obs.add(pos)
    return obs


class GameState:
    def __init__(self, settings, player_id=None, personal_best=0):
        self.settings       = settings
        self.player_id      = player_id
        self.personal_best  = personal_best

        self.border_walls   = build_border_walls()
        self.obstacles      = set()

        mid_c, mid_r        = COLS // 2, ROWS // 2
        self.snake          = [(mid_c - i, mid_r) for i in range(3)]
        self.direction      = RIGHT
        self.next_dir       = RIGHT

        self.score          = 0
        self.level          = 1
        self.food_in_level  = 0
        food_needed, fps    = LEVELS[0]
        self.food_needed    = food_needed
        self.fps            = fps

        self.foods: list[Food]    = []
        self.powerup: PowerUp | None = None
        self.active_effect: dict  = {}  
        self.shield_active  = False

        self.level_up_flash = 0  
        self.alive          = True

        self._spawn_normal_food()
        self._spawn_poison_food()

    @property
    def all_walls(self):
        return self.border_walls | self.obstacles

    @property
    def snake_color(self):
        return tuple(self.settings.get("snake_color", [50, 200, 50]))

    def _occupied(self):
        occupied = set(self.snake)
        occupied |= self.all_walls
        occupied |= {f.pos for f in self.foods}
        if self.powerup:
            occupied.add(self.powerup.pos)
        return occupied

    def _spawn_normal_food(self):
        normal_count = sum(1 for f in self.foods if f.KIND == "normal")
        while normal_count < 2:
            pos = random_free_pos(self.snake, self.all_walls, {f.pos for f in self.foods})
            if pos is None:
                break
            if random.random() < 0.8:
                self.foods.append(Food(pos, points=10))
            else:
                self.foods.append(Food(pos, points=30, lifetime_ms=7_000))
            normal_count += 1

    def _spawn_poison_food(self):
        if not any(f.KIND == "poison" for f in self.foods):
            pos = random_free_pos(self.snake, self.all_walls, {f.pos for f in self.foods})
            if pos:
                self.foods.append(PoisonFood(pos))

    def _maybe_spawn_powerup(self):
        if self.powerup is None and random.random() < 0.005: 
            kind = random.choice(["speed", "slow", "shield"])
            pos  = random_free_pos(self.snake, self.all_walls, {f.pos for f in self.foods})
            if pos:
                self.powerup = PowerUp(kind, pos)

    def set_direction(self, new_dir):
        opposites = {UP: DOWN, DOWN: UP, LEFT: RIGHT, RIGHT: LEFT}
        if new_dir != opposites.get(self.direction):
            self.next_dir = new_dir

    def tick(self):
        """Advance the game by one frame. Returns True while alive."""
        if not self.alive:
            return False

        now = pygame.time.get_ticks()

        if self.powerup and self.powerup.field_expired():
            self.powerup = None

        if self.active_effect and now > self.active_effect["end_tick"]:
            self._remove_effect(self.active_effect["kind"])
            self.active_effect = {}

        self.foods = [f for f in self.foods if not f.expired()]
        self._spawn_normal_food()
        self._spawn_poison_food()
        self._maybe_spawn_powerup()

        self.direction = self.next_dir
        head = (self.snake[0][0] + self.direction[0],
                self.snake[0][1] + self.direction[1])

        hit_wall = head in self.all_walls
        hit_self = head in self.snake

        if hit_wall or hit_self:
            if self.shield_active:
                self.shield_active = False
                self.active_effect = {}
                return True
            self.alive = False
            return False

        self.snake.insert(0, head)

        eaten = next((f for f in self.foods if f.pos == head), None)
        if eaten:
            self.foods.remove(eaten)
            if eaten.KIND == "poison":
                for _ in range(2):
                    if len(self.snake) > 1:
                        self.snake.pop()
                if len(self.snake) <= 1:
                    self.alive = False
                    return False
            else:
                self.score        += eaten.points * self.level
                self.food_in_level += 1
                self._check_level_up()
        else:
            self.snake.pop()

        if self.powerup and head == self.powerup.pos:
            self._apply_effect(self.powerup.kind, now)
            self.powerup = None

        return True

    def _check_level_up(self):
        if self.food_in_level >= self.food_needed and self.level < len(LEVELS):
            self.level        += 1
            self.food_in_level = 0
            self.food_needed, self.fps = LEVELS[self.level - 1]
            self.level_up_flash = pygame.time.get_ticks() + 1200
            if self.level >= 3:
                self.obstacles = build_obstacles(
                    self.level, self.snake, self.border_walls, self.obstacles
                )

    def _apply_effect(self, kind, now):
        if self.active_effect:
            self._remove_effect(self.active_effect["kind"])
        self.active_effect = {"kind": kind, "end_tick": now + POWERUP_EFFECT_TIME}
        if kind == "speed":
            self.fps = max(4, self.fps + 6)
        elif kind == "slow":
            self.fps = max(4, self.fps - 4)
        elif kind == "shield":
            self.shield_active = True

    def _remove_effect(self, kind):
        _, base_fps = LEVELS[self.level - 1]
        if kind in ("speed", "slow"):
            self.fps = base_fps
        elif kind == "shield":
            self.shield_active = False