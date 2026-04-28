CELL  = 20
COLS  = 30
ROWS  = 25
W     = COLS * CELL          
H     = ROWS * CELL + 60    
HUD_H = 60

BLACK   = (0,   0,   0)
WHITE   = (255, 255, 255)
GREEN   = (50,  200,  50)
DK_GRN  = (30,  140,  30)
RED     = (220,  50,  50)
YELLOW  = (255, 220,   0)
GRAY    = (130, 130, 130)
DK_GRAY = (50,   50,  50)
WALL_C  = (80,   80,  80)
BG      = (20,   20,  20)
POISON  = (139,   0,   0)   
PURPLE  = (160,  32, 240)   
CYAN    = (0,   200, 200)  
ORANGE  = (255, 140,   0)   
OBS_C   = (100,  60,  20)   

UP    = (0, -1)
DOWN  = (0,  1)
LEFT  = (-1, 0)
RIGHT = (1,  0)

LEVELS = [
    (3,  8),
    (4, 11),
    (5, 14),
    (6, 17),
    (7, 20),
]

POWERUP_FIELD_TIME = 8_000   
POWERUP_EFFECT_TIME = 5_000 

OBSTACLES_PER_LEVEL = 6

DB_CONFIG = {
    "host":     "localhost",
    "dbname":   "snake_game",
    "user":     "postgres",
    "password": "postgres",
    "port":     5432,
}