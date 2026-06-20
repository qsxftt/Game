"""Модели подбираемых ресурсов."""

from src.core.config import (
    AMMO_TEXTURE,
    MEDKIT_TEXTURE,
)
from src.systems.visibility_system import get_depth


class Pickup:
    """Базовый ресурс на карте: аптечка, патроны или будущий pickup."""

    def __init__(self, x, y):
        """Создает ресурс в координатах мира."""
        self.x = x
        self.y = y
        self.amount = 0
        self.is_pickedup = False
        self.frame_count = 0
        self.animation_speed = 0
        self.animation_cooldown = 0
        self.pickup_radius = 0
        self.type = None
        self.texture = None

    def update(self, player):
        """Обновляет анимацию и проверяет подбор игроком."""
        if self.animation_cooldown > 0:
            self.animation_cooldown -= 1

            if self.animation_cooldown == 0:
                self.animation_cooldown = self.animation_speed

        self.pickup_item(player)

    def pickup_item(self, player):
        """Применяет эффект ресурса, если игрок подошел достаточно близко."""
        if self.is_pickedup:
            return False

        depth = get_depth(self, player)

        if depth <= self.pickup_radius:
            if self.type == 'medkit':
                player.health = min(player.max_health, player.health + self.amount)
            elif self.type == 'ammo':
                player.weapon.reserve_ammo += self.amount

            self.is_pickedup = True


class MedKit(Pickup):
    """Аптечка, восстанавливающая здоровье игрока."""

    def __init__(self, x, y):
        """Создает аптечку."""
        super().__init__(x, y)
        self.amount = 10
        self.frame_count = 1
        self.animation_speed = 20
        self.pickup_radius = 50
        self.type = 'medkit'
        self.texture = MEDKIT_TEXTURE


class Ammo(Pickup):
    """Пачка патронов, пополняющая запас оружия."""

    def __init__(self, x, y):
        """Создает пачку патронов."""
        super().__init__(x, y)
        self.amount = 10
        self.frame_count = 1
        self.animation_speed = 20
        self.pickup_radius = 50
        self.type = 'ammo'
        self.texture = AMMO_TEXTURE
