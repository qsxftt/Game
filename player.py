import pygame
from math import *
from config import *

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

        if keys[pygame.K_w]:
            self.x += cos_a * self.speed
            self.y += sin_a * self.speed
        if keys[pygame.K_s]:
            self.x -= cos_a * self.speed
            self.y -= sin_a * self.speed
        if keys[pygame.K_a]:
            self.x += sin_a * self.speed
            self.y -= cos_a * self.speed
        if keys[pygame.K_d]:
            self.x -= sin_a * self.speed
            self.y += cos_a * self.speed
        if keys[pygame.K_LEFT]:
            self.angle -= 0.02 * self.speed 
        if keys[pygame.K_RIGHT]:
            self.angle += 0.02 * self.speed