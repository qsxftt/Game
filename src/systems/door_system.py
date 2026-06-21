'''Система управления дверями'''

from src.systems.map_system import get_cell, get_front_cell


def get_door(x, y, level):
    '''Возвращает дверь в клетке, содержащей координаты x/y

    Args:
        x: мировая координата по горизонтали
        y: мировая координата по вертикали
        level: текущий уровень

    Returns:
        Найденная дверь или None
    '''
    cell = get_cell(x, y)
    return level.doors.get(cell)


def open_door(player, level):
    '''Пытается открыть дверь в клетке перед игроком

    Args:
        player: модель игрока
        level: текущий уровень

    Returns:
        True, если дверь начала открываться
    '''
    cell = get_front_cell(player)

    if cell in level.doors:
        return level.doors[cell].open()

    return False

def open_door_at_cell(cell, level):
    '''Пытается открыть дверь в указанной клетке карты

    Args:
        cell: координаты клетки двери
        level: текущий уровень

    Returns:
        True, если дверь начала открываться
    '''
    if cell in level.doors:
        return level.doors[cell].open()

    return False

def update_doors(level, player, enemies):
    '''Обновляет двери и не дает им закрыться на живых сущностях

    Args:
        level: текущий уровень
        player: модель игрока
        enemies: список врагов уровня
    '''
    occupied_cells = {get_cell(player.x, player.y)}
    for enemy in enemies:
        if enemy.alive:
            occupied_cells.add(get_cell(enemy.x, enemy.y))

    for cell, door in level.doors.items():
        door.update(cell in occupied_cells)
