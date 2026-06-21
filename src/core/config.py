'''Глобальные настройки, константы и загружаемые ресурсы игры'''

from math import pi, tan

import pygame

# Экран
WIDTH = 1600
HEIGHT = 1000
WIDTH_HALF = WIDTH // 2
HEIGHT_HALF = HEIGHT // 2
FPS = 60

# Текстуры
WALL_TEXTURE = pygame.image.load('assets/textures/wall.png')
DOOR_TEXTURE = pygame.image.load('assets/textures/door.png')
TERMINAL_TEXTURE = pygame.image.load('assets/textures/terminal.png')
PISTOL_TEXTURE = pygame.image.load('assets/weapons/Pistol.png')
PISTOLR_TEXTURE = pygame.image.load('assets/weapons/Pistolreload.png')
SHOTGUN_TEXTURE = pygame.image.load('assets/weapons/shotgun.png')
SHOTGUNR_TEXTURE = pygame.image.load('assets/weapons/shotgunr.png')
BRUTE_WALK_TEXTURE = pygame.image.load('assets/enemies/brute_walk.png')
BRUTE_ATTACK_TEXTURE = pygame.image.load('assets/enemies/brute_attack.png')
SCIENTIST_WALK_TEXTURE = pygame.image.load('assets/enemies/scientist_walk.png')
SCIENTIST_ATTACK_TEXTURE = pygame.image.load('assets/enemies/scientist_attack.png')
MEDKIT_TEXTURE = pygame.image.load('assets/pickups/medkit.png')
AMMO_TEXTURE = pygame.image.load('assets/pickups/ammo.png')


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
