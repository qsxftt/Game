from math import sin, cos, tan
import pygame

from config import *


# Работа с клетками карты

def get_cell(x, y):
    '''
    Возвращает координаты клетки карты по переданным координатам
    '''
    endX = x // block_size * block_size
    endY = y // block_size * block_size

    return endX, endY


def get_front_cell(player):
    '''
    Возвращает координаты клетки, находящейся перед игроком
    '''
    front_x = player.x + cos(player.angle) * block_size
    front_y = player.y + sin(player.angle) * block_size

    cell = get_cell(front_x, front_y)

    return cell


# Проверки блоков и препятствий

def is_wall(x, y):
    '''
    Проверяет, является ли клетка препятствием для движения
    Обычные стены всегда считаются препятствием
    Дверь считается препятствием, пока её open_progress меньше 0.8
    '''
    cell = get_cell(x, y)

    if cell in block_map:
        return True

    if cell in doors:
        door = doors[cell]
        return door.open_progress < 0.8

    return False


def get_block_type(x, y):
    '''
    Возвращает тип блока в указанной клетке карты
    '''
    cell = get_cell(x, y)

    if cell in block_map:
        return 'wall'

    if cell in doors and doors[cell].open_progress < 1.0:
        return 'door'

    return None


# Работа с цветом

def apply_shade(color, shade):
    '''
    Возвращает затемнённую версию переданного цвета
    shade работает как коэффициент яркости
    '''
    return tuple(int(channel * shade) for channel in color)


# Работа с дверями

def get_door(x, y):
    '''
    Возвращает объект двери по переданным координатам
    '''
    cell = get_cell(x, y)
    return doors.get(cell)


def open_door(player):
    '''
    Пытается открыть дверь, находящуюся перед игроком
    Если перед игроком есть дверь, вызывается её метод open()
    '''
    cell = get_front_cell(player)

    if cell in doors:
        return doors[cell].open()

    return False


def update_doors():
    '''
    Обновляет состояние всех дверей на карте
    '''
    for door in doors.values():
        door.update()


def cast_ray_to_door(player, angle, door):
    '''
    Проверяет пересечение луча с движущейся дверной перегородкой

    Дверь рассматривается не как целая клетка, а как тонкий отрезок
    который может смещаться при открытии
    '''
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


# Ray casting

def cast_single_ray(player, angle):
    '''
    Выпускает один луч и ищет ближайшее столкновение со стеной или дверью

    Луч проверяет пересечения с вертикальными и горизонтальными линиями сетки карты
    После этого выбирается ближайшее найденное попадание
    '''
    sin_a = sin(angle)
    cos_a = cos(angle)
    tan_a = tan(angle)

    # Пересечения с вертикальными линиями сетки
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

    # Пересечения с горизонтальными линиями сетки
    hor_x = 0
    hor_y = 0
    hor_type = None
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
    """
    Выпускает веер лучей от игрока и рисует 3D сцену

    Каждый луч ищет ближайшее столкновение со стеной или дверью
    По расстоянию до столкновения вычисляется высота вертикальной полоски
    Также применяется затемнение по расстоянию и затемнение горизонтальных сторон
    """
    start = player.angle - HALF_FOV

    for ray in range(NUM_RAYS):
        ray_angle = start + ray * DELTA_RAY
        endX, endY, depth, side, block_type = cast_single_ray(player, ray_angle)

        depth *= cos(player.angle - ray_angle)

        wall_height = block_size * SCREEN_DISTANCE // depth
        wall_x = ray * SCALE
        wall_y = HEIGHT_HALF - wall_height // 2

        shade = max(30, 255 - (depth // 3)) / 255

        if side == 'hor':
            shade *= 0.75

        if block_type == 'door':
            wall_color = apply_shade(GREEN, shade)
        else:
            wall_color = apply_shade(GRAY, shade)

        pygame.draw.rect(screen, wall_color, (wall_x, wall_y, SCALE, wall_height))

        if DEBUG:
            pygame.draw.line(screen, RED, (player.x, player.y), (endX, endY), 2)
            pygame.draw.circle(screen, RED, (endX, endY), 5)


# Debug-отрисовка

def draw_map(screen, player):
    '''
    Рисует debug-карту сверху
    '''
    for x, y in block_map:
        pygame.draw.rect(screen, GRAY, (x, y, block_size, block_size), 2)

    for cell, door in doors.items():
        x, y = cell

        if door.is_open:
            color = GREEN
        elif door.is_opening:
            color = YELLOW
        else:
            color = RED

        rect = door.get_panel_rect()
        pygame.draw.rect(screen, color, rect)

    pygame.draw.circle(screen, RED, (player.x, player.y), 10)