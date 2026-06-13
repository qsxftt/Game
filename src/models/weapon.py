import pygame
from src.core.config import *


class Weapon:
    def __init__(self):
        self.damage = 0
        self.ammo = 0
        self.magazine_size = 0
        self.reserve_ammo = 0

        self.shoot_delay = 0
        self.shoot_cooldown = 0

        self.reload_delay = 0
        self.reload_cooldown = 0

        self.texture = None
        self.texture_reload = None
        self.frame_count = 0

    def update(self):
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        if self.reload_cooldown > 0:
            self.reload_cooldown -= 1
            if self.reload_cooldown == 0:
                need_ammo = self.magazine_size - self.ammo
                ammo_to = min(self.reserve_ammo, need_ammo)

                self.ammo += ammo_to
                self.reserve_ammo -= ammo_to

    def can_shoot(self):
        if self.ammo > 0 and self.shoot_cooldown == 0 and self.reload_cooldown == 0:
            return True
        else:
            return False
        
    def shoot(self):
        if not self.can_shoot():
            return False
        
        self.ammo -= 1
        self.shoot_cooldown = self.shoot_delay

        return True
    
    def reload(self):
        if self.ammo == self.magazine_size:
            return False
        
        if self.reload_cooldown > 0:
            return False
        
        if self.reserve_ammo <= 0:
            return False
        
        self.reload_cooldown = self.reload_delay

        return True


class Pistol(Weapon):
    def __init__(self):
        super().__init__()
        self.damage = 35
        self.ammo = 10
        self.magazine_size = 10
        self.shoot_delay = 20
        self.reload_delay = 60
        self.texture = PISTOL_TEXTURE
        self.frame_count = 5
        self.texture_reload = PISTOLR_TEXTURE
        self.reserve_ammo = 30