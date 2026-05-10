import pygame
from math import *
from config import *
from func import is_wall

class Player:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.angle = 0
        self.speed = 5

    def move(self):
        keys = pygame.key.get_pressed()
        sin_a = sin(self.angle)
        cos_a = cos(self.angle)

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
        
        if not is_wall(self.x + dx, self.y):
                self.x += dx

        if not is_wall(self.x, self.y + dy):
            self.y += dy