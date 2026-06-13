"""Система коллизий."""

from src.core.config import block_map, doors
from src.systems.map_system import get_cell


def is_wall(x, y):
    """Проверяет, является ли точка препятствием для движения.

    Стены всегда блокируют движение. Дверь блокирует движение, пока открыта
    меньше чем на 80 процентов.
    """
    cell = get_cell(x, y)

    if cell in block_map:
        return True

    if cell in doors:
        door = doors[cell]
        return door.open_progress < 0.8

    return False
