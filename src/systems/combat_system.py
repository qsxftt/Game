"""Система боя."""


def player_shoot(player, enemies):
    """Обрабатывает попадание выстрела игрока по ближайшему врагу в прицеле."""
    target = None
    max_depth = float('inf')

    for enemy in enemies:
        if enemy.health <= 0:
            continue

        if enemy.near_crosshair(player):
            depth = enemy.get_depth(player)

            if depth < max_depth:
                max_depth = depth
                target = enemy

    if target:
        target.take_damage(player.weapon.damage)
        return True

    return False
