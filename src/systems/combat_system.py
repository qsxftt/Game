'''Система боя'''

from math import cos, sin

from src.systems.visibility_system import get_depth, is_in_fov, is_visible


def player_shoot(player, enemies, level):
    '''Обрабатывает попадание выстрела игрока по ближайшему врагу в прицеле'''
    target = None
    max_depth = float('inf')

    for enemy in enemies:
        if enemy.health <= 0:
            continue

        if enemy_near_crosshair(enemy, player, level):
            depth = get_depth(enemy, player)

            if depth > player.weapon.attack_distance:
                continue

            if depth < max_depth:
                max_depth = depth
                target = enemy

    if target:
        target.take_damage(player.weapon.damage)
        return target

    return False


def enemy_near_crosshair(enemy, player, level):
    '''Проверяет, находится ли враг под прицелом игрока'''
    if not enemy.alive:
        return False

    if not is_in_fov(enemy, player):
        return False

    if not is_visible(enemy, player, level):
        return False

    dx = enemy.x - player.x
    dy = enemy.y - player.y

    direction_x = cos(player.angle)
    direction_y = sin(player.angle)

    forward_distance = dx * direction_x + dy * direction_y

    if forward_distance <= 0:
        return False

    side_distance = abs(dx * direction_y - dy * direction_x)

    return side_distance <= enemy.hitbox_radius
