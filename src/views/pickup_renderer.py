import pygame
from src.core.config import *

class PickupRender:
    def get_frame(self, pickup):
        texture = pickup.texture
        frame_width = texture.get_width() / pickup.frame_count
        frame_height = texture.get_height()

        frame_index = round((1 - pickup.animation_cooldown / pickup.animation_speed) * (pickup.frame_count - 1))
        x = frame_index * frame_width

        frame = texture.subsurface(x, 0, frame_width, frame_height)

        return frame, frame_width, frame_height
    
    def draw(self, pickup, screen, player, level):
        if pickup.is_pickedup:
            return False
        
        if not pickup.is_visible(player, level):
            return False
        
        if not pickup.is_in_fov(player):
            return False
        
        frame, frame_width, frame_height = self.get_frame(pickup)

        depth = max(pickup.get_depth(player), 50)
        screen_x = pickup.get_screen_x(player)
        pickup_height = int(block_size * SCREEN_DISTANCE / depth * 0.5)
        pickup_width = int(frame_width * pickup_height / frame_height)

        frame = pygame.transform.scale(frame, (pickup_width, pickup_height))
        screen.blit(frame, (screen_x - pickup_width // 2, (HEIGHT - pickup_height // 2) * 0.53))

    def draw_pickups(self, pickups, screen, player, level):
        for pickup in pickups:
            self.draw(pickup, screen, player, level)
