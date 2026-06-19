"""Renderer HUD игрока."""

import pygame

from src.core.config import GREEN, HEIGHT_HALF, WHITE, WIDTH_HALF
from src.systems.map_system import world_to_grid
from src.systems.visibility_system import is_visible
from math import cos, sin


class HUDrender:
    """Рисует здоровье, патроны и прицел."""

    def __init__(self):
        """Создает шрифт HUD."""
        self.font = pygame.font.SysFont('Arial', 32)
        self.minimap_radius = 5
        self.minimap_base_cell_size = 20
        self.base_width = 1200
        self.base_height = 800

    def draw_hud(self, screen, player):
        """Рисует здоровье игрока и патроны текущего оружия."""
        ammo_text = self.font.render(f'{player.weapon.ammo}/{player.weapon.reserve_ammo}', True, GREEN)
        hp_text = self.font.render(f'HP: {player.health}', True, GREEN)
        weapon_text = self.font.render(player.weapon.name, True, GREEN)

        screen.blit(ammo_text, (20, 20))
        screen.blit(hp_text, (100, 20))
        screen.blit(weapon_text, (200, 20))

    def draw_minimap(self, screen, player, enemies, level):
        ui_scale = min(screen.get_width() / self.base_width, screen.get_height() / self.base_height)

        cell_size = int(self.minimap_base_cell_size * ui_scale)
        minimap_size = (self.minimap_radius * 2 + 1) * cell_size
        margin = int(20 * ui_scale)

        x = screen.get_width() - minimap_size - margin
        y = margin

        player_x, player_y = world_to_grid(player.x, player.y)

        pygame.draw.rect(screen, (0, 0, 0), (x, y, minimap_size, minimap_size))

        for offset_y in range(-self.minimap_radius, self.minimap_radius + 1):
            for offset_x in range(-self.minimap_radius, self.minimap_radius + 1):
                map_x = player_x + offset_x
                map_y = player_y + offset_y

                if not (0 <= map_y < len(level.text_map)):
                    continue
                if not (0 <= map_x < len(level.text_map[map_y])):
                    continue

                tile = level.text_map[map_y][map_x]

                if tile in ('W', 'T'):
                    color = (100, 100, 100)
                elif tile == 'D':
                    color = (180, 150, 40)
                else:
                    continue

                cell_x = x + (offset_x + self.minimap_radius) * cell_size
                cell_y = y + (offset_y + self.minimap_radius) * cell_size

                pygame.draw.rect(screen, color, (cell_x, cell_y, cell_size, cell_size))

        for enemy in enemies:
            if not enemy.alive:
                continue

            if not is_visible(enemy, player, level):
                continue

            enemy_x, enemy_y = world_to_grid(enemy.x, enemy.y)

            offset_x = enemy_x - player_x
            offset_y = enemy_y - player_y

            if abs(offset_x) > self.minimap_radius:
                continue
            if abs(offset_y) > self.minimap_radius:
                continue

            enemy_screen_x = x + (offset_x + self.minimap_radius) * cell_size + cell_size // 2
            enemy_screen_y = y + (offset_y + self.minimap_radius) * cell_size + cell_size // 2

            pygame.draw.circle(
                screen,
                (255, 0, 0),
                (enemy_screen_x, enemy_screen_y),
                max(2, cell_size // 3)
            )

        term_x, term_y = level.terminal_pos
        term_x += level.block_size // 2
        term_y += level.block_size // 2

        dx = term_x - player.x
        dy = term_y - player.y

        distance = (dx ** 2 + dy ** 2) ** 0.5

        blink_interval = None

        if distance < 300:
            blink_interval = 150
        elif distance < 600:
            blink_interval = 300
        elif distance < 900:
            blink_interval = 600

        blink_color = WHITE

        if blink_interval is not None:
            if (pygame.time.get_ticks() // blink_interval) % 2 == 0:
                blink_color = (0, 255, 0)



        player_screen_x = x + minimap_size // 2
        player_screen_y = y + minimap_size // 2

        direction_x = player_screen_x + cos(player.angle) * cell_size
        direction_y = player_screen_y + sin(player.angle) * cell_size
        
        pygame.draw.line(screen, (0, 255, 0), (player_screen_x, player_screen_y), (direction_x, direction_y), max(1, int(2 * ui_scale)))
        pygame.draw.circle(screen, (0, 255, 0), (player_screen_x, player_screen_y), max(2, cell_size // 2))

        pygame.draw.rect(screen, blink_color, (x, y, minimap_size, minimap_size), max(1, int(5 * ui_scale)))

    def draw_crossfire(self, screen):
        """Рисует прицел в центре экрана."""
        size = 10
        pygame.draw.line(screen, WHITE, (WIDTH_HALF - size, HEIGHT_HALF), (WIDTH_HALF + size, HEIGHT_HALF), 2)
        pygame.draw.line(screen, WHITE, (WIDTH_HALF, HEIGHT_HALF - size), (WIDTH_HALF, HEIGHT_HALF + size), 2)
