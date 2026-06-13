"""Renderer спрайтовых объектов мира."""

import pygame

from src.core.config import HEIGHT_HALF, SCREEN_DISTANCE, block_size


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
            frame_index = enemy.frame_walk_count - enemy.frame_walk_cooldown

        x = frame_width * frame_index
        frame = texture.subsurface(x, 0, frame_width, frame_height)

        return frame, frame_width, frame_height

    def draw(self, enemy, screen, player):
        """Рисует одного врага, если он жив, видим и находится в FOV."""
        if not enemy.is_visible(player):
            return False

        if not enemy.alive:
            return False

        if not enemy.is_in_fov(player):
            return False

        if enemy.attack_cooldown > 0:
            frame, frame_width, frame_height = self.get_frame(enemy, enemy.texture_attack, 'attack')
        else:
            frame, frame_width, frame_height = self.get_frame(enemy, enemy.texture_walk, 'walk')

        depth = enemy.get_depth(player)
        screen_x = enemy.get_screen_x(player)
        enemy_height = int(block_size * SCREEN_DISTANCE / depth) * 0.75
        enemy_width = (frame_width * enemy_height / frame_height)

        # Временный технический долг: combat использует enemy.radius для попадания.
        enemy.radius = enemy_width // 2

        frame = pygame.transform.scale(frame, (enemy_width, enemy_height))
        screen.blit(frame, (screen_x - enemy_width // 2, HEIGHT_HALF - enemy_height // 2))

    def draw_enemies(self, enemies, screen, player):
        """Рисует всех врагов текущего уровня."""
        for enemy in enemies:
            self.draw(enemy, screen, player)
