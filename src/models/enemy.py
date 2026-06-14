"""Модели врагов."""

from math import atan2, pi

import pygame

from src.core.config import (
    DELTA_RAY,
    ENEMY12_TEXTURE,
    ENEMY1_TEXTURE,
    HALF_FOV,
    RED,
    SCALE,
    WIDTH_HALF,
)
from src.systems.collision_system import is_wall
from src.views.raycast_renderer import cast_single_ray


class Enemy:
    """Базовый враг.

    Временно содержит часть логики видимости и расчёта screen_x. Позже это
    можно вынести в VisibilitySystem, чтобы модель не зависела от renderer'а.
    """

    def __init__(self, x, y):
        """Создаёт базового врага в координатах карты."""
        self.x = x
        self.y = y
        self.health = 0
        self.damage = 0
        self.alive = True
        self.radius = 0
        self.speed = 0
        self.attack_delay = 0
        self.attack_cooldown = 0
        self.attack_distance = 0
        self.frame_walk_cooldown = 0
        self.frame_walk_delay = 0
        self.frame_walk_count = 0
        self.frame_attack_count = 0
        self.texture_walk = None
        self.texture_attack = None

    def get_depth(self, player):
        """Возвращает расстояние от врага до игрока."""
        dx = player.x - self.x
        dy = player.y - self.y

        return (dx ** 2 + dy ** 2) ** 0.5

    def get_angle(self, player):
        """Возвращает угол от игрока к врагу."""
        dx = self.x - player.x
        dy = self.y - player.y

        return atan2(dy, dx)

    def get_delta_angle(self, player):
        """Возвращает разницу между направлением взгляда игрока и врагом."""
        angle = self.get_angle(player)
        delta_angle = angle - player.angle

        while delta_angle > pi:
            delta_angle -= 2 * pi

        while delta_angle < -pi:
            delta_angle += 2 * pi

        return delta_angle

    def is_in_fov(self, player):
        """Проверяет, попадает ли враг в поле зрения игрока."""
        delta_angle = self.get_delta_angle(player)

        return abs(delta_angle) < HALF_FOV

    def get_screen_x(self, player):
        """Возвращает X-координату врага на экране."""
        delta_angle = self.get_delta_angle(player)

        return WIDTH_HALF + delta_angle / DELTA_RAY * SCALE

    def is_visible(self, player, level):
        """Проверяет, не перекрыт ли враг стеной или закрытой дверью."""
        angle = self.get_angle(player)
        hit_x, hit_y, wall_depth, side, block_type = cast_single_ray(player, angle, level)
        enemy_depth = self.get_depth(player)

        return enemy_depth < wall_depth

    def take_damage(self, damage):
        """Наносит врагу урон и помечает его мёртвым при нуле здоровья."""
        self.health -= damage

        if self.health <= 0:
            self.health = 0
            self.alive = False

    def near_crosshair(self, player, level):
        """Проверяет, находится ли враг достаточно близко к прицелу."""
        if not self.alive:
            return False

        if not self.is_visible(player, level):
            return False

        if not self.is_in_fov(player):
            return False

        screen_x = self.get_screen_x(player)

        return abs(screen_x - WIDTH_HALF) < self.radius

    def can_move(self, x, y, level):
        """Проверяет, может ли враг занять указанную позицию."""
        return (
            not is_wall(x + 15, y, level)
            and not is_wall(x, y + 15, level)
            and not is_wall(x - 15, y, level)
            and not is_wall(x, y - 15, level)
        )

    def move(self, player, level):
        """Двигает врага к игроку или атакует при достаточной близости."""
        dx = player.x - self.x
        dy = player.y - self.y

        depth = (dx ** 2 + dy ** 2) ** 0.5

        if depth == 0:
            return False

        if depth <= self.attack_distance:
            self.attack(player)
            return False

        dx = dx / depth * self.speed
        dy = dy / depth * self.speed

        if self.can_move(self.x + dx, self.y, level):
            self.x += dx

        if self.can_move(self.x, self.y + dy, level):
            self.y += dy

    def attack(self, player):
        """Наносит урон игроку, если cooldown атаки закончился."""
        if self.attack_cooldown > 0:
            return False

        player.health -= self.damage
        self.attack_cooldown = self.attack_delay

        return True

    def update(self, player, level):
        """Обновляет cooldown'ы и поведение врага за один кадр."""
        if not self.alive:
            return False

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        if self.frame_walk_cooldown > 0:
            self.frame_walk_cooldown -= 1

        if self.frame_walk_cooldown == 0:
            self.frame_walk_cooldown = self.frame_walk_delay

        self.move(player, level)

    def draw_debug(self, screen):
        """Рисует debug-кружок врага на мини-карте."""
        if not self.alive:
            return False

        pygame.draw.circle(screen, RED, (self.x, self.y), 20)


class Dwarf(Enemy):
    """Конкретный тип врага с параметрами и текстурами."""

    def __init__(self, x, y):
        """Создаёт врага Dwarf с заданными характеристиками."""
        super().__init__(x, y)
        self.health = 100
        self.damage = 10
        self.speed = 2
        self.attack_distance = 100
        self.attack_delay = 50
        self.frame_attack_count = 8
        self.frame_walk_delay = 25
        self.frame_walk_count = 4
        self.texture_walk = ENEMY1_TEXTURE
        self.texture_attack = ENEMY12_TEXTURE
