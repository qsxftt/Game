import pygame
from src.core.config import *

class WeaponRender:
    def get_frame(self, weapon, texture, status=None):
        frame_count = weapon.frame_count
        frame_width = texture.get_width() // frame_count
        frame_height = texture.get_height()

        if status == 'shoot':
            frame_index = round((1 - weapon.shoot_cooldown / weapon.shoot_delay) * (frame_count - 1))
        elif status == 'reload':
            frame_index = round((1 - weapon.reload_cooldown / weapon.reload_delay) * (frame_count - 1))
        else:
            frame_index = 0

        x = frame_width * frame_index
        frame = texture.subsurface(x, 0, frame_width, frame_height)

        return frame, frame_width, frame_height

    def draw(self, screen, weapon):
        if weapon.shoot_cooldown > 0:
            frame, frame_width, frame_height = self.get_frame(weapon, weapon.texture, 'shoot')
        elif weapon.reload_cooldown > 0:
            frame, frame_width, frame_height = self.get_frame(weapon, weapon.texture_reload, 'reload')
        else:
            frame, frame_width, frame_height = self.get_frame(weapon, weapon.texture)

        screen_width = (frame_width * HEIGHT_HALF / frame_height)
        frame = pygame.transform.scale(frame, (screen_width, HEIGHT_HALF))

        screen.blit(frame, (WIDTH - screen_width, HEIGHT_HALF))