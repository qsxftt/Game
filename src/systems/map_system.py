"""Система запросов к сетке карты."""

from math import cos, sin

from src.core.config import block_map, block_size, doors


def get_cell(x, y):
    """Возвращает левый верхний угол клетки, содержащей координаты x/y."""
    endX = x // block_size * block_size
    endY = y // block_size * block_size

    return endX, endY


def get_front_cell(player):
    """Возвращает клетку на расстоянии одного блока перед игроком."""
    front_x = player.x + cos(player.angle) * block_size
    front_y = player.y + sin(player.angle) * block_size

    cell = get_cell(front_x, front_y)

    return cell


def get_block_type(x, y):
    """Возвращает тип блока в точке: 'wall', 'door' или None."""
    cell = get_cell(x, y)

    if cell in block_map:
        return 'wall'

    if cell in doors and doors[cell].open_progress < 1.0:
        return 'door'

    return None
