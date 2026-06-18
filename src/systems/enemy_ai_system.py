"""AI-поведение врагов: выбор цели, путь и следующая точка движения."""

from src.systems.map_system import grid_to_world, world_to_grid
from src.systems.path_system import find_path
from src.systems.visibility_system import get_depth, is_visible


def can_see_player(enemy, player, level):
    """Проверяет, видит ли враг игрока с учетом дистанции и препятствий."""
    if get_depth(enemy, player) > enemy.vision_distance:
        return False

    return is_visible(enemy, player, level)


def update_path(enemy, target_cell, level):
    """Пересчитывает A* путь врага до целевой клетки."""
    start_cell = world_to_grid(enemy.x, enemy.y)
    enemy.path = find_path(level.text_map, start_cell, target_cell)
    enemy.path_update_cooldown = enemy.path_update_delay


def get_target_cell(enemy, player, level):
    """Выбирает клетку, к которой враг должен двигаться сейчас."""
    if can_see_player(enemy, player, level):
        enemy.last_seen_player_cell = world_to_grid(player.x, player.y)
        enemy.state = 'chase'
        return enemy.last_seen_player_cell

    if enemy.last_seen_player_cell:
        enemy.state = 'search'
        return enemy.last_seen_player_cell

    enemy.state = 'idle'
    return None


def trim_path(enemy):
    """Удаляет из пути уже пройденные клетки."""
    current_cell = world_to_grid(enemy.x, enemy.y)

    while enemy.path and enemy.path[0] == current_cell:
        enemy.path.pop(0)


def get_next_path_point(enemy):
    """Возвращает мировые координаты следующей точки пути."""
    trim_path(enemy)

    if not enemy.path:
        return None

    return grid_to_world(*enemy.path[0])
