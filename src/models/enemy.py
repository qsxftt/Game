"""Модели врагов."""

import pygame

from src.core.config import (
    ENEMY12_TEXTURE,
    ENEMY1_TEXTURE,
    RED,
)
from src.systems.collision_system import is_wall
from src.systems.enemy_ai_system import get_next_path_point, get_target_cell, update_path


class Enemy:
    """Базовый враг.

    Временно содержит часть логики видимости и расчета screen_x. Позже это можно
    вынести в VisibilitySystem, чтобы модель меньше зависела от ray casting.
    """

    def __init__(self, x, y):
        """Создает базового врага в координатах карты."""
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

        self.state = 'idle'
        self.path = []
        self.path_update_delay = 30
        self.path_update_cooldown = 0
        self.vision_distance = 500
        self.last_seen_player_cell = None

    def take_damage(self, damage):
        """Наносит врагу урон и помечает его мертвым при нуле здоровья."""
        self.health -= damage

        if self.health <= 0:
            self.health = 0
            self.alive = False

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
        
        target_cell = get_target_cell(self, player, level)

        if not target_cell:
            return False
        
        if self.path_update_cooldown == 0:
            update_path(self, target_cell, level)

        target_point = get_next_path_point(self)

        if target_point is None:
            return False
        
        target_x, target_y = target_point
        
        dx = target_x - self.x
        dy = target_y - self.y

        move_depth = (dx ** 2 + dy ** 2) ** 0.5

        if move_depth == 0:
            return False

        dx = dx / move_depth * self.speed
        dy = dy / move_depth * self.speed

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

        if self.path_update_cooldown > 0:
            self.path_update_cooldown -= 1

        self.move(player, level)

    def draw_debug(self, screen):
        """Рисует debug-кружок врага на мини-карте."""
        if not self.alive:
            return False

        pygame.draw.circle(screen, RED, (self.x, self.y), 20)


class Dwarf(Enemy):
    """Конкретный тип врага с параметрами и текстурами."""

    def __init__(self, x, y):
        """Создает врага Dwarf с заданными характеристиками."""
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
