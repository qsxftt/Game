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

def update_doors(level, player, enemies):
    """Обновляет состояние всех дверей текущего уровня."""
    cell_obj = {get_cell(player.x, player.y)}
    for enemy in enemies:
        if enemy.alive:
            cell_obj.add(get_cell(enemy.x, enemy.y))

    for cell, door in level.doors.items():
        if cell in cell_obj:
            blocked = True
        else:
            blocked = False
            
        door.update(blocked)
