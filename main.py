import pygame
from config import *
from player import Player
from enemy import Dwarf
from math import cos, sin, pi
from func import *

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
font = pygame.font.SysFont('Arial', 32)
clock = pygame.time.Clock()
player = Player()
enemies = [
    Dwarf(300, 200)
]


running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    pygame.draw.rect(screen, (66, 170, 255), (0, 0, WIDTH, HEIGHT_HALF))
    pygame.draw.rect(screen, (25, 25, 25), (0, HEIGHT_HALF, WIDTH, HEIGHT_HALF))

    shot_fired = player.move()
    ray_casting(screen, player)
    update_doors()
    for enemy in enemies:
        enemy.update(player)
        enemy.draw(screen, player)
    player.weapon.draw(screen)
    ammo_text = font.render(f'{player.weapon.ammo}/{player.weapon.reserve_ammo}', True, GREEN)
    hp_text = font.render(f'HP: {player.health}', True, GREEN)
    screen.blit(ammo_text, (20, 20))
    screen.blit(hp_text, (100, 20))
    if shot_fired:
        player_shoot(player, enemies)

    if player.health <= 0:
        print('Game Over')
        running = False

    size = 10
    pygame.draw.line(screen, WHITE, (WIDTH_HALF - size, HEIGHT_HALF), (WIDTH_HALF + size, HEIGHT_HALF), 2)
    pygame.draw.line(screen, WHITE, (WIDTH_HALF, HEIGHT_HALF - size), (WIDTH_HALF, HEIGHT_HALF  + size), 2)

    if DEBUG:
        draw_map(screen, player)
        for enemy in enemies:
            enemy.draw_debug(screen)

    pygame.display.flip()
    pygame.display.set_caption(f'{clock.get_fps()}')
    clock.tick(FPS)
    
pygame.quit()