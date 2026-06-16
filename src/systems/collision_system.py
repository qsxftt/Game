"""Система коллизий."""

from src.systems.map_system import get_cell


def is_wall(x, y, level):
    """Проверяет, является ли точка препятствием для движения.

    Стены всегда блокируют движение. Дверь блокирует движение, пока открыта
    меньше чем на 80 процентов. Терминал тоже считается препятствием.
    """
    cell = get_cell(x, y)

    if cell in level.block_map:
        return True

    if cell in level.doors:
        door = level.doors[cell]
        return door.open_progress < 0.8

    if cell == level.terminal_pos:
        return True

    return False
