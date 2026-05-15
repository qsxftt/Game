import pygame
from config import *


class Weapon:
    def __init__(self):
        self.damage = 0
        self.ammo = 0
        self.magazine_size = 0

        self.shot_delay = 0
        self.shot_cooldown = 0

        self.reload_delay = 0
        self.reload_cooldown = 0

        self.texture = None

    def update(self):
        if self.shot_cooldown > 0:
            self.shot_cooldown -= 1

        if self.reload_cooldown > 0:
            self.reload_cooldown -= 1
            if self.reload_cooldown == 0:
                self.ammo = self.magazine_size

    def can_shoot(self):
        if self.ammo > 0 and self.shot_cooldown == 0 and self.reload_cooldown == 0:
            return True
        else:
            return False
        
    def shoot(self):
        if not self.can_shoot():
            return False
        
        self.ammo -= 1
        self.shot_cooldown = self.shot_delay

        return True
    
    def reload(self):
        if self.ammo == self.magazine_size:
            return False
        
        if self.reload_cooldown > 0:
            return False
        
        self.reload_cooldown = self.reload_delay

        return True
    
    def draw(self, screen):
        x_size = 100
        y_size = 30
        x = WIDTH - x_size - 20
        y = HEIGHT - y_size - 20

        pygame.draw.rect(screen, RED, (x, y, x_size, y_size))


class Pistol(Weapon):
    def __init__(self):
        super().__init__()
        self.damage = 15
        self.ammo = 10
        self.magazine_size = 10
        self.shot_delay = 20
        self.reload_delay = 60
        self.texture = None