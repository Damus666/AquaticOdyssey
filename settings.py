import pygame
from pygame import Vector2 as vec
from random import randint, choice, uniform

# window
pygame.display.init()
WIDTH, HEIGHT = WINDOW_SIZES = pygame.display.get_desktop_sizes()[0]
#WIDTH, HEIGHT = WINDOW_SIZES = (800,400)
H_WIDTH, H_HEIGHT = WIDTH//2, HEIGHT//2
WINDOW_CENTER = vec(H_WIDTH, H_HEIGHT)
WINDOW_TITLE = "Aquatic Odyssey"
WINDOW_FPS = 0

# level
LEVEL_SPEED = 250
MIDBG_SPEED_MUL = 0.6
BG_SPEED_MUL = 0.3
BG_SCALE = WIDTH/960
SCALE = BG_SCALE*2
ANIMATION_SPEED = 6
TOP_H  = 62 * BG_SCALE
BOTTOM_H = 57 * BG_SCALE
TILE_W = 80 * BG_SCALE
OS_RANGE = (0.0009, 0.0025)
OS_RANGE_UI = (0.0012, 0.0035)
SPEED_INCREASE = 1.6
TRANSITION_SPEED = 10
TRANSITION_THRESHOLD = 30
TRANSITION_COL = (20, 20, 20)

BUBBLE_OFFSET = 50
DART_AMOUNT_RANGE = (2,4)
MINE_AMOUNTS = [1,2,3,5,8]
MINE_ROTATE_SPEED = (30,60)
MINE_SPEED = (1.10,1.20)
POWERUP_WEIGHTS = [100,50,50]
COINS_FORMATIONS = {
    "line":(5,15),
    "wave":(5,15),
    "diagonal":(5,15),
    "chess":(3, 8),
    "area":(3, 8),
    "rect":(3, 8),
    "circle":(4, 10),
}
POWERUP_TYPES = {
    "extra-life":["heart",2.5*BG_SCALE], # sprite name, scale
    "magnet":["magnet",2*BG_SCALE],
    "energy":["energy",2*BG_SCALE],
}
SPAWN_TIME_RANGE = {
    "bubble-g": vec(50,150),
    "bubble-s": vec(3000,5000),
    "fish-normal": vec(4000,8000),
    "fish-dart": vec(5000,12000),
    "fish-bomb": vec(8000,17000),
    "coin": vec(2800,5000),
    "powerup": vec(16000,25000),
    "mine": vec(2000,5000),
    "prop-big": vec(1800,3000),
    "prop-small": vec(500,1000),
    "island": vec(4000, 6500),
    "angled-tile": vec(3000,6000),
    "light": vec(2500,3500),
    "wave": vec(12000,22000)
}
FISH_SPEED = {
    "normal":1.6,
    "dart": 2.2,
    "bomb": 1.2,
}
ISLAND_SCALES = {
    "normal": vec(0.6,1),
    "ball": vec(1.2,1.7),
}
CHANCES = {
    "second-normal-fish":20,
    "direction-flip":50,
    "normal-island-g":20,
    "first-chain":30,
    "second-chain":20,
    "temple-flip":50,
    "menu-chain": 50,
}
BG_ATTRS = {
    "speed-mul": (0.75, 0.80),
    "spawn-amount": (3,5),
    "x-scale": (0.8,2.0),
    "y-mul": 1.1,
    "neg-angles": (-35,-10),
    "pos-angles": (5,15),
    "alpha": (25,40),
}
PROP_ATTRS = {
    "scale":(1.0,1.5),
    "arc-scale": (0.6,0.8),
    "parallax-speed": 0.8,
    "bubble-cooldown": (3000,5000),
}

# wave
POWERUP_SPAWN_MUL = 6
FISH_ENABLE_SCORE = {
    "normal":80,
    "dart":200,
    "bomb":400,
}
MINE_AMOUNT_WEIGHTS = [
    [100,40,20,0,0],
    [100,60,30,8,2],
    [100,100,50,16,6],
    [100,125,80,40,12],
    [100,180,120,80,20]
]

# player
SWIM_ACCELLERATION = 400
DECELERATION_MUL = 2
SWIM_MAX_SPEED = 350
AUTODIVE_SPEED = 80
PLAYER_LEFT_OFFSET = 0
SCORE_INCREASE = WIDTH//5

# menu
MENU_RATIO_DICT = {28: '-', 9: 'S', 35: 'i', 13: '8', 8: 'U', 24: 'W', 31: 'w', 37: 'd', 27: 'v', 
                    14: 'L', 21: 'd', 20: 'V', 7: '0', 38: 'S', 18: 'U', 30: 'Y', 12: 'C', 41: 'i', 
                    25: 'Y', 19: '2', 36: 'O', 33: 'Z', 23: 't', 29: 'o', 5: '0', 10: 'W', 32: 'Q', 
                    2: 'a', 34: '4', 11: '6', 6: 'f', 17: 'C', 39: '0', 4: 'i', 16: 'h', 43: '=', 
                    0: 'n', 42: 'U', 26: 'C', 40: 'z', 15: 't', 22: 'z', 1: 'c', 3: 'F'}
MENU_RATIO_LIST = sorted(list(MENU_RATIO_DICT.items()), key = lambda tuple: tuple[0])
MENU_RATIO = ""
for thing in MENU_RATIO_LIST: MENU_RATIO += thing[1]
MENU_RATIO = MENU_RATIO.encode() 

MENU_PLAYER_SPEED = 400
FILL_COLOR = (13,26,32)
UI_SPACING = 8*BG_SCALE
SHOPITEM_MINE_SIZE = HEIGHT//6
SHOPITEM_IMG_SIZE = SHOPITEM_MINE_SIZE//2.5
ON_CHAIN_COL = (44,107,101)
SHOP_LERP_SPEED = 3
MENU_STAGES = {
    "extra-life": {
        "values": [ 1,2,3,4,5 ],
        "price": 250
    },
    "energy-lifetime":{
        "values": [ 20000, 30000, 50000, 80000, 150000],
        "price": 300
    },
    "magnet-lifetime": {
        "values": [20000, 30000, 50000, 80000, 150000],
        "price": 300,
    },
    "magnet-power": {
        "values": [1.0, 1.2, 1.5, 2.0, 3.0],
        "price": 250,
    }
}
DEFAULT_DATA = {
    "extra-life": 0,
    "energy-lifetime":0,
    "magnet-lifetime":0,
    "magnet-power":0,
}