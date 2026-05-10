from math import sin, cos, tan
import pygame

from config import *


def is_wall(x, y):
    endX = x // block_size * block_size
    endY = y // block_size * block_size

    return (endX, endY) in block_map

def cast_single_ray(player, angle):
    sin_a = sin(angle)
    cos_a = cos(angle)
    tan_a = tan(angle)

    # Пересечения с вертикальной стенкой
    vert_x = 0
    vert_y = 0
    vert_depth = float("inf")

    if cos_a > 0:
        x_vert = (player.x // block_size) * block_size + block_size
        vert_delta_x = block_size
    else:
        x_vert = (player.x // block_size) * block_size
        vert_delta_x = -block_size

    y_vert = player.y + (x_vert - player.x) * tan_a
    vert_delta_y = vert_delta_x * tan_a

    for _ in range(MAX_DEPTH):
        if cos_a > 0:
            x_check = x_vert
        else:
            x_check = x_vert - 1

        if is_wall(x_check, y_vert):
            vert_x = x_vert
            vert_y = y_vert
            vert_depth = (vert_x - player.x) / cos_a
            break

        x_vert += vert_delta_x
        y_vert += vert_delta_y

    # Пересечения с горизонтальной стенкой
    hor_x = 0
    hor_y = 0
    hor_depth = float("inf")

    if sin_a > 0:
        y_hor = (player.y // block_size) * block_size + block_size
        hor_delta_y = block_size
    else:
        y_hor = (player.y // block_size) * block_size
        hor_delta_y = -block_size

    x_hor = player.x + (y_hor - player.y) / tan_a
    hor_delta_x = hor_delta_y / tan_a

    for _ in range(MAX_DEPTH):
        if sin_a > 0:
            y_check = y_hor
        else:
            y_check = y_hor - 1

        if is_wall(x_hor, y_check):
            hor_x = x_hor
            hor_y = y_hor
            hor_depth = (hor_y - player.y) / sin_a
            break

        x_hor += hor_delta_x
        y_hor += hor_delta_y

    if vert_depth < hor_depth:
        return vert_x, vert_y, vert_depth
    else:
        return hor_x, hor_y, hor_depth
