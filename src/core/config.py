"""Глобальные настройки, константы и загружаемые ресурсы игры."""

from math import pi, tan

import pygame


DEBUG = False

# Экран
WIDTH = 1600
HEIGHT = 1000
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
TERMINAL_TEXTURE = pygame.image.load('assets/textures/terminal.png')
PISTOL_TEXTURE = pygame.image.load('assets/weapons/Pistol.png')
PISTOLR_TEXTURE = pygame.image.load('assets/weapons/Pistolreload.png')
ENEMY1_TEXTURE = pygame.image.load('assets/enemies/FLYING.png')
ENEMY12_TEXTURE = pygame.image.load('assets/enemies/ATTACK.png')
MEDKIT_TEXTURE = pygame.image.load('assets/pickups/medkit.png')
AMMO_TEXTURE = pygame.image.load('assets/pickups/ammo.png')

PISTOL_ICON = pygame.image.load('assets/icons/pistol_icon.png')
SHOTGUN_ICON = pygame.image.load('assets/icons/shotgun_icon.png')

# Карта
block_size = 100
TOTAL_SECTORS = 5

# Трассировка лучей
FOV = pi / 3
HALF_FOV = FOV / 2
MAX_DEPTH = 30
NUM_RAYS = 320
DELTA_RAY = FOV / (NUM_RAYS - 1)
SCALE = WIDTH // NUM_RAYS
SCREEN_DISTANCE = WIDTH_HALF / tan(HALF_FOV)

# Игрок
PLAYER_RADIUS = 15
