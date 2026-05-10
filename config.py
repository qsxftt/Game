from math import pi


# экран
WIDTH = 1200
HEIGHT = 800
HEIGHT_HALF = HEIGHT // 2
FPS = 60

# цвета
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GRAY = (128, 128, 128)

#карта
block_size = 100
text_map =[
    'WWWWWWWWWWWW',
    'W..........W',
    'W..........W',
    'W..........W',
    'W..........W',
    'W......W...W',
    'W..........W',
    'WWWWWWWWWWWW',
]

block_map = set()
y_block = 0
for i in text_map:
    x_block = 0
    for j in i:
        if j == 'W':
            block_map.add((x_block, y_block))
        x_block += block_size
    y_block += block_size

# трассировка лучей
FOV = pi / 3
HALF_FOV = FOV / 2
max_depth = WIDTH // block_size
NUM_RAYS = 120
DELTA_RAY = FOV / (NUM_RAYS - 1)
SCALE = WIDTH // NUM_RAYS
