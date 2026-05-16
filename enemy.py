import pygame
from config import *
from func import cast_single_ray, is_wall
from math import atan2, pi

class Enemy:
    def __init__(self, x, y):
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
        self.texture = None
        

    def get_depth(self, player):
        dx = player.x - self.x
        dy = player.y - self.y

        return (dx ** 2 + dy ** 2) ** 0.5
    
    def get_angle(self, player):
        dx = self.x - player.x
        dy = self.y - player.y

        return atan2(dy, dx)
    
    def get_delta_angle(self, player):
        angle = self.get_angle(player)
        delta_angle = angle - player.angle

        while delta_angle > pi:
            delta_angle -= 2 * pi
        
        while delta_angle < -pi:
            delta_angle += 2* pi

        return delta_angle

    def is_in_fov(self, player):
        delta_angle = self.get_delta_angle(player)

        return abs(delta_angle) < HALF_FOV
    
    def get_screen_x(self, player):
        delta_angle = self.get_delta_angle(player)

        return WIDTH_HALF + delta_angle / DELTA_RAY * SCALE
    
    def is_visible(self, player):
        angle = self.get_angle(player)
        hit_x, hit_y, wall_depth, side, block_type = cast_single_ray(player, angle)
        enemy_depth = self.get_depth(player)

        return enemy_depth < wall_depth
    
    def take_damage(self, damage):
        self.health -= damage

        if self.health <= 0:
            self.health = 0
            self.alive = False
    
    def near_crosshair(self, player):
        if not self.alive:
            return False
        
        if not self.is_visible(player):
            return False
        
        if not self.is_in_fov(player):
            return False
        
        screen_x = self.get_screen_x(player)

        return abs(screen_x - WIDTH_HALF) < self.radius
    
    def can_move(self, x, y):
        return (
            not is_wall(x + 15, y)
            and not is_wall(x, y + 15)
            and not is_wall(x - 15, y)
            and not is_wall(x, y - 15)
        )
    
    def move(self, player):
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
        
        if self.can_move(self.x + dx, self.y):
            self.x += dx

        if self.can_move(self.x, self.y + dy):
            self.y += dy

    def attack(self, player):
        if self.attack_cooldown > 0:
            return False
        
        player.health -= self.damage
        self.attack_cooldown = self.attack_delay

        return True

    def update(self, player):
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        self.move(player)
    
    def draw(self, screen, player):
        if not self.is_visible(player):
            return False

        if not self.alive:
            return False
        
        if not self.is_in_fov(player):
            return False
        
        depth = self.get_depth(player)
        screen_x = self.get_screen_x(player)
        enemy_height = int(block_size * SCREEN_DISTANCE / depth)
        frame_width = self.texture.get_width()
        frame_height = self.texture.get_height()
        enemy_width = (frame_width * enemy_height / frame_height)
        self.radius = enemy_width // 2

        frame = self.texture.subsurface(0, 0, frame_width, frame_height)
        frame = pygame.transform.scale(frame, (enemy_width, enemy_height))

        screen.blit(frame, (screen_x - enemy_width // 2, HEIGHT_HALF - enemy_height // 2))

    def draw_debug(self, screen):
        if not self.alive:
            return False
        
        pygame.draw.circle(screen, RED, (self.x, self.y), 20)
        

class Dwarf(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.health = 100
        self.damage = 10
        self.speed = 2
        self.attack_distance = 50
        self.attack_delay = 20
        self.texture = ENEMY1_TEXTURE

    

