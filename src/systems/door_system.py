"""Система управления дверями."""

from src.core.config import doors
from src.systems.map_system import get_cell, get_front_cell


def get_door(x, y):
    """Возвращает дверь в клетке, содержащей координаты x/y."""
    cell = get_cell(x, y)
    return doors.get(cell)


def open_door(player):
    """Пытается открыть дверь в клетке перед игроком."""
    cell = get_front_cell(player)

    if cell in doors:
        return doors[cell].open()

    return False


def update_doors():
    """Обновляет состояние всех дверей текущей карты."""
    for door in doors.values():
        door.update()
