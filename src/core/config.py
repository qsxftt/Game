"""Глобальные настройки и временные данные текущего прототипа.

Пока здесь лежит не только конфигурация, но и статичная карта с дверями.
Позже карту лучше перенести в Level, а текстуры — в отдельный assets-модуль.
"""

from math import pi, tan

import pygame

from src.models.door import Door


DEBUG = False

# Экран
WIDTH = 1200
HEIGHT = 800
WIDTH_HALF = WIDTH // 2
HEIGHT_HALF = HEIGHT // 2
FPS = 60

# Цвета
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GRAY = (128, 128, 128)
GREEN = (0, 255, 0)
YELLOW = (255, 220, 0)
WHITE = (255, 255, 255)

# Текстуры
WALL_TEXTURE = pygame.image.load('assets/textures/wall.png')
DOOR_TEXTURE = pygame.image.load('assets/textures/door.png')
PISTOL_TEXTURE = pygame.image.load('assets/weapons/Pistol.png')
PISTOLR_TEXTURE = pygame.image.load('assets/weapons/Pistolreload.png')
ENEMY1_TEXTURE = pygame.image.load('assets/enemies/FLYING.png')
ENEMY12_TEXTURE = pygame.image.load('assets/enemies/ATTACK.png')

# Карта
block_size = 100
text_map = [
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


def get_orient_door(x, y):
    """Определяет ориентацию двери по соседним стенам."""
    left = (x - block_size, y) in block_map
    right = (x + block_size, y) in block_map
    up = (x, y - block_size) in block_map
    down = (x, y + block_size) in block_map

    if left and right:
        return "hor"

    if up and down:
        return "vert"

    return "vert"


y_block = 0
for row in text_map:
    x_block = 0
    for tile in row:
        if tile == 'W':
            block_map.add((x_block, y_block))
        elif tile == 'D':
            door_positions.append((x_block, y_block))
        x_block += block_size
    y_block += block_size

for x, y in door_positions:
    orient = get_orient_door(x, y)
    doors[(x, y)] = Door(x, y, orient, block_size)

# Трассировка лучей
FOV = pi / 3
HALF_FOV = FOV / 2
MAX_DEPTH = WIDTH // block_size
NUM_RAYS = 120
DELTA_RAY = FOV / (NUM_RAYS - 1)
SCALE = WIDTH // NUM_RAYS
SCREEN_DISTANCE = WIDTH_HALF / tan(HALF_FOV)

# Игрок
PLAYER_RADIUS = 15
