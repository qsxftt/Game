"""Renderer спрайтовых объектов мира."""

import pygame

from src.core.config import HEIGHT_HALF, SCREEN_DISTANCE, block_size
from src.systems.visibility_system import get_depth, get_screen_x, is_in_fov, is_visible


class SpriteRender:
    """Рисует врагов как псевдо-3D спрайты."""

    def get_frame(self, enemy, texture, status='walk'):
        """Возвращает кадр анимации врага для указанного состояния."""
        if status == 'walk':
            frame_count = enemy.frame_walk_count
        elif status == 'attack':
            frame_count = enemy.frame_attack_count

        frame_width = texture.get_width() / frame_count
        frame_height = texture.get_height()

        if status == 'attack':
            frame_index = round((1 - enemy.attack_cooldown / enemy.attack_delay) * (frame_count - 1))
        elif status == 'walk':
            frame_index = round((1 - enemy.frame_walk_cooldown / enemy.frame_walk_delay) * (frame_count - 1))

        x = frame_width * frame_index
        frame = texture.subsurface(x, 0, frame_width, frame_height)

        return frame, frame_width, frame_height

    def draw(self, enemy, screen, player, level):
        """Рисует одного врага, если он жив, видим и находится в FOV."""
        if not enemy.alive:
            return False

        if not is_in_fov(enemy, player):
            return False
        
        if not is_visible(enemy, player, level):
            return False

        if enemy.attack_cooldown > 0:
            frame, frame_width, frame_height = self.get_frame(enemy, enemy.texture_attack, 'attack')
        else:
            frame, frame_width, frame_height = self.get_frame(enemy, enemy.texture_walk, 'walk')

        depth = max(get_depth(enemy, player), 50)
        screen_x = get_screen_x(enemy, player)
        enemy_height = int(block_size * SCREEN_DISTANCE / depth * 0.75)
        enemy_width = int(frame_width * enemy_height / frame_height)

        frame = pygame.transform.scale(frame, (enemy_width, enemy_height))
        screen.blit(frame, (screen_x - enemy_width // 2, HEIGHT_HALF - enemy_height // 2))
