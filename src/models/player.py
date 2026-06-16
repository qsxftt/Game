"""Модель игрока."""

from math import cos, pi, sin

from src.core.config import PLAYER_RADIUS
from src.models.weapon import Pistol
from src.systems.collision_system import is_wall
from src.systems.door_system import open_door


class Player:
    """Игрок: позиция, здоровье, угол камеры и текущее оружие."""

    def __init__(self, x, y):
        """Создает игрока в переданных координатах мира."""
        self.x = x
        self.y = y
        self.health = 100
        self.angle = 0
        self.speed = 5
        self.radius = PLAYER_RADIUS
        self.cooldown = 0
        self.delay = 20
        self.weapon = Pistol()

    def can_move(self, x, y, level):
        """Проверяет, может ли игрок занять позицию с учетом радиуса."""
        return (
            not is_wall(x + self.radius, y, level)
            and not is_wall(x, y + self.radius, level)
            and not is_wall(x - self.radius, y, level)
            and not is_wall(x, y - self.radius, level)
        )

    def update(self, actions, level):
        """Обрабатывает действия игрока за кадр и возвращает факт выстрела."""
        sin_a = sin(self.angle)
        cos_a = cos(self.angle)

        shot_fired = False

        if self.cooldown > 0:
            self.cooldown -= 1

        dx = 0
        dy = 0

        if actions['W']:
            dx += cos_a * self.speed
            dy += sin_a * self.speed
        if actions['S']:
            dx -= cos_a * self.speed
            dy -= sin_a * self.speed
        if actions['A']:
            dx += sin_a * self.speed
            dy -= cos_a * self.speed
        if actions['D']:
            dx -= sin_a * self.speed
            dy += cos_a * self.speed
        if actions['left']:
            self.angle -= 0.01 * self.speed
        if actions['right']:
            self.angle += 0.01 * self.speed

        self.angle %= 2 * pi

        if actions['E'] and self.cooldown == 0:
            if open_door(self, level):
                self.cooldown = self.delay

        if actions['space']:
            if self.weapon.shoot():
                shot_fired = True

        if actions['R']:
            self.weapon.reload()

        if self.can_move(self.x + dx, self.y, level):
            self.x += dx

        if self.can_move(self.x, self.y + dy, level):
            self.y += dy

        return shot_fired
