'''Игровые сцены: меню, игра, переходы и финальные экраны'''

import pygame

from src.core.config import HEIGHT, HEIGHT_HALF, TOTAL_SECTORS, WIDTH
from src.models.enemy import Dwarf, Dwarf2
from src.models.game_state import GameState
from src.models.pickup import Ammo, MedKit, Pickup
from src.models.weapon import Pistol
from src.systems.combat_system import player_shoot
from src.systems.door_system import update_doors
from src.systems.map_system import get_sprite_sorted
from src.systems.score_system import add_sector_score, update_score
from src.systems.sector_system import (
    activate_terminal,
    all_enemies_dead,
    go_to_next_sector,
    start_new_game,
)
from src.views.raycast_renderer import ray_casting


class BaseScene:
    '''Базовый интерфейс сцены'''

    def __init__(self, state, scene_manager):
        '''Создает базовую сцену

        Args:
            state: общее состояние игровой сессии
            scene_manager: менеджер переключения сцен
        '''
        self.state = state
        self.scene_manager = scene_manager

    def update(self, actions):
        '''Обновляет сцену за один кадр

        Args:
            actions: словарь действий пользователя
        '''
        pass

    def render(self, screen):
        '''Рисует сцену

        Args:
            screen: внутренняя поверхность игры
        '''
        pass


class PlayingScene(BaseScene):
    '''Основная игровая сцена'''

    def __init__(
        self,
        state,
        scene_manager,
        weaponrender,
        spriterender,
        hud,
        pickuprender,
        sound_manager,
    ):
        '''Создает основную игровую сцену

        Args:
            state: общее состояние игровой сессии
            scene_manager: менеджер переключения сцен
            weaponrender: renderer оружия
            spriterender: renderer врагов
            hud: renderer игрового интерфейса
            pickuprender: renderer ресурсов
            sound_manager: менеджер звуков
        '''
        super().__init__(state, scene_manager)
        self.weaponrender = weaponrender
        self.spriterender = spriterender
        self.hud = hud
        self.pickuprender = pickuprender
        self.sound_manager = sound_manager

    def update(self, actions):
        '''Обновляет игровой мир и проверяет переходы между сценами

        Args:
            actions: словарь действий пользователя
        '''
        if actions['esc']:
            self.sound_manager.stop_music()
            self.scene_manager.change_scene(GameState.MAIN_MENU)
            return

        door_states = {
            door: door.state for door in self.state.current_level.doors.values()
        }

        self.state.player.weapon.update()
        shot_fired, reload_started = self.state.player.update(actions, self.state.current_level)
        weapon = self.state.player.weapon

        if isinstance(weapon, Pistol):
            sound_prefix = 'pistol'
        else:
            sound_prefix = 'shotgun'

        if shot_fired:
            self.sound_manager.play_sound(f'{sound_prefix}_shot')

        if reload_started:
            self.sound_manager.play_sound(f'{sound_prefix}_reload')

        update_doors(self.state.current_level, self.state.player, self.state.enemies)

        for pickup in self.state.pickups:
            picked_up = pickup.update(self.state.player)

            if picked_up:
                if isinstance(pickup, MedKit):
                    self.sound_manager.play_sound('medkit_pickup')
                elif isinstance(pickup, Ammo):
                    self.sound_manager.play_sound('ammo_pickup')

        for enemy in self.state.enemies:
            attacked = enemy.update(self.state.player, self.state.current_level)

            if attacked:
                if isinstance(enemy, Dwarf):
                    self.sound_manager.play_sound('enemy_basic_attack')
                elif isinstance(enemy, Dwarf2):
                    self.sound_manager.play_sound('enemy_heavy_attack')

                self.sound_manager.play_sound('player_hurt')

        for door, previous_state in door_states.items():
            if door.state == 'opening' and previous_state != 'opening':
                self.sound_manager.play_sound('door_open')

            elif door.state == 'closing' and previous_state != 'closing':
                self.sound_manager.play_sound('door_close')

        if shot_fired:
            hit = player_shoot(self.state.player, self.state.enemies, self.state.current_level)
            if hit:
                self.hud.trigger_hitmark()

                if not hit.alive:
                    self.sound_manager.play_sound('enemy_death')

        update_score(self.state)

        if self.state.player.health <= 0:
            self.sound_manager.stop_music()
            self.scene_manager.change_scene(GameState.GAME_OVER)

        if not self.state.sector_clean and all_enemies_dead(self.state.enemies):
            self.state.sector_clean = True
            self.hud.show_message('СЕКТОР ЗАЧИЩЕН')

        if actions['E'] and not self.state.terminal_activated:
            if activate_terminal(self.state.player, self.state.current_level):
                if self.state.sector_clean:
                    self.sound_manager.play_sound('terminal_activate')
                    add_sector_score(self.state)
                    self.state.terminal_activated = True
                    if (
                        self.state.game_mode == GameState.CAMPAIGN
                        and self.state.sector_index == TOTAL_SECTORS - 1
                    ):
                        self.sound_manager.stop_music()

                    self.scene_manager.change_scene(GameState.SECTOR_CLEAR)

    def render(self, screen):
        '''Рисует игровой мир, спрайты, оружие и HUD

        Args:
            screen: внутренняя поверхность игры
        '''
        pygame.draw.rect(screen, (36, 42, 45), (0, 0, WIDTH, HEIGHT_HALF))
        pygame.draw.rect(screen, (18, 21, 22), (0, HEIGHT_HALF, WIDTH, HEIGHT_HALF))
        ray_casting(screen, self.state.player, self.state.current_level)

        sprites = get_sprite_sorted(
            self.state.pickups, self.state.enemies, self.state.player
        )
        for sprite in sprites:
            if isinstance(sprite, Pickup):
                self.pickuprender.draw(
                    sprite, screen, self.state.player, self.state.current_level
                )
            else:
                self.spriterender.draw(
                    sprite, screen, self.state.player, self.state.current_level
                )

        self.weaponrender.draw(screen, self.state.player.weapon)
        self.hud.draw(screen, self.state)


class MainMenuScene(BaseScene):
    '''Стартовое меню'''

    def __init__(self, state, scene_manager, sound_manager):
        '''Создает главное меню

        Args:
            state: общее состояние игровой сессии
            scene_manager: менеджер переключения сцен
            sound_manager: менеджер звуков
        '''
        super().__init__(state, scene_manager)
        self.sound_manager = sound_manager
        self.title_font = pygame.font.SysFont('Arial', 86, bold=True)
        self.font = pygame.font.SysFont('Arial', 52)
        self.options = [
            ('КАМПАНИЯ', GameState.CAMPAIGN),
            ('БЕСКОНЕЧНЫЙ РЕЖИМ', GameState.ENDLESS),
            ('НАСТРОЙКИ', GameState.SETTINGS),
            ('ВЫХОД', 'exit'),
        ]
        self.selected_index = 0

    def update(self, actions):
        '''Обрабатывает навигацию и выбор пункта меню

        Args:
            actions: словарь действий пользователя
        '''
        if actions['up_pressed']:
            self.selected_index = (self.selected_index - 1) % len(self.options)

        elif actions['down_pressed']:
            self.selected_index = (self.selected_index + 1) % len(self.options)

        if actions['E']:
            self.sound_manager.play_sound('menu_select')
            _, action = self.options[self.selected_index]

            if action == GameState.CAMPAIGN:
                start_new_game(self.state, GameState.CAMPAIGN)
                self.sound_manager.play_music()
                self.scene_manager.change_scene(GameState.PLAYING)

            elif action == GameState.ENDLESS:
                start_new_game(self.state, GameState.ENDLESS)
                self.sound_manager.play_music()
                self.scene_manager.change_scene(GameState.PLAYING)

            elif action == GameState.SETTINGS:
                self.scene_manager.change_scene(GameState.SETTINGS)

            elif action == 'exit':
                self.state.running = False

    def render(self, screen):
        '''Рисует главное меню

        Args:
            screen: внутренняя поверхность игры
        '''
        screen.fill((0, 0, 0))

        title = self.title_font.render('PROJECT GATE', True, (0, 255, 0))
        screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 4)))

        for index, (label, _) in enumerate(self.options):
            if index == self.selected_index:
                color = (0, 255, 0)
            else:
                color = (120, 120, 120)
            text = self.font.render(label, True, color)
            y = HEIGHT // 2 - 40 + index * 60
            screen.blit(text, text.get_rect(center=(WIDTH // 2, y)))


class SettingsScene(BaseScene):
    '''Экран настройки разрешения, режима окна и громкости'''

    def __init__(self, state, scene_manager, display_settings, sound_manager):
        '''Создает экран настроек

        Args:
            state: общее состояние игровой сессии
            scene_manager: менеджер переключения сцен
            display_settings: настройки окна
            sound_manager: менеджер звуков
        '''
        super().__init__(state, scene_manager)
        self.display_settings = display_settings
        self.sound_manager = sound_manager
        self.font = pygame.font.SysFont('Arial', 52)
        self.selected_index = 0
        self.options = ['resolution', 'fullscreen', 'volume', 'back']

    def update(self, actions):
        '''Обрабатывает навигацию и изменение настроек

        Args:
            actions: словарь действий пользователя
        '''
        if actions['up_pressed']:
            self.selected_index = (self.selected_index - 1) % len(self.options)

        elif actions['down_pressed']:
            self.selected_index = (self.selected_index + 1) % len(self.options)

        selected_option = self.options[self.selected_index]

        if actions['E']:
            self.sound_manager.play_sound('menu_select')

        if selected_option == 'resolution':
            if actions['left_pressed']:
                self.display_settings.change_resolution(-1)
            elif actions['right_pressed'] or actions['E']:
                self.display_settings.change_resolution(1)

        elif selected_option == 'fullscreen':
            if actions['left_pressed'] or actions['right_pressed'] or actions['E']:
                self.display_settings.toggle_fullscreen()

        elif selected_option == 'volume':
            if actions['left_pressed']:
                self.sound_manager.set_volume(self.sound_manager.volume - 0.1)
            elif actions['right_pressed']:
                self.sound_manager.set_volume(self.sound_manager.volume + 0.1)

        elif selected_option == 'back' and actions['E']:
            self.scene_manager.change_scene(GameState.MAIN_MENU)

    def render(self, screen):
        '''Рисует текущие значения настроек

        Args:
            screen: внутренняя поверхность игры
        '''
        screen.fill((0, 0, 0))

        width, height = self.display_settings.resolution
        if self.display_settings.fullscreen:
            fullscreen = 'ВКЛ'
        else:
            fullscreen = 'ВЫКЛ'

        labels = {
            'resolution': f'РАЗРЕШЕНИЕ: {width}x{height}',
            'fullscreen': f'ПОЛНЫЙ ЭКРАН: {fullscreen}',
            'volume': f'ГРОМКОСТЬ: {round(self.sound_manager.volume * 100)}%',
            'back': 'НАЗАД',
        }

        title = self.font.render('НАСТРОЙКИ', True, (0, 255, 0))

        screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 140)))

        for index, option in enumerate(self.options):
            if index == self.selected_index:
                color = (0, 255, 0)
            else:
                color = (120, 120, 120)

            text = self.font.render(labels[option], True, color)
            y = HEIGHT // 2 - 30 + index * 70

            screen.blit(text, text.get_rect(center=(WIDTH // 2, y)))


class ResultScene(BaseScene):
    '''Общий экран результата в стиле терминала GATE'''

    title = ''
    subtitle = ''
    hint = ''
    accent_color = (0, 255, 0)

    def __init__(self, state, scene_manager):
        '''Создает общий экран результата

        Args:
            state: общее состояние игровой сессии
            scene_manager: менеджер переключения сцен
        '''
        super().__init__(state, scene_manager)
        self.title_font = pygame.font.SysFont('Arial', 64, bold=True)
        self.subtitle_font = pygame.font.SysFont('Arial', 28, bold=True)
        self.stats_font = pygame.font.SysFont('Arial', 30)
        self.hint_font = pygame.font.SysFont('Arial', 24, bold=True)
        self.system_font = pygame.font.SysFont('Arial', 18)

    def get_stats(self):
        '''Возвращает строки статистики конкретного результата'''
        return ()

    def draw_frame(self, screen, rect):
        '''Рисует рамку экрана результата

        Args:
            screen: внутренняя поверхность игры
            rect: прямоугольник рамки
        '''
        pygame.draw.rect(screen, (0, 45, 20), rect, 1)
        corner = 32
        segments = (
            ((rect.left, rect.top), (rect.left + corner, rect.top)),
            ((rect.left, rect.top), (rect.left, rect.top + corner)),
            ((rect.right, rect.top), (rect.right - corner, rect.top)),
            ((rect.right, rect.top), (rect.right, rect.top + corner)),
            ((rect.left, rect.bottom), (rect.left + corner, rect.bottom)),
            ((rect.left, rect.bottom), (rect.left, rect.bottom - corner)),
            ((rect.right, rect.bottom), (rect.right - corner, rect.bottom)),
            ((rect.right, rect.bottom), (rect.right, rect.bottom - corner)),
        )
        for start, end in segments:
            pygame.draw.line(screen, self.accent_color, start, end, 3)

    def render(self, screen):
        '''Рисует общий экран результата

        Args:
            screen: внутренняя поверхность игры
        '''
        width, height = screen.get_size()
        screen.fill((0, 6, 3))

        grid_color = (0, 20, 9)
        for x in range(0, width, 80):
            pygame.draw.line(screen, grid_color, (x, 0), (x, height))
        for y in range(0, height, 80):
            pygame.draw.line(screen, grid_color, (0, y), (width, y))

        system = self.system_font.render(
            'GENESIS ANOMALY TESTING ENVIRONMENT', True, (70, 120, 85)
        )
        screen.blit(system, system.get_rect(center=(width // 2, 55)))

        frame = pygame.Rect(0, 0, int(width * 0.68), int(height * 0.58))
        frame.center = (width // 2, height // 2)
        self.draw_frame(screen, frame)

        title = self.title_font.render(self.title, True, self.accent_color)
        subtitle = self.subtitle_font.render(self.subtitle, True, (180, 200, 185))
        screen.blit(title, title.get_rect(center=(width // 2, frame.top + 105)))
        screen.blit(subtitle, subtitle.get_rect(center=(width // 2, frame.top + 165)))

        line_y = frame.top + 205
        pygame.draw.line(
            screen,
            (0, 65, 28),
            (frame.left + 90, line_y),
            (frame.right - 90, line_y),
            1,
        )

        for index, stat in enumerate(self.get_stats()):
            text = self.stats_font.render(stat, True, (205, 220, 210))
            y = line_y + 55 + index * 48
            screen.blit(text, text.get_rect(center=(width // 2, y)))

        if (pygame.time.get_ticks() // 600) % 2 == 0:
            hint = self.hint_font.render(self.hint, True, self.accent_color)
            screen.blit(hint, hint.get_rect(center=(width // 2, frame.bottom - 55)))


class SectorClearScene(ResultScene):
    '''Показывает статистику завершенного сектора'''

    title = 'СЕКТОР ЗАЧИЩЕН'
    subtitle = 'УГРОЗЫ НЕЙТРАЛИЗОВАНЫ'
    hint = 'E  ПРОДОЛЖИТЬ'
    accent_color = (0, 255, 100)

    def get_stats(self):
        '''Возвращает номер сектора, здоровье и текущий счет'''
        return (
            f'СЕКТОР: {self.state.sector_index + 1}',
            f'ЗДОРОВЬЕ: {int(self.state.player.health)}',
            f'СЧЁТ: {self.state.score}',
        )

    def update(self, actions):
        '''Загружает следующий сектор или открывает экран победы

        Args:
            actions: словарь действий пользователя
        '''
        if actions['E']:
            if go_to_next_sector(self.state):
                self.scene_manager.change_scene(GameState.PLAYING)
            else:
                self.scene_manager.change_scene(GameState.FINAL_VICTORY)


class GameOverScene(ResultScene):
    '''Показывает результат после гибели игрока'''

    title = 'СИГНАЛ ПОТЕРЯН'
    subtitle = 'СОТРУДНИК НЕ ОТВЕЧАЕТ'
    hint = 'E  ГЛАВНОЕ МЕНЮ'
    accent_color = (255, 55, 55)

    def get_stats(self):
        '''Возвращает достигнутый сектор и итоговый счет'''
        return (
            f'ДОСТИГНУТЫЙ СЕКТОР: {self.state.sector_index + 1}',
            f'ИТОГОВЫЙ СЧЁТ: {self.state.score}',
        )

    def update(self, actions):
        '''Возвращает игрока в главное меню

        Args:
            actions: словарь действий пользователя
        '''
        if actions['E']:
            self.scene_manager.change_scene(GameState.MAIN_MENU)


class FinalVictoryScene(ResultScene):
    '''Показывает итог успешного прохождения кампании'''

    title = 'ПРОТОКОЛ GATE ЗАВЕРШЁН'
    subtitle = 'ВСЕ СЕКТОРЫ ЗАЧИЩЕНЫ'
    hint = 'E  ГЛАВНОЕ МЕНЮ'
    accent_color = (0, 220, 220)

    def get_stats(self):
        '''Возвращает число секторов и итоговый счет кампании'''
        return (
            f'СЕКТОРОВ ЗАЧИЩЕНО: {TOTAL_SECTORS}',
            f'ИТОГОВЫЙ СЧЁТ: {self.state.score}',
        )

    def update(self, actions):
        '''Возвращает игрока в главное меню

        Args:
            actions: словарь действий пользователя
        '''
        if actions['E']:
            self.scene_manager.change_scene(GameState.MAIN_MENU)
