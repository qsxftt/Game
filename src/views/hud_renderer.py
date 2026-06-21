'''Отрисовка HUD игрока и локальной мини-карты'''

from math import cos, sin

import pygame

from src.core.config import TOTAL_SECTORS
from src.models.game_state import GameState
from src.systems.visibility_system import is_visible

GREEN = (0, 255, 0)
DARK_GREEN = (8, 95, 18)
MIDDLE_GREEN = (15, 155, 35)
WHITE = (255, 255, 255)
RED = (255, 55, 55)
ORANGE = (255, 155, 25)
PANEL_COLOR = (0, 8, 4, 185)


class HUDrender:
    '''Рисует основные показатели игрока и состояние сектора'''

    def __init__(self):
        '''Создаёт настройки и временное состояние интерфейса'''
        self.base_width = 1200
        self.base_height = 800
        self.minimap_radius = 5
        self.minimap_cell_size = 20

        self.legacy_font = pygame.font.SysFont('Arial', 32)
        self.font_scale = None
        self.large_font = None
        self.medium_font = None
        self.small_font = None
        self.message_font = None

        self.panel_cache = {}
        self.icon_cache = {}

        self.message = ''
        self.message_color = ORANGE
        self.message_end_time = 0
        self.hitmark_end_time = 0

        self.last_player = None
        self.last_health = None
        self.damage_start_time = 0
        self.damage_end_time = 0
        self.damage_duration = 220

    # ------------------------------------------------------------------
    # Общая отрисовка

    def draw(self, screen, state):
        '''Рисует весь HUD одним вызовом'''
        player = state.player
        level = state.current_level

        if player is None or level is None:
            return

        scale = self.get_scale(screen)
        self.update_fonts(scale)
        self.update_damage_effect(player)

        self.draw_damage_effect(screen)
        self.draw_health(screen, player, scale)
        self.draw_objective(screen, state, scale)
        self.draw_minimap(screen, player, state.enemies, level)
        self.draw_weapon(screen, player.weapon, scale)
        self.draw_crosshair(screen, scale)
        self.draw_message(screen, scale)

    def get_scale(self, screen):
        '''Возвращает масштаб интерфейса для текущего разрешения'''
        return min(
            screen.get_width() / self.base_width, screen.get_height() / self.base_height
        )

    def update_fonts(self, scale):
        '''Обновляет шрифты при изменении масштаба HUD'''
        scale = round(scale, 2)

        if scale == self.font_scale:
            return

        self.font_scale = scale
        self.large_font = pygame.font.SysFont(
            'Arial', max(18, int(42 * scale)), bold=True
        )
        self.medium_font = pygame.font.SysFont(
            'Arial', max(12, int(19 * scale)), bold=True
        )
        self.small_font = pygame.font.SysFont(
            'Arial', max(10, int(13 * scale)), bold=True
        )
        self.message_font = pygame.font.SysFont(
            'Arial', max(14, int(24 * scale)), bold=True
        )
        self.panel_cache.clear()
        self.icon_cache.clear()

    # ------------------------------------------------------------------
    # Панели

    def draw_panel(self, screen, rect, scale, border_color=GREEN):
        '''Рисует полупрозрачную панель с угловыми отметками'''
        panel = self.panel_cache.get(rect.size)

        if panel is None:
            panel = pygame.Surface(rect.size, pygame.SRCALPHA)
            panel.fill(PANEL_COLOR)
            self.panel_cache[rect.size] = panel

        screen.blit(panel, rect.topleft)
        self.draw_frame(screen, rect, scale, border_color)

    def draw_frame(self, screen, rect, scale, color, corner_size=9):
        '''Рисует тонкую рамку и яркие углы вокруг прямоугольника'''
        pygame.draw.rect(screen, DARK_GREEN, rect, 1)

        corner = max(5, int(corner_size * scale))
        thickness = max(1, int(2 * scale))
        left, top, right, bottom = rect.left, rect.top, rect.right - 1, rect.bottom - 1

        lines = (
            ((left, top), (left + corner, top)),
            ((left, top), (left, top + corner)),
            ((right, top), (right - corner, top)),
            ((right, top), (right, top + corner)),
            ((left, bottom), (left + corner, bottom)),
            ((left, bottom), (left, bottom - corner)),
            ((right, bottom), (right - corner, bottom)),
            ((right, bottom), (right, bottom - corner)),
        )

        for start, end in lines:
            pygame.draw.line(screen, color, start, end, thickness)

    # ------------------------------------------------------------------
    # Здоровье

    def draw_health(self, screen, player, scale):
        '''Рисует здоровье игрока в левом нижнем углу'''
        width = int(340 * scale)
        height = int(115 * scale)
        margin = int(20 * scale)
        rect = pygame.Rect(margin, screen.get_height() - height - margin, width, height)
        self.draw_panel(screen, rect, scale)

        max_health = max(1, player.max_health)
        health = max(0, min(player.health, max_health))
        health_part = health / max_health

        if health_part > 0.5:
            health_color = GREEN
        elif health_part > 0.25:
            health_color = ORANGE
        else:
            health_color = RED

        cross_size = max(12, int(22 * scale))
        cross_x = rect.x + int(20 * scale)
        cross_y = rect.y + int(17 * scale)
        cross_width = max(3, cross_size // 3)
        pygame.draw.rect(
            screen,
            health_color,
            (cross_x, cross_y + cross_width, cross_size, cross_width),
        )
        pygame.draw.rect(
            screen,
            health_color,
            (cross_x + cross_width, cross_y, cross_width, cross_size),
        )

        title = self.medium_font.render('ЗДОРОВЬЕ', True, WHITE)
        value = self.medium_font.render(str(int(health)), True, health_color)
        text_x = cross_x + cross_size + int(16 * scale)
        text_y = cross_y - int(2 * scale)
        screen.blit(title, (text_x, text_y))
        screen.blit(value, (text_x + title.get_width() + int(10 * scale), text_y))

        bar_x = rect.x + int(20 * scale)
        bar_y = rect.y + int(53 * scale)
        bar_width = rect.width - int(40 * scale)
        bar_height = max(8, int(18 * scale))
        pygame.draw.rect(screen, (0, 28, 8), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(
            screen,
            health_color,
            (bar_x, bar_y, int(bar_width * health_part), bar_height),
        )

        for index in range(1, 20):
            segment_x = round(bar_x + bar_width * index / 20)
            pygame.draw.line(
                screen,
                (0, 0, 0),
                (segment_x, bar_y),
                (segment_x, bar_y + bar_height - 1),
                1,
            )

        pygame.draw.rect(screen, MIDDLE_GREEN, (bar_x, bar_y, bar_width, bar_height), 1)
        ruler_y = bar_y + bar_height + int(5 * scale)
        pygame.draw.line(
            screen, DARK_GREEN, (bar_x, ruler_y), (bar_x + bar_width, ruler_y), 1
        )

        for part in (0, 0.25, 0.5, 0.75, 1):
            tick_x = round(bar_x + bar_width * part)
            pygame.draw.line(
                screen,
                DARK_GREEN,
                (tick_x, ruler_y),
                (tick_x, ruler_y + int(5 * scale)),
                1,
            )
            label = self.small_font.render(
                str(round(max_health * part)), True, MIDDLE_GREEN
            )
            label_rect = label.get_rect(center=(tick_x, ruler_y + int(14 * scale)))
            screen.blit(label, label_rect)

    # ------------------------------------------------------------------
    # Сектор и задача

    def draw_objective(self, screen, state, scale):
        '''Рисует состояние сектора в левом верхнем углу'''
        margin = int(20 * scale)
        rect = pygame.Rect(margin, margin, int(390 * scale), int(108 * scale))
        self.draw_panel(screen, rect, scale)

        if state.game_mode == GameState.ENDLESS:
            sector_text = f'СЕКТОР {state.sector_index + 1}'
        else:
            sector_text = f'СЕКТОР {state.sector_index + 1}/{TOTAL_SECTORS}'

        enemies_left = sum(enemy.alive for enemy in state.enemies)
        sector = self.medium_font.render(sector_text, True, GREEN)
        threats = self.medium_font.render(
            f'УГРОЗЫ: {enemies_left}', True, RED if enemies_left else GREEN
        )

        if state.terminal_activated:
            task = 'ЗАДАЧА: ТЕРМИНАЛ АКТИВИРОВАН'
            task_color = GREEN
        elif state.sector_clean:
            task = 'ЗАДАЧА: НАЙТИ ТЕРМИНАЛ'
            task_color = GREEN
        else:
            task = 'ЗАДАЧА: ЗАЧИСТИТЬ СЕКТОР'
            task_color = ORANGE

        task_surface = self.small_font.render(task, True, task_color)
        text_x = rect.x + int(16 * scale)
        text_y = rect.y + int(13 * scale)
        spacing = int(27 * scale)
        screen.blit(sector, (text_x, text_y))
        screen.blit(threats, (text_x, text_y + spacing))
        screen.blit(task_surface, (text_x, text_y + spacing * 2 + int(3 * scale)))

    # ------------------------------------------------------------------
    # Оружие

    def get_minimap_rect(self, screen, scale):
        '''Возвращает прямоугольник мини-карты и размер одной клетки'''
        cell_size = max(1, int(self.minimap_cell_size * scale))
        size = (self.minimap_radius * 2 + 1) * cell_size
        margin = int(20 * scale)
        rect = pygame.Rect(screen.get_width() - size - margin, margin, size, size)
        return rect, cell_size

    def draw_weapon(self, screen, weapon, scale):
        '''Рисует выбранное оружие и количество патронов'''
        minimap_rect, _ = self.get_minimap_rect(screen, scale)
        margin = int(20 * scale)
        rect = pygame.Rect(
            minimap_rect.x,
            minimap_rect.bottom + margin,
            minimap_rect.width,
            int(120 * scale),
        )
        self.draw_panel(screen, rect, scale)

        name = self.medium_font.render(weapon.name.upper(), True, GREEN)
        screen.blit(name, (rect.x + int(15 * scale), rect.y + int(11 * scale)))

        ammo_color = RED if weapon.ammo == 0 else WHITE
        ammo = self.large_font.render(str(weapon.ammo), True, ammo_color)
        reserve = self.medium_font.render(
            f'/ {weapon.reserve_ammo}', True, MIDDLE_GREEN
        )
        ammo_x = rect.x + int(15 * scale)
        ammo_y = rect.y + int(39 * scale)
        screen.blit(ammo, (ammo_x, ammo_y))
        screen.blit(
            reserve,
            (ammo_x + ammo.get_width() + int(8 * scale), ammo_y + int(20 * scale)),
        )

        if weapon.reload_cooldown > 0 and weapon.reload_delay > 0:
            progress = 1 - weapon.reload_cooldown / weapon.reload_delay
            progress = max(0, min(progress, 1))
            bar_x = rect.x + int(15 * scale)
            bar_y = rect.bottom - int(14 * scale)
            bar_width = rect.width - int(30 * scale)
            bar_height = max(3, int(5 * scale))
            label = self.small_font.render('ПЕРЕЗАРЯДКА', True, ORANGE)
            screen.blit(label, (bar_x, bar_y - label.get_height() - int(3 * scale)))
            pygame.draw.rect(screen, (45, 25, 0), (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(
                screen,
                ORANGE,
                (bar_x, bar_y, int(bar_width * progress), bar_height),
            )

    # ------------------------------------------------------------------
    # Мини-карта

    def draw_minimap(self, screen, player, enemies, level):
        '''Рисует плавную локальную карту вокруг игрока'''
        scale = self.get_scale(screen)
        rect, cell_size = self.get_minimap_rect(screen, scale)
        minimap = pygame.Surface(rect.size)
        minimap.fill((0, 0, 0))

        center_x = rect.width // 2
        center_y = rect.height // 2
        map_scale = cell_size / level.block_size
        max_distance = (self.minimap_radius + 1.5) * level.block_size

        for line in range(self.minimap_radius * 2 + 2):
            position = line * cell_size
            pygame.draw.line(
                minimap, (0, 25, 5), (position, 0), (position, rect.height), 1
            )
            pygame.draw.line(
                minimap, (0, 25, 5), (0, position), (rect.width, position), 1
            )

        objects = [
            (level.block_map, (95, 100, 95)),
            (level.doors.keys(), (190, 155, 35)),
        ]
        if level.terminal_pos is not None:
            objects.append(((level.terminal_pos,), (95, 100, 95)))

        for positions, color in objects:
            for object_x, object_y in positions:
                dx = object_x - player.x
                dy = object_y - player.y

                if abs(dx) >= max_distance or abs(dy) >= max_distance:
                    continue

                cell_x = round(center_x + dx * map_scale)
                cell_y = round(center_y + dy * map_scale)
                pygame.draw.rect(minimap, color, (cell_x, cell_y, cell_size, cell_size))

        for enemy in enemies:
            if not enemy.alive:
                continue

            dx = enemy.x - player.x
            dy = enemy.y - player.y
            if abs(dx) >= max_distance or abs(dy) >= max_distance:
                continue
            if not is_visible(enemy, player, level):
                continue

            enemy_x = round(center_x + dx * map_scale)
            enemy_y = round(center_y + dy * map_scale)
            pygame.draw.circle(minimap, RED, (enemy_x, enemy_y), max(2, cell_size // 3))

        direction_x = center_x + cos(player.angle) * cell_size
        direction_y = center_y + sin(player.angle) * cell_size
        pygame.draw.line(
            minimap,
            GREEN,
            (center_x, center_y),
            (direction_x, direction_y),
            max(1, int(2 * scale)),
        )
        pygame.draw.circle(minimap, GREEN, (center_x, center_y), max(2, cell_size // 3))

        screen.blit(minimap, rect.topleft)
        self.draw_frame(
            screen, rect, scale, self.get_radar_color(player, level), corner_size=20
        )

    def get_radar_color(self, player, level):
        '''Возвращает цвет радара с учётом расстояния до терминала'''
        if level.terminal_pos is None:
            return DARK_GREEN

        terminal_x, terminal_y = level.terminal_pos
        terminal_x += level.block_size // 2
        terminal_y += level.block_size // 2
        distance = ((terminal_x - player.x) ** 2 + (terminal_y - player.y) ** 2) ** 0.5

        if distance < 300:
            interval = 150
        elif distance < 600:
            interval = 300
        elif distance < 900:
            interval = 600
        else:
            return DARK_GREEN

        if (pygame.time.get_ticks() // interval) % 2 == 0:
            return GREEN
        return DARK_GREEN

    # ------------------------------------------------------------------
    # Прицел и временные эффекты

    def draw_crosshair(self, screen, scale=None):
        '''Рисует прицел в центре текущего экрана'''
        if scale is None:
            scale = self.get_scale(screen)

        center_x = screen.get_width() // 2
        center_y = screen.get_height() // 2
        size = max(6, int(10 * scale))
        thickness = max(1, int(2 * scale))
        pygame.draw.line(
            screen,
            WHITE,
            (center_x - size, center_y),
            (center_x + size, center_y),
            thickness,
        )
        pygame.draw.line(
            screen,
            WHITE,
            (center_x, center_y - size),
            (center_x, center_y + size),
            thickness,
        )

        if pygame.time.get_ticks() >= self.hitmark_end_time:
            return

        gap = max(4, int(7 * scale))
        length = max(4, int(7 * scale))
        marks = (
            (
                (center_x - gap - length, center_y - gap - length),
                (center_x - gap, center_y - gap),
            ),
            (
                (center_x + gap, center_y - gap),
                (center_x + gap + length, center_y - gap - length),
            ),
            (
                (center_x - gap - length, center_y + gap + length),
                (center_x - gap, center_y + gap),
            ),
            (
                (center_x + gap, center_y + gap),
                (center_x + gap + length, center_y + gap + length),
            ),
        )
        for start, end in marks:
            pygame.draw.line(screen, RED, start, end, thickness)

    def trigger_hitmark(self, duration=160):
        '''Показывает отметку успешного попадания'''
        self.hitmark_end_time = pygame.time.get_ticks() + duration

    def show_message(self, text, duration=1800, color=ORANGE):
        '''Показывает временное сообщение рядом с прицелом'''
        self.message = text
        self.message_color = color
        self.message_end_time = pygame.time.get_ticks() + duration

    def draw_message(self, screen, scale):
        '''Рисует активное временное сообщение'''
        if not self.message or pygame.time.get_ticks() >= self.message_end_time:
            return

        text = self.message_font.render(self.message, True, self.message_color)
        shadow = self.message_font.render(self.message, True, (0, 0, 0))
        text_rect = text.get_rect(
            center=(
                screen.get_width() // 2,
                screen.get_height() // 2 + int(82 * scale),
            )
        )
        shadow_offset = max(1, int(2 * scale))
        screen.blit(shadow, (text_rect.x + shadow_offset, text_rect.y + shadow_offset))
        screen.blit(text, text_rect)

    def update_damage_effect(self, player):
        '''Запускает вспышку при уменьшении здоровья игрока'''
        if self.last_player is not player:
            self.last_player = player
            self.last_health = player.health
            return

        if player.health < self.last_health:
            now = pygame.time.get_ticks()
            self.damage_start_time = now
            self.damage_end_time = now + self.damage_duration

        self.last_health = player.health

    def draw_damage_effect(self, screen):
        '''Рисует затухающую красную вспышку поверх игрового мира'''
        now = pygame.time.get_ticks()
        if now >= self.damage_end_time:
            return

        progress = (now - self.damage_start_time) / self.damage_duration
        alpha = int(90 * (1 - progress))
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((255, 0, 0, alpha))
        screen.blit(overlay, (0, 0))
