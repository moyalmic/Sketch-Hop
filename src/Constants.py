import pygame as pg

# Screen dimensions
WIN_WIDTH = 900
WIN_HEIGHT = 900

# Player data
PLAYER_ACC = 1
PLAYER_FRICT = -0.15
PLAYER_GRAV = 1
PLAYER_JUMP = 25
MAX_JUMP = 0
for i in range(PLAYER_JUMP + 1):
    MAX_JUMP += i - (0.5 * PLAYER_GRAV)

# Sprites
basePlatform = pg.image.load("../sprites/Terrain/Ground Platform(900x92).png")
woodenPlatform = pg.image.load("../sprites/Terrain/Platform(92x30).png")
trampolineIdle = pg.image.load("../sprites/Traps/Trampoline/Idle (46x22).png")
quip = pg.image.load("../sprites/Other/Quip.png")
background = pg.image.load("../sprites/Background/GreenBig.png")

# Other utility
PLAT_WIDTH = 92
PLAT_HEIGHT = 30
FONT_NAME = 'verdana'
FPS = 60
NUM_OF_PLATS = 7
GAME_NAME = 'Sketch Hop'
TRAMP_WIDTH_IDLE = 54
TRAMP_HEIGHT_IDLE = 22
BOOST_POWER = 40
POW_FREQ = 9

# Colors

BLACK = (0, 0, 0)