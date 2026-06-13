"""Ray casting renderer и debug-отрисовка карты."""

from math import cos, sin, tan

import pygame

from src.core.config import (
    DEBUG,
    DELTA_RAY,
    DOOR_TEXTURE,
    GRAY,
    GREEN,
    HEIGHT,
    HEIGHT_HALF,
    HALF_FOV,
    MAX_DEPTH,
    NUM_RAYS,
    RED,
    SCALE,
    SCREEN_DISTANCE,
    WALL_TEXTURE,
    YELLOW,
    block_map,
    block_size,
    doors,
    current_level
)
from src.systems.door_system import get_door
from src.systems.map_system import get_block_type


def apply_shade_texture(texture_column, shade):
    """Возвращает затемнённую копию вертикальной колонки текстуры."""
    shade *= 255
    texture_column_copy = texture_column.copy()
    texture_column_copy.fill((shade, shade, shade), special_flags=pygame.BLEND_MULT)

    return texture_column_copy


def cast_ray_to_door(player, angle, door):
    """Проверяет пересечение луча с движущейся дверной панелью.

    Дверь считается не целой клеткой, а тонким отрезком, который смещается
    во время открытия. Это позволяет ray casting рисовать открывающуюся дверь.
    """
    sin_a = sin(angle)
    cos_a = cos(angle)

    orient, x1, y1, x2, y2 = door.get_panel_segment()

    if orient == "hor":
        depth = (y1 - player.y) / sin_a
        hit_x = player.x + cos_a * depth

        if depth > 0 and x1 <= hit_x <= x2:
            return hit_x, y1, depth

    if orient == "vert":
        depth = (x1 - player.x) / cos_a
        hit_y = player.y + sin_a * depth

        if depth > 0 and y1 <= hit_y <= y2:
            return x1, hit_y, depth

    return None


def cast_single_ray(player, angle):
    """Выпускает один луч и возвращает ближайшее столкновение.

    Луч отдельно проверяет пересечения с вертикальными и горизонтальными
    линиями сетки, а затем выбирает ближайшее найденное попадание.
    Возвращает: hit_x, hit_y, depth, side, block_type.
    """
    sin_a = sin(angle)
    cos_a = cos(angle)
    tan_a = tan(angle)

    # Пересечения с вертикальными линиями сетки.
    vert_x = 0
    vert_y = 0
    vert_type = None
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

        block_type = get_block_type(x_check, y_vert)

        if block_type == "wall":
            vert_x = x_vert
            vert_y = y_vert
            vert_depth = (vert_x - player.x) / cos_a
            vert_type = "wall"
            break

        if block_type == "door":
            door = get_door(x_check, y_vert)
            door_hit = cast_ray_to_door(player, angle, door)

            if door_hit:
                vert_x, vert_y, vert_depth = door_hit
                vert_type = "door"
                break

        x_vert += vert_delta_x
        y_vert += vert_delta_y

    # Пересечения с горизонтальными линиями сетки.
    hor_x = 0
    hor_y = 0
    hor_type = None
    hor_depth = float("inf")
    if tan_a != 0:
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

            block_type = get_block_type(x_hor, y_check)

            if block_type == "wall":
                hor_x = x_hor
                hor_y = y_hor
                hor_depth = (hor_y - player.y) / sin_a
                hor_type = "wall"
                break

            if block_type == "door":
                door = get_door(x_hor, y_check)
                door_hit = cast_ray_to_door(player, angle, door)

                if door_hit:
                    hor_x, hor_y, hor_depth = door_hit
                    hor_type = "door"
                    break

            x_hor += hor_delta_x
            y_hor += hor_delta_y

    if vert_depth < hor_depth:
        return vert_x, vert_y, vert_depth, 'vert', vert_type
    else:
        return hor_x, hor_y, hor_depth, 'hor', hor_type


def ray_casting(screen, player):
    """Рисует псевдо-3D стены и двери через веер лучей от игрока."""
    start = player.angle - HALF_FOV

    for ray in range(NUM_RAYS):
        ray_angle = start + ray * DELTA_RAY
        hit_x, hit_y, depth, side, block_type = cast_single_ray(player, ray_angle)
        shade = max(30, 255 - (depth // 3)) / 255

        if side == 'vert':
            texture_offset = int(hit_y % block_size)
        else:
            texture_offset = int(hit_x % block_size)
            shade *= 0.75

        if block_type == 'door':
            texture = DOOR_TEXTURE
        else:
            texture = WALL_TEXTURE

        # Убирает fish-eye и делает расстояние перпендикулярным экрану.
        depth *= cos(player.angle - ray_angle)

        wall_height = int(block_size * SCREEN_DISTANCE / depth)
        wall_x = ray * SCALE

        if wall_height <= HEIGHT:
            wall_y = int(HEIGHT_HALF - wall_height // 2)
            texture_column = texture.subsurface(texture_offset, 0, 1, block_size)
            texture_column = apply_shade_texture(texture_column, shade)
            texture_column = pygame.transform.scale(texture_column, (SCALE, wall_height))
        else:
            wall_y = 0

            texture_y = int((wall_height - HEIGHT) / 2 / wall_height * block_size)
            texture_height = int(HEIGHT / wall_height * block_size)

            texture_column = texture.subsurface(texture_offset, texture_y, 1, texture_height)
            texture_column = apply_shade_texture(texture_column, shade)
            texture_column = pygame.transform.scale(texture_column, (SCALE, HEIGHT))

        screen.blit(texture_column, (wall_x, wall_y))

        if DEBUG:
            pygame.draw.line(screen, RED, (player.x, player.y), (hit_x, hit_y), 2)
            pygame.draw.circle(screen, RED, (hit_x, hit_y), 5)


def draw_map(screen, player):
    """Рисует debug-карту сверху: стены, двери и позицию игрока."""
    for x, y in block_map:
        pygame.draw.rect(screen, GRAY, (x, y, block_size, block_size), 2)

    for cell, door in doors.items():
        x, y = cell

        if door.state == 'opening' or door.state == 'closing':
            color = YELLOW
        elif door.state == 'open':
            color = GREEN
        else:
            color = RED

        rect = door.get_panel_rect()
        pygame.draw.rect(screen, color, rect)

    pygame.draw.circle(screen, RED, (player.x, player.y), 10)
    x, y = current_level.terminal_pos
    x, y = x + block_size // 2, y + block_size // 2
    pygame.draw.circle(screen, (77, 150, 9), (x, y), 10)
