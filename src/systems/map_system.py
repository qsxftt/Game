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
    '''Определяет тип препятствия в мировой точке

    Args:
        x: мировая координата по горизонтали
        y: мировая координата по вертикали
        level: текущий уровень

    Returns:
        Строка wall, door, terminal или None
    '''
    cell = get_cell(x, y)

    if cell in level.block_map:
        return 'wall'

    if cell in level.doors and level.doors[cell].open_progress < 1.0:
        return 'door'

    if cell == level.terminal_pos:
        return 'terminal'

    return None


# ============================================================
# PAINTER'S ALGORITHM - СОРТИРОВКА СПРАЙТОВ ПО ГЛУБИНЕ
# ============================================================

def get_sprite_sorted(pickups, enemies, player):
    '''Сортирует спрайты от дальних к ближним

    Args:
        pickups: список ресурсов уровня
        enemies: список врагов уровня
        player: модель игрока

    Returns:
        Общий список объектов в порядке отрисовки
    '''
    sprites = pickups + enemies
    return sorted(sprites, key=lambda sprite: get_depth(sprite, player), reverse=True)

def world_to_grid(x, y):
    '''Переводит мировые координаты в координаты клетки

    Args:
        x: мировая координата по горизонтали
        y: мировая координата по вертикали

    Returns:
        Координаты клетки текстовой карты
    '''
    return int(x // block_size), int(y // block_size)

def grid_to_world(x, y):
    '''Переводит координаты клетки в мировые координаты

    Args:
        x: координата клетки по горизонтали
        y: координата клетки по вертикали

    Returns:
        Мировые координаты центра клетки
    '''
    return x * block_size + block_size // 2, y * block_size + block_size // 2
