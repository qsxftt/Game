"""Запросы к клеточной карте и общие утилиты для координат."""

from math import cos, sin

from src.core.config import block_size


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


def get_block_type(x, y, level):
    """Возвращает тип блока в точке: wall, door, terminal или None."""
    cell = get_cell(x, y)

    if cell in level.block_map:
        return 'wall'

    if cell in level.doors and level.doors[cell].open_progress < 1.0:
        return 'door'

    if cell == level.terminal_pos:
        return 'terminal'

    return None


def get_sprite_sorted(pickups, enemies, player):
    """Возвращает pickups и enemies, отсортированные от дальних к ближним."""
    sprites = pickups + enemies
    return sorted(sprites, key=lambda sprite: sprite.get_depth(player), reverse=True)
