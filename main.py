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
    screen.fill(BLACK)


    player.move()
    

    
    for x, y in block_map:
        pygame.draw.rect(screen, GRAY, (x, y, block_size, block_size), 1)

    start = player.angle - HALF_FOV
    for ray in range(NUM_RAYS):
        ray_angle = start + ray * DELTA_RAY

        endX, endY, depth = cast_single_ray(player, ray_angle)
        depth *= cos(player.angle - ray_angle)
        wall_height = 50000 // max(depth, 1)
        wall_x = ray * SCALE
        wall_y = HEIGHT_HALF - wall_height // 2
        # pygame.draw.line(screen, RED, (player.x, player.y), (endX, endY), 2)
        # pygame.draw.circle(screen, RED, (endX, endY), 5)
        pygame.draw.rect(screen, GRAY, (wall_x, wall_y, SCALE, wall_height))

    pygame.draw.circle(screen, RED, (player.x, player.y), 10)

    pygame.display.flip()
    clock.tick(FPS)
    
pygame.quit()