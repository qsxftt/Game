"""Renderer HUD игрока в стиле Sci-Fi."""

import pygame
from math import cos, sin
from src.core.config import WIDTH_HALF, HEIGHT_HALF
from src.systems.visibility_system import is_visible
from src.systems.combat_system import enemy_near_crosshair

# Основные цвета интерфейса
GREEN = (0, 255, 0)
DARK_GREEN = (10, 120, 10)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
ORANGE = (255, 150, 0)

class HUDrender:
    """Рисует здоровье, патроны, миникарту, задачи и временные уведомления."""

    def __init__(self):
        self.minimap_radius = 5
        self.minimap_base_cell_size = 20
        self.base_width = 1200
        self.base_height = 800
        
        # Кэш для масштабирования шрифтов
        self.cached_scale = 0.0
        self.font_large = None
        self.font_medium = None
        self.font_small = None
        self.font_message = None

        # Состояние временных уведомлений
        self.message = ""
        self.message_timer = 0

        # Состояние эффектов урона и попадания
        self.damage_flash_timer = 0
        self.hit_indicator_timer = 0
        self.last_health = 100

    def _init_fonts(self, ui_scale):
        """Динамически пересоздает шрифты при изменении масштаба разрешения."""
        if abs(self.cached_scale - ui_scale) > 0.01:
            self.cached_scale = ui_scale
            # Создаем сглаженные полужирные системные шрифты
            self.font_large = pygame.font.SysFont('Arial', int(42 * ui_scale), bold=True)
            self.font_medium = pygame.font.SysFont('Arial', int(18 * ui_scale), bold=True)
            self.font_small = pygame.font.SysFont('Arial', int(11 * ui_scale), bold=True)
            self.font_message = pygame.font.SysFont('Arial', int(24 * ui_scale), bold=True)

    def show_message(self, text, duration_frames=120):
        """Запускает показ временного сообщения по центру экрана."""
        self.message = text
        self.message_timer = duration_frames

    def trigger_hitmark(self):
        """Запускает отображение индикатора попадания (крестика на прицеле)."""
        self.hit_indicator_timer = 12

    def draw_hud(self, screen, state):
        """Главный метод отрисовки всего интерфейса."""
        player = state.player
        enemies = state.enemies
        level = state.current_level
        sector_index = state.sector_index

        # Рассчитываем масштаб интерфейса
        ui_scale = min(screen.get_width() / self.base_width, screen.get_height() / self.base_height)
        self._init_fonts(ui_scale)

        # Автоматически отслеживаем получение урона для эффекта красной вспышки
        if player.health < self.last_health:
            self.damage_flash_timer = 15 # вспышка на 15 кадров
        self.last_health = player.health

        # 1. Отрисовка основных панелей HUD
        self._draw_health_panel(screen, player, ui_scale)
        self._draw_objective_panel(screen, sector_index, enemies, ui_scale)
        self._draw_weapon_panel(screen, player, ui_scale)

        # 2. Отрисовка миникарты (встроенный метод)
        self.draw_minimap(screen, player, enemies, level)

        # 3. Отрисовка прицела и хитмарка
        self._draw_crosshair_and_effects(screen, player, enemies, level, ui_scale)

        # 4. Отрисовка временных уведомлений
        self._draw_temporary_messages(screen, ui_scale)

        # 5. Отрисовка вспышки урона (накладывается поверх всего экрана)
        self._draw_damage_flash(screen)

    def _draw_panel(self, screen, x, y, w, h, ui_scale):
        """Рисует полупрозрачную панель с зелёной обводкой и угловыми скобками."""
        # Полупрозрачный черный фон
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 160))
        screen.blit(surf, (x, y))

        # Тонкая зеленая рамка
        pygame.draw.rect(screen, DARK_GREEN, (x, y, w, h), 1)

        # Угловые скобки (яркие зеленые уголки)
        br_len = int(8 * ui_scale)
        thickness = max(1, int(2 * ui_scale))

        # Левый верхний
        pygame.draw.line(screen, GREEN, (x, y), (x + br_len, y), thickness)
        pygame.draw.line(screen, GREEN, (x, y), (x, y + br_len), thickness)
        # Правый верхний
        pygame.draw.line(screen, GREEN, (x + w, y), (x + w - br_len, y), thickness)
        pygame.draw.line(screen, GREEN, (x + w, y), (x + w, y + br_len), thickness)
        # Левый нижний
        pygame.draw.line(screen, GREEN, (x, y + h), (x + br_len, y + h), thickness)
        pygame.draw.line(screen, GREEN, (x, y + h), (x, y + h - br_len), thickness)
        # Правый нижний
        pygame.draw.line(screen, GREEN, (x + w, y + h), (x + w - br_len, y + h), thickness)
        pygame.draw.line(screen, GREEN, (x + w, y + h), (x + w, y + h - br_len), thickness)

    def _draw_health_panel(self, screen, player, ui_scale):
        """Панель здоровья в нижнем левом углу."""
        w = int(320 * ui_scale)
        h = int(110 * ui_scale)
        x = int(20 * ui_scale)
        y = screen.get_height() - h - int(20 * ui_scale)

        self._draw_panel(screen, x, y, w, h, ui_scale)

        # Рисуем красный/зеленый медицинский крест
        cross_size = int(18 * ui_scale)
        cx = x + int(20 * ui_scale)
        cy = y + int(20 * ui_scale)
        arm_w = cross_size // 3
        # Горизонтальная и вертикальная перекладины
        pygame.draw.rect(screen, GREEN, (cx, cy + arm_w, cross_size, arm_w))
        pygame.draw.rect(screen, GREEN, (cx + arm_w, cy, arm_w, cross_size))

        # Текст "ЗДОРОВЬЕ [значение]"
        hp_val = max(0, player.health)
        hp_text = self.font_medium.render(f"ЗДОРОВЬЕ  {hp_val}", True, GREEN)
        screen.blit(hp_text, (cx + cross_size + int(15 * ui_scale), cy - int(2 * ui_scale)))

        # Шкала здоровья (сегментированная)
        bar_x = x + int(20 * ui_scale)
        bar_y = y + int(50 * ui_scale)
        bar_w = w - int(40 * ui_scale)
        bar_h = int(18 * ui_scale)

        # Выбираем цвет шкалы в зависимости от здоровья
        if player.health > 50:
            bar_color = GREEN
        elif player.health > 25:
            bar_color = ORANGE
        else:
            bar_color = RED

        # Фон полосы здоровья
        pygame.draw.rect(screen, (0, 30, 0), (bar_x, bar_y, bar_w, bar_h))

        # Заполнение шкалы
        fill_w = int(bar_w * (hp_val / 100.0))
        if fill_w > 0:
            pygame.draw.rect(screen, bar_color, (bar_x, bar_y, fill_w, bar_h))

        # Рисуем разделители, чтобы шкала выглядела сегментированной (как на референсе)
        num_segments = 20
        seg_w = bar_w / num_segments
        for i in range(1, num_segments):
            sx = int(bar_x + i * seg_w)
            pygame.draw.line(screen, (0, 0, 0), (sx, bar_y), (sx, bar_y + bar_h - 1), 1)

        # Обводка шкалы
        pygame.draw.rect(screen, DARK_GREEN, (bar_x, bar_y, bar_w, bar_h), 1)

        # Линейка делений под шкалой: 0 ... 25 ... 50 ... 75 ... 100
        line_y = bar_y + bar_h + int(4 * ui_scale)
        pygame.draw.line(screen, DARK_GREEN, (bar_x, line_y), (bar_x + bar_w, line_y), 1)
        for pct in [0, 25, 50, 75, 100]:
            tx = int(bar_x + bar_w * (pct / 100.0))
            pygame.draw.line(screen, DARK_GREEN, (tx, line_y), (tx, line_y + int(4 * ui_scale)), 1)
            lbl = self.font_small.render(str(pct), True, DARK_GREEN)
            lbl_rect = lbl.get_rect(center=(tx, line_y + int(12 * ui_scale)))
            screen.blit(lbl, lbl_rect)

    def _draw_objective_panel(self, screen, sector_index, enemies, ui_scale):
        """Панель целей в верхнем левом углу."""
        w = int(280 * ui_scale)
        h = int(95 * ui_scale)
        x = int(20 * ui_scale)
        y = int(20 * ui_scale)

        self._draw_panel(screen, x, y, w, h, ui_scale)

        # Считаем живых врагов
        live_enemies = sum(1 for e in enemies if e.alive)

        # Текст
        sec_text = self.font_medium.render(f"СЕКТОР {sector_index + 1}/5", True, GREEN)
        
        enemy_color = RED if live_enemies > 0 else GREEN
        threat_text = self.font_medium.render(f"УГРОЗЫ: {live_enemies}", True, enemy_color)

        if live_enemies > 0:
            task_str = "ЗАДАЧА: ЗАЧИСТИТЬ СЕКТОР"
            task_color = ORANGE
        else:
            task_str = "ЗАДАЧА: НАЙТИ ТЕРМИНАЛ"
            task_color = GREEN
            
        task_text = self.font_medium.render(task_str, True, task_color)

        # Отрисовка строк
        spacing = int(22 * ui_scale)
        screen.blit(sec_text, (x + int(15 * ui_scale), y + int(12 * ui_scale)))
        screen.blit(threat_text, (x + int(15 * ui_scale), y + int(12 * ui_scale) + spacing))
        screen.blit(task_text, (x + int(15 * ui_scale), y + int(12 * ui_scale) + spacing * 2))

    def _draw_weapon_panel(self, screen, player, ui_scale):
        """Панель оружия в верхнем правом углу под миникартой."""
        # Привязываем ширину к размеру миникарты
        minimap_size = (self.minimap_radius * 2 + 1) * int(self.minimap_base_cell_size * ui_scale)
        margin = int(20 * ui_scale)

        w = minimap_size
        h = int(110 * ui_scale)
        x = screen.get_width() - w - margin
        y = margin + minimap_size + margin

        self._draw_panel(screen, x, y, w, h, ui_scale)

        weapon = player.weapon
        
        # 1. Название оружия
        name_text = self.font_medium.render(weapon.name.upper(), True, GREEN)
        screen.blit(name_text, (x + int(15 * ui_scale), y + int(12 * ui_scale)))

        # 2. Патроны: [Магазин] / [Резерв]
        ammo_val = weapon.ammo
        reserve_val = weapon.reserve_ammo

        ammo_surf = self.font_large.render(str(ammo_val), True, WHITE)
        reserve_surf = self.font_medium.render(f" / {reserve_val}", True, GREEN)

        ammo_x = x + int(15 * ui_scale)
        ammo_y = y + int(40 * ui_scale)
        screen.blit(ammo_surf, (ammo_x, ammo_y))
        # Сдвигаем резервные патроны вправо и немного приподнимаем для красоты
        screen.blit(reserve_surf, (ammo_x + ammo_surf.get_width() + int(5 * ui_scale), ammo_y + int(18 * ui_scale)))

        # 3. Индикатор перезарядки (если она идет)
        if weapon.reload_cooldown > 0:
            progress = 1.0 - (weapon.reload_cooldown / weapon.reload_delay)
            bar_w = w - int(30 * ui_scale)
            bar_h = int(6 * ui_scale)
            bx = x + int(15 * ui_scale)
            by = y + h - int(18 * ui_scale)

            # Текст ПЕРЕЗАРЯДКА
            reload_lbl = self.font_small.render("ПЕРЕЗАРЯДКА", True, RED)
            screen.blit(reload_lbl, (bx, by - int(14 * ui_scale)))

            # Полоса перезарядки
            pygame.draw.rect(screen, (50, 0, 0), (bx, by, bar_w, bar_h))
            pygame.draw.rect(screen, RED, (bx, by, int(bar_w * progress), bar_h))
            pygame.draw.rect(screen, RED, (bx, by, bar_w, bar_h), 1)

    def draw_minimap(self, screen, player, enemies, level):
        """Отрисовка миникарты на отдельной Pygame-поверхности."""
        ui_scale = min(screen.get_width() / self.base_width, screen.get_height() / self.base_height)
        cell_size = int(self.minimap_base_cell_size * ui_scale)
        minimap_size = (self.minimap_radius * 2 + 1) * cell_size
        margin = int(20 * ui_scale)

        x = screen.get_width() - minimap_size - margin
        y = margin

        # Создаем холст миникарты
        minimap_surf = pygame.Surface((minimap_size, minimap_size))
        minimap_surf.fill((0, 0, 0))

        center_x = minimap_size // 2
        center_y = minimap_size // 2
        map_scale = cell_size / level.block_size
        max_dist = (self.minimap_radius + 1.5) * level.block_size

        # 1. Рисуем статические блоки
        self._draw_minimap_terrain(minimap_surf, center_x, center_y, max_dist, map_scale, cell_size, player, level)

        # 2. Рисуем врагов
        self._draw_minimap_enemies(minimap_surf, center_x, center_y, max_dist, map_scale, cell_size, player, enemies, level)

        # 3. Рисуем маркер игрока
        self._draw_player_marker(minimap_surf, center_x, center_y, cell_size, ui_scale, player.angle)

        # Переносим холст на экран
        screen.blit(minimap_surf, (x, y))

        # 4. Рисуем рамку радара (зеленую по умолчанию)
        blink_color = self._get_radar_border_color(player, level)
        pygame.draw.rect(screen, blink_color, (x, y, minimap_size, minimap_size), max(1, int(4 * ui_scale)))

    def _draw_minimap_terrain(self, surf, center_x, center_y, max_dist, map_scale, cell_size, player, level):
        """Отрисовывает стены, двери и терминал на холсте миникарты."""
        map_object = [
            (level.block_map, (100, 100, 100)),       # Стены (серые)
            (level.doors.keys(), (180, 150, 50))      # Двери (коричнево-желтые)
        ]

        if level.terminal_pos is not None:
            map_object.append(([level.terminal_pos], (100, 100, 100))) # Терминал выхода (зеленый)

        for map_obj, color in map_object:
            for obj_x, obj_y in map_obj:
                dx = obj_x - player.x
                dy = obj_y - player.y

                if abs(dx) < max_dist and abs(dy) < max_dist:
                    cell_x = round(center_x + dx * map_scale)
                    cell_y = round(center_y + dy * map_scale)
                    pygame.draw.rect(surf, color, (cell_x, cell_y, cell_size, cell_size))

    def _draw_minimap_enemies(self, surf, center_x, center_y, max_dist, map_scale, cell_size, player, enemies, level):
        """Отрисовывает врагов на холсте миникарты."""
        for enemy in enemies:
            if not enemy.alive or not is_visible(enemy, player, level):
                continue

            dx = enemy.x - player.x
            dy = enemy.y - player.y

            if abs(dx) < max_dist and abs(dy) < max_dist:
                enemy_x = round(center_x + dx * map_scale)
                enemy_y = round(center_y + dy * map_scale)
                pygame.draw.circle(surf, RED, (enemy_x, enemy_y), max(2, cell_size // 3))

    def _draw_player_marker(self, surf, center_x, center_y, cell_size, ui_scale, angle):
        """Отрисовывает кружок игрока и вектор его взгляда."""
        direction_x = center_x + cos(angle) * cell_size
        direction_y = center_y + sin(angle) * cell_size
        
        pygame.draw.line(surf, GREEN, (center_x, center_y), (direction_x, direction_y), max(1, int(2 * ui_scale)))
        pygame.draw.circle(surf, GREEN, (center_x, center_y), max(2, cell_size // 3))

    def _get_radar_border_color(self, player, level):
        """Радар-индикатор близости к выходу."""
        if level.terminal_pos is None:
            return GREEN

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
                return GREEN

        return DARK_GREEN

    def _draw_crosshair_and_effects(self, screen, player, enemies, level, ui_scale):
        """Рисует прицел, индикатор наведения на врага и хитмарк при попадании."""
        # 1. Проверяем, наведен ли прицел на врага прямо сейчас
        is_aiming = any(
            enemy_near_crosshair(enemy, player, level) 
            for enemy in enemies if enemy.alive
        )

        cross_color = RED if is_aiming else WHITE
        size = int(10 * ui_scale)

        # Рисуем перекрестие прицела
        pygame.draw.line(screen, cross_color, (WIDTH_HALF - size, HEIGHT_HALF), (WIDTH_HALF + size, HEIGHT_HALF), 2)
        pygame.draw.line(screen, cross_color, (WIDTH_HALF, HEIGHT_HALF - size), (WIDTH_HALF, HEIGHT_HALF + size), 2)

        # 2. Отрисовка хитмарка (крестик X вокруг прицела при попадании)
        if self.hit_indicator_timer > 0:
            self.hit_indicator_timer -= 1
            hm_color = RED
            hm_dist = int(6 * ui_scale)  # внутренний отступ
            hm_len = int(6 * ui_scale)   # длина черточки
            thickness = max(1, int(2 * ui_scale))

            # Рисуем 4 диагональные полоски хитмарка
            # Левая верхняя
            pygame.draw.line(screen, hm_color, (WIDTH_HALF - hm_dist - hm_len, HEIGHT_HALF - hm_dist - hm_len), (WIDTH_HALF - hm_dist, HEIGHT_HALF - hm_dist), thickness)
            # Правая верхняя
            pygame.draw.line(screen, hm_color, (WIDTH_HALF + hm_dist, HEIGHT_HALF - hm_dist), (WIDTH_HALF + hm_dist + hm_len, HEIGHT_HALF - hm_dist - hm_len), thickness)
            # Левая нижняя
            pygame.draw.line(screen, hm_color, (WIDTH_HALF - hm_dist - hm_len, HEIGHT_HALF + hm_dist + hm_len), (WIDTH_HALF - hm_dist, HEIGHT_HALF + hm_dist), thickness)
            # Правая нижняя
            pygame.draw.line(screen, hm_color, (WIDTH_HALF + hm_dist, HEIGHT_HALF + hm_dist), (WIDTH_HALF + hm_dist + hm_len, HEIGHT_HALF + hm_dist + hm_len), thickness)

    def _draw_temporary_messages(self, screen, ui_scale):
        """Отрисовывает всплывающие временные сообщения под прицелом."""
        if self.message_timer > 0:
            self.message_timer -= 1
            
            msg_surf = self.font_message.render(self.message, True, ORANGE)
            msg_rect = msg_surf.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + int(80 * ui_scale)))
            
            # Добавляем размытую тень для лучшей читаемости на любом фоне
            shadow_surf = self.font_message.render(self.message, True, (0, 0, 0))
            screen.blit(shadow_surf, (msg_rect.x + 2, msg_rect.y + 2))
            screen.blit(msg_surf, msg_rect)

    def _draw_damage_flash(self, screen):
        """Накладывает красный полупрозрачный фильтр при получении урона."""
        if self.damage_flash_timer > 0:
            self.damage_flash_timer -= 1
            # Рассчитываем прозрачность (плавное затухание)
            alpha = int(110 * (self.damage_flash_timer / 15.0))
            
            flash_surf = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
            flash_surf.fill((255, 0, 0, alpha))
            screen.blit(flash_surf, (0, 0))
