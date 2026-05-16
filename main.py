import pygame
from config import *
from player import Player
from math import cos, sin, pi
from func import *

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
font = pygame.font.SysFont('Arial', 32)
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
    player.weapon.draw(screen)
    ammo_text = font.render(f'{player.weapon.ammo}/{player.weapon.reserve_ammo}', True, GREEN)
    screen.blit(ammo_text, (20, 20))

    size = 10
    pygame.draw.line(screen, WHITE, (WIDTH_HALF - size, HEIGHT_HALF), (WIDTH_HALF + size, HEIGHT_HALF), 2)
    pygame.draw.line(screen, WHITE, (WIDTH_HALF, HEIGHT_HALF - size), (WIDTH_HALF, HEIGHT_HALF  + size), 2)

    if DEBUG:
        draw_map(screen, player)

    pygame.display.flip()
    pygame.display.set_caption(f'{clock.get_fps()}')
    clock.tick(FPS)
    
pygame.quit()