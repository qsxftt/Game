"""AI-поведение врагов: выбор цели, путь и следующая точка движения."""

from src.systems.map_system import grid_to_world, world_to_grid
from src.systems.path_system import find_path
from src.systems.visibility_system import get_depth, is_visible, has_line_of_sight
from src.systems.door_system import open_door_at_cell
from random import choice


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

def update_enemy_state(enemy, player, level):
    if enemy.try_attack(player):
        enemy.state = 'attack'
    elif can_see_player(enemy, player, level):
        enemy.state = 'chase'
        enemy.last_seen_player_cell = world_to_grid(player.x, player.y)
    elif enemy.last_seen_player_cell:
        enemy.state = 'search'
    else:
        enemy.state = 'idle'

def get_target_cell(enemy, player, level):
    if enemy.state == 'chase':
        return world_to_grid(player.x, player.y)

    if enemy.state == 'search':
        return enemy.last_seen_player_cell
    
    if enemy.state == 'idle':
        if enemy.idle_wait_cooldown > 0:
            return None

        if enemy.idle_target_cell is None:
            enemy.idle_target_cell = get_random_idle_cell(enemy, level)

        return enemy.idle_target_cell

    return None

def get_random_idle_cell(enemy, level):
    x, y = world_to_grid(enemy.x, enemy.y)

    near = [
        (x + 1, y),
        (x - 1, y),
        (x, y + 1),
        (x, y - 1),
    ]

    free_near = [cell for cell in near if level.text_map[cell[1]][cell[0]] == '.']

    if not free_near:
        return None

    return choice(free_near)

def get_next_path_point(enemy, level):
    """Возвращает мировые координаты следующей точки пути."""
    current_cell = world_to_grid(enemy.x, enemy.y)

    while enemy.path and enemy.path[0] == current_cell:
        enemy.path.pop(0)

    if not enemy.path:
        return None

    for cell in reversed(enemy.path[:4]):
        x, y = grid_to_world(*cell)

        if has_line_of_sight(enemy.x, enemy.y, x, y, level):
            return x, y
        
    return grid_to_world(*enemy.path[0])

def open_next_door(enemy, level):
    if not enemy.path:
        return False

    next_cell = enemy.path[0]
    door_cell = (next_cell[0] * level.block_size, next_cell[1] * level.block_size)

    if door_cell in level.doors:
        return open_door_at_cell(door_cell, level)

    return False
