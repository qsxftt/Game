'''Модели врагов'''

from src.systems.collision_system import is_wall
from src.systems.enemy_ai_system import (
    get_next_path_point,
    get_target_cell,
    open_next_door,
    update_enemy_state,
    update_path,
)
from src.systems.visibility_system import get_depth


class Enemy:
    '''Базовый враг с боевым состоянием и параметрами навигации'''

    def __init__(self, x, y):
        '''Создает базового врага в координатах карты'''
        self.x = x
        self.y = y
        self.health = 0
        self.damage = 0
        self.alive = True
        self.hitbox_radius = 0
        self.speed = 0
        self.attack_delay = 0
        self.attack_cooldown = 0
        self.attack_distance = 0
        self.frame_walk_cooldown = 0
        self.frame_walk_delay = 0

        self.state = 'idle'
        self.path = []
        self.path_update_delay = 30
        self.path_update_cooldown = 0
        self.vision_distance = 500
        self.last_seen_player_cell = None

        self.idle_target_cell = None
        self.idle_wait_cooldown = 0
        self.idle_wait_delay = 60

        self.score_value = 0
        self.score_awarded = False

    def take_damage(self, damage):
        '''Наносит врагу урон и помечает его мертвым при нуле здоровья'''
        self.health -= damage

        if self.health <= 0:
            self.health = 0
            self.alive = False

    def can_move(self, x, y, level):
        '''Проверяет, может ли враг занять указанную позицию'''
        return (
            not is_wall(x + 15, y, level)
            and not is_wall(x, y + 15, level)
            and not is_wall(x - 15, y, level)
            and not is_wall(x, y - 15, level)
        )

    def move(self, player, level):
        '''Двигает врага к игроку или атакует при достаточной близости'''
        if self.state == 'attack':
            return False

        target_cell = get_target_cell(self, player, level)

        if not target_cell:
            return False

        if self.path_update_cooldown == 0:
            update_path(self, target_cell, level)

        open_next_door(self, level)

        target_point = get_next_path_point(self, level)

        if target_point is None:
            if self.state == 'search':
                self.last_seen_player_cell = None

            if self.state == 'idle':
                self.idle_target_cell = None
                self.idle_wait_cooldown = self.idle_wait_delay

            return False

        target_x, target_y = target_point

        return self.move_to_point(target_x, target_y, level)

    def move_to_point(self, target_x, target_y, level):
        '''Перемещает врага к мировой точке с учетом коллизий'''
        dx = target_x - self.x
        dy = target_y - self.y

        move_depth = (dx**2 + dy**2) ** 0.5

        if move_depth == 0:
            return False

        dx = dx / move_depth * self.speed
        dy = dy / move_depth * self.speed

        if self.can_move(self.x + dx, self.y, level):
            self.x += dx

        if self.can_move(self.x, self.y + dy, level):
            self.y += dy

        return True

    def try_attack(self, player):
        '''Пытается атаковать игрока, если тот находится достаточно близко'''
        depth = get_depth(self, player)

        if depth > self.attack_distance:
            return False

        self.attack(player)
        return True

    def attack(self, player):
        '''Наносит урон игроку, если cooldown атаки закончился'''
        if self.attack_cooldown > 0:
            return False

        player.health -= self.damage
        self.attack_cooldown = self.attack_delay

        return True

    def update(self, player, level):
        '''Обновляет cooldown'ы и поведение врага за один кадр'''
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

        if self.idle_wait_cooldown > 0:
            self.idle_wait_cooldown -= 1

        health_before = player.health

        update_enemy_state(self, player, level)

        self.move(player, level)

        return player.health < health_before


class Dwarf(Enemy):
    '''Слабый зараженный ученый'''

    def __init__(self, x, y):
        '''Создает зараженного ученого'''
        super().__init__(x, y)
        self.health = 100
        self.damage = 10
        self.speed = 2
        self.attack_distance = 100
        self.attack_delay = 50
        self.frame_walk_delay = 50
        self.hitbox_radius = 40

        self.score_value = 100


class Dwarf2(Enemy):
    '''Сильный аномальный монстр'''

    def __init__(self, x, y):
        '''Создает аномального монстра'''
        super().__init__(x, y)
        self.health = 200
        self.damage = 30
        self.speed = 3
        self.attack_distance = 100
        self.attack_delay = 50
        self.frame_walk_delay = 50
        self.hitbox_radius = 40

        self.score_value = 200
