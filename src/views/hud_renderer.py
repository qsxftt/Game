"""Renderer HUD'а игрока."""

import pygame

from src.core.config import GREEN, HEIGHT_HALF, WHITE, WIDTH_HALF


class HUDrender:
    """Рисует здоровье, патроны и прицел."""

    def __init__(self):
        """Создаёт шрифт HUD."""
        self.font = pygame.font.SysFont('Arial', 32)

    def draw_hud(self, screen, player):
        """Рисует здоровье игрока и патроны текущего оружия."""
        ammo_text = self.font.render(f'{player.weapon.ammo}/{player.weapon.reserve_ammo}', True, GREEN)
        hp_text = self.font.render(f'HP: {player.health}', True, GREEN)
        screen.blit(ammo_text, (20, 20))
        screen.blit(hp_text, (100, 20))

    def draw_crossfire(self, screen):
        """Рисует прицел в центре экрана."""
        size = 10
        pygame.draw.line(screen, WHITE, (WIDTH_HALF - size, HEIGHT_HALF), (WIDTH_HALF + size, HEIGHT_HALF), 2)
        pygame.draw.line(screen, WHITE, (WIDTH_HALF, HEIGHT_HALF - size), (WIDTH_HALF, HEIGHT_HALF + size), 2)
