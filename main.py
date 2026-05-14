import pygame
from config import *
from player import Player
from math import cos, sin, pi
from func import *

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
player = Player()

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    pygame.draw.rect(screen, (66, 170, 255), (0, 0, WIDTH, HEIGHT_HALF))
    pygame.draw.rect(screen, (25, 25, 25), (0, HEIGHT_HALF, WIDTH, HEIGHT_HALF))

    player.move()
    ray_casting(screen, player)
    update_doors()

    if DEBUG:
        draw_map(screen, player)

    pygame.display.flip()
    pygame.display.set_caption(f'{clock}')
    clock.tick(FPS)
    
pygame.quit()