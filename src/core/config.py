"""Глобальные настройки и временные данные текущего прототипа.

Пока здесь лежит не только конфигурация, но и статичная карта с дверями.
Позже карту лучше перенести в Level, а текстуры — в отдельный assets-модуль.
"""

from math import pi, tan

import pygame

from src.models.level import Level


DEBUG = True

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
text_map_1 = [
    'WWWWWWWWWWWW',
    'W........T.W',
    'W...P......W',
    'W..........W',
    'W..........W',
    'W..E...WWDWW',
    'W......D...W',
    'WWWWWWWWWWWW',
]

text_map_2 = [
    'WWWWWWWWWWWW',
    'W.E.W....T.W',
    'W...W......W',
    'WWWDW......W',
    'W..........W',
    'W........P.W',
    'W..........W',
    'WWWWWWWWWWWW',
]

sector_maps = [
    text_map_1,
    text_map_2
]



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
