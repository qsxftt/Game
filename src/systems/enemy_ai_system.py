from src.systems.map_system import grid_to_world, world_to_grid
from src.systems.path_system import find_path


def can_see_player(enemy, player, level):
    if enemy.get_depth(player) > enemy.vision_distance:
        return False

    return enemy.is_visible(player, level)

def update_path(enemy, target_cell, level):
    start_cell = world_to_grid(enemy.x, enemy.y)
    enemy.path = find_path(level.text_map, start_cell, target_cell)
    enemy.path_update_cooldown = enemy.path_update_delay

def get_target_cell(enemy, player, level):
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
    current_cell = world_to_grid(enemy.x, enemy.y)

    while enemy.path and enemy.path[0] == current_cell:
        enemy.path.pop(0)


def get_next_path_point(enemy):
    trim_path(enemy)

    if not enemy.path:
        return None

    return grid_to_world(*enemy.path[0])
