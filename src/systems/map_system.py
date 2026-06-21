'''Запросы к клеточной карте и общие утилиты для координат'''

from math import cos, sin

from src.core.config import block_size
from src.systems.visibility_system import get_depth


def get_cell(x, y):
    '''Возвращает левый верхний угол клетки, содержащей координаты x/y'''
    endX = x // block_size * block_size
    endY = y // block_size * block_size

    return endX, endY


def get_front_cell(player):
    '''Возвращает клетку на расстоянии одного блока перед игроком'''
    front_x = player.x + cos(player.angle) * block_size
    front_y = player.y + sin(player.angle) * block_size

    cell = get_cell(front_x, front_y)

    return cell


def get_block_type(x, y, level):
    '''Возвращает тип блока в точке: wall, door, terminal или None'''
    cell = get_cell(x, y)

    if cell in level.block_map:
        return 'wall'

    if cell in level.doors and level.doors[cell].open_progress < 1.0:
        return 'door'

    if cell == level.terminal_pos:
        return 'terminal'

    return None


def get_sprite_sorted(pickups, enemies, player):
    '''Возвращает pickups и enemies, отсортированные от дальних к ближним'''
    sprites = pickups + enemies
    return sorted(sprites, key=lambda sprite: get_depth(sprite, player), reverse=True)


def world_to_grid(x, y):
    '''Переводит мировые координаты в координаты клетки текстовой карты'''
    return int(x // block_size), int(y // block_size)


def grid_to_world(x, y):
    '''Возвращает центр клетки карты в мировых координатах'''
    return x * block_size + block_size // 2, y * block_size + block_size // 2
