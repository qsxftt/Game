"""Система боя."""

from src.core.config import WIDTH_HALF
from src.systems.visibility_system import get_depth, get_screen_x, is_in_fov, is_visible


def player_shoot(player, enemies, level):
    """Обрабатывает попадание выстрела игрока по ближайшему врагу в прицеле."""
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
        return True

    return False


def enemy_near_crosshair(enemy, player, level):
    """Проверяет, находится ли враг под прицелом игрока."""
    if not enemy.alive:
        return False

    if not is_visible(enemy, player, level):
        return False

    if not is_in_fov(enemy, player):
        return False

    screen_x = get_screen_x(enemy, player)

    return abs(screen_x - WIDTH_HALF) < enemy.radius
