from math import sin, cos
import pygame

from config import *


def is_wall(x, y):
    endX = x // block_size * block_size
    endY = y // block_size * block_size

    return (endX, endY) in block_map

def get_ray_point(player, depth, angle):
    x = player.x + depth * cos(angle)
    y = player.y + depth * sin(angle)

    return x, y

def cast_single_ray(player, angle):
    for depth in range(0, WIDTH, 5):
        x, y = get_ray_point(player, depth, angle)
        
        if is_wall(x, y):
            
            return x, y, depth