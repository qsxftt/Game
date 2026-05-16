from math import pi, tan
from door import Door
import pygame


DEBUG = False
# экран
WIDTH = 1200
HEIGHT = 800
WIDTH_HALF = WIDTH // 2
HEIGHT_HALF = HEIGHT // 2
FPS = 60

# цвета
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GRAY = (128, 128, 128)
GREEN = (0, 255, 0)
YELLOW = (255, 220, 0)
WHITE = (255, 255, 255)

# текстуры
WALL_TEXTURE = pygame.image.load('assets/textures/wall.png')
DOOR_TEXTURE = pygame.image.load('assets/textures/door.png')
PISTOL_TEXTURE = pygame.image.load('assets/weapons/Pistol.png')
PISTOLR_TEXTURE = pygame.image.load('assets/weapons/Pistolreload.png')

# карта
def get_orient_door(x, y):
    left = (x - block_size, y) in block_map
    right = (x + block_size, y) in block_map
    up = (x, y - block_size) in block_map
    down = (x, y + block_size) in block_map

    if left and right:
        return "hor"

    if up and down:
        return "vert"

    return "vert"

block_size = 100
text_map =[
    'WWWWWWWWWWWW',
    'W..........W',
    'W..........W',
    'W..........W',
    'W..........W',
    'W......WWDWW',
    'W......D...W',
    'WWWWWWWWWWWW',
]

block_map = set()
door_positions = []
doors = {}
y_block = 0
for i in text_map:
    x_block = 0
    for j in i:
        if j == 'W':
            block_map.add((x_block, y_block))
        elif j == 'D':
            door_positions.append((x_block, y_block))
        x_block += block_size
    y_block += block_size

for x, y in door_positions:
    orient = get_orient_door(x, y)
    doors[(x, y)] = Door(x, y, orient, block_size)

# трассировка лучей
FOV = pi / 3
HALF_FOV = FOV / 2
MAX_DEPTH = WIDTH // block_size
NUM_RAYS = 120
DELTA_RAY = FOV / (NUM_RAYS - 1)
SCALE = WIDTH // NUM_RAYS
SCREEN_DISTANCE = WIDTH_HALF / tan(HALF_FOV)

# игрок
PLAYER_RADIUS = 15