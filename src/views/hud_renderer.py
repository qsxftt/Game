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

        minimap_surf = pygame.Surface((minimap_size, minimap_size))
        minimap_surf.fill((0, 0, 0))

        center_x = minimap_size // 2
        center_y = minimap_size // 2

        map_scale = cell_size / level.block_size
        max_dist = (self.minimap_radius + 1.5) * level.block_size

        # Стены двери терминал

        map_objects = [(level.block_map, (100, 100, 100)), (level.doors.keys(), (180, 150, 50))]

        if level.terminal_pos is not None:
            map_objects.append(([level.terminal_pos], (100, 100, 100)))

        for map_obj, color in map_objects:
            for obj_x, obj_y in map_obj:
                dx = obj_x - player.x
                dy = obj_y - player.y

                if abs(dx) < max_dist and abs(dy) < max_dist:
                    cell_x = round(center_x + dx * map_scale)
                    cell_y = round(center_y + dy * map_scale)

                    pygame.draw.rect(minimap_surf, color, (cell_x, cell_y, cell_size, cell_size))

        # Враги

        for enemy in enemies:
            if not enemy.alive or not is_visible(enemy, player, level):
                continue

            dx = enemy.x - player.x
            dy = enemy.y - player.y

            if abs(dx) < max_dist and abs(dy) < max_dist:
                enemy_x = round(center_x + dx * map_scale)
                enemy_y = round(center_y + dy * map_scale)

                pygame.draw.circle(minimap_surf, (255, 0, 0), (enemy_x, enemy_y), max(2, cell_size // 3))

        # Игрок

        direction_x = center_x + cos(player.angle) * cell_size
        direction_y = center_y + sin(player.angle) * cell_size
        
        pygame.draw.line(minimap_surf, (0, 255, 0), (center_x, center_y), (direction_x, direction_y), max(1, int(2 * ui_scale)))
        pygame.draw.circle(minimap_surf, (0, 255, 0), (center_x, center_y), max(2, cell_size // 3))

        screen.blit(minimap_surf, (x, y))

        blink_color = self.get_radar_border_color(player, level)

        pygame.draw.rect(screen, blink_color, (x, y, minimap_size, minimap_size), max(1, int(5 * ui_scale)))

    def get_radar_border_color(self, player, level):
        """Возвращает цвет рамки: белый или мигающий зелёный (при приближении к выходу)."""
        if level.terminal_pos is None:
            return (255, 255, 255) 

        term_x, term_y = level.terminal_pos
        term_x += level.block_size // 2
        term_y += level.block_size // 2

        distance = ((term_x - player.x) ** 2 + (term_y - player.y) ** 2) ** 0.5

        blink_interval = None
        if distance < 300:
            blink_interval = 150
        elif distance < 600:
            blink_interval = 300
        elif distance < 900:
            blink_interval = 600

        if blink_interval is not None:
            if (pygame.time.get_ticks() // blink_interval) % 2 == 0:
                return (0, 255, 0)

        return (255, 255, 255)

    def draw_crossfire(self, screen):
        """Рисует прицел в центре экрана."""
        size = 10
        pygame.draw.line(screen, WHITE, (WIDTH_HALF - size, HEIGHT_HALF), (WIDTH_HALF + size, HEIGHT_HALF), 2)
        pygame.draw.line(screen, WHITE, (WIDTH_HALF, HEIGHT_HALF - size), (WIDTH_HALF, HEIGHT_HALF + size), 2)
