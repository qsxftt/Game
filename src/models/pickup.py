"""Модели подбираемых ресурсов."""

from math import atan2, pi

from src.core.config import (
    AMMO_TEXTURE,
    DELTA_RAY,
    HALF_FOV,
    MEDKIT_TEXTURE,
    SCALE,
    WIDTH_HALF,
)
from src.views.raycast_renderer import cast_single_ray


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

    def get_depth(self, player):
        """Возвращает расстояние от ресурса до игрока."""
        dx = player.x - self.x
        dy = player.y - self.y

        return (dx ** 2 + dy ** 2) ** 0.5

    def get_angle(self, player):
        """Возвращает угол от игрока к ресурсу."""
        dx = self.x - player.x
        dy = self.y - player.y

        return atan2(dy, dx)

    def get_delta_angle(self, player):
        """Возвращает разницу между направлением взгляда игрока и ресурсом."""
        angle = self.get_angle(player)
        delta_angle = angle - player.angle

        while delta_angle > pi:
            delta_angle -= 2 * pi

        while delta_angle < -pi:
            delta_angle += 2 * pi

        return delta_angle

    def is_in_fov(self, player):
        """Проверяет, попадает ли ресурс в поле зрения игрока."""
        delta_angle = self.get_delta_angle(player)

        return abs(delta_angle) < HALF_FOV

    def is_visible(self, player, level):
        """Проверяет, не перекрыт ли ресурс стеной, дверью или терминалом."""
        angle = self.get_angle(player)
        hit_x, hit_y, wall_depth, side, block_type = cast_single_ray(player, angle, level)
        pickup_depth = self.get_depth(player)

        return pickup_depth < wall_depth

    def get_screen_x(self, player):
        """Возвращает X-координату ресурса на экране."""
        delta_angle = self.get_delta_angle(player)

        return WIDTH_HALF + delta_angle / DELTA_RAY * SCALE

    def pickup_item(self, player):
        """Применяет эффект ресурса, если игрок подошел достаточно близко."""
        if self.is_pickedup:
            return False

        depth = self.get_depth(player)

        if depth <= self.pickup_radius:
            if self.type == 'medkit':
                player.health = min(100, player.health + self.amount)
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
