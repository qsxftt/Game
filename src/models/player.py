'''Модель игрока'''

from math import cos, pi, sin

from src.models.weapon import Pistol, Shotgun
from src.systems.collision_system import is_wall
from src.systems.door_system import open_door


class Player:
    '''Игрок: позиция, здоровье, угол камеры и текущее оружие'''

    def __init__(self, x, y):
        '''Создает игрока в переданных координатах мира

        Args:
            x: начальная мировая координата по горизонтали
            y: начальная мировая координата по вертикали
        '''
        self.x = x
        self.y = y
        self.max_health = 100
        self.health = self.max_health
        self.angle = 0
        self.speed = 5
        self.radius = 15
        self.cooldown = 0
        self.delay = 20

        self.weapons = [Pistol(), Shotgun()]
        self.weapon_index = 0
        self.weapon = self.weapons[self.weapon_index]

    def can_move(self, x, y, level):
        '''Проверяет возможность перемещения с учетом радиуса игрока

        Args:
            x: проверяемая мировая координата по горизонтали
            y: проверяемая мировая координата по вертикали
            level: текущий уровень

        Returns:
            True, если новая позиция свободна
        '''
        return (
            not is_wall(x + self.radius, y, level)
            and not is_wall(x, y + self.radius, level)
            and not is_wall(x - self.radius, y, level)
            and not is_wall(x, y - self.radius, level)
        )

    def set_start_pos(self, x, y):
        '''Перемещает игрока в стартовую позицию нового сектора

        Args:
            x: новая мировая координата по горизонтали
            y: новая мировая координата по вертикали
        '''
        self.x = x
        self.y = y

    def switch_weapon(self):
        '''Переключает оружие, если игрок не стреляет и не перезаряжается'''
        if self.weapon.shoot_cooldown > 0 or self.weapon.reload_cooldown > 0:
            return False

        self.weapon_index = (self.weapon_index + 1) % len(self.weapons)
        self.weapon = self.weapons[self.weapon_index]

        return True

    def update(self, actions, level):
        '''Обрабатывает действия игрока за один кадр

        Args:
            actions: словарь активных игровых действий
            level: текущий уровень

        Returns:
            Флаги выполненного выстрела и начатой перезарядки
        '''
        sin_a = sin(self.angle)
        cos_a = cos(self.angle)

        shot_fired = False
        reload_started = False

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
        if actions['Q']:
            self.switch_weapon()

        self.angle %= 2 * pi

        if actions['E'] and self.cooldown == 0:
            if open_door(self, level):
                self.cooldown = self.delay

        if actions['space']:
            if self.weapon.shoot():
                shot_fired = True

        if actions['R']:
            if self.weapon.reload():
                reload_started = True

        if self.can_move(self.x + dx, self.y, level):
            self.x += dx

        if self.can_move(self.x, self.y + dy, level):
            self.y += dy

        return shot_fired, reload_started
