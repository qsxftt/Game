"""Система управления дверями."""

from src.systems.map_system import get_cell, get_front_cell


def get_door(x, y, level):
    """Возвращает дверь в клетке, содержащей координаты x/y."""
    cell = get_cell(x, y)
    return level.doors.get(cell)


def open_door(player, level):
    """Пытается открыть дверь в клетке перед игроком."""
    cell = get_front_cell(player)

    if cell in level.doors:
        return level.doors[cell].open()

    return False

def open_door_at_cell(cell, level):
    if cell in level.doors:
        return level.doors[cell].open()

    return False

def update_doors(level):
    """Обновляет состояние всех дверей текущего уровня."""
    for door in level.doors.values():
        door.update()
