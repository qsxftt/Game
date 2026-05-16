import pygame
from math import *
from config import *
from weapon import Pistol
from func import is_wall, open_door

class Player:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.health = 100
        self.angle = 0
        self.speed = 5
        self.radius = PLAYER_RADIUS
        self.cooldown = 0
        self.delay = 20
        self.weapon = Pistol()

    def can_move(self, x, y):
        return (
            not is_wall(x + self.radius, y)
            and not is_wall(x, y + self.radius)
            and not is_wall(x - self.radius, y)
            and not is_wall(x, y - self.radius)
        )

    def move(self):
        keys = pygame.key.get_pressed()
        sin_a = sin(self.angle)
        cos_a = cos(self.angle)
        self.weapon.update()

        shot_fired = False

        if self.cooldown > 0:
            self.cooldown -= 1

        dx = 0
        dy = 0

        if keys[pygame.K_w]:
            dx += cos_a * self.speed
            dy += sin_a * self.speed
        if keys[pygame.K_s]:
            dx -= cos_a * self.speed
            dy -= sin_a * self.speed
        if keys[pygame.K_a]:
            dx += sin_a * self.speed
            dy -= cos_a * self.speed
        if keys[pygame.K_d]:
            dx -= sin_a * self.speed
            dy += cos_a * self.speed
        if keys[pygame.K_LEFT]:
            self.angle -= 0.01 * self.speed 
        if keys[pygame.K_RIGHT]:
            self.angle += 0.01 * self.speed

        self.angle %= 2 * pi

        if keys[pygame.K_e] and self.cooldown == 0:
            if open_door(self):
                self.cooldown = self.delay

        if keys[pygame.K_SPACE]:
            if self.weapon.shoot():
                shot_fired = True

        if keys[pygame.K_r]:
            self.weapon.reload()
        
        if self.can_move(self.x + dx, self.y):
                self.x += dx

        if self.can_move(self.x, self.y + dy):
            self.y += dy
        
        return shot_fired
