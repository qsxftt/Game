"""Игровые сцены: меню, игра, переходы и финальные экраны."""

import pygame

from src.core.config import HEIGHT, HEIGHT_HALF, WIDTH
from src.models.game_state import GameState
from src.models.pickup import Pickup
from src.systems.combat_system import player_shoot
from src.systems.door_system import update_doors
from src.systems.map_system import get_sprite_sorted
from src.systems.sector_system import activate_terminal, all_enemies_dead, go_to_next_sector, start_new_game
from src.views.raycast_renderer import ray_casting
from src.systems.score_system import update_score, add_sector_score


class BaseScene:
    """Базовый интерфейс сцены."""

    def __init__(self, state, scene_manager):
        """Сохраняет общее состояние игры и менеджер сцен."""
        self.state = state
        self.scene_manager = scene_manager

    def update(self, actions):
        """Обновляет сцену за один кадр."""
        pass

    def render(self, screen):
        """Рисует сцену."""
        pass


class PlayingScene(BaseScene):
    """Основная игровая сцена."""

    def __init__(self, state, scene_manager, weaponrender, spriterender, hud, pickuprender):
        """Получает state, renderers и HUD для игрового режима."""
        super().__init__(state, scene_manager)
        self.weaponrender = weaponrender
        self.spriterender = spriterender
        self.hud = hud
        self.pickuprender = pickuprender

    def update(self, actions):
        """Обновляет игрока, врагов, двери, pickups и условия перехода сцены."""
        if actions['esc']:
            self.scene_manager.change_scene(GameState.MAIN_MENU)
            return

        self.state.player.weapon.update()
        shot_fired = self.state.player.update(actions, self.state.current_level)
        update_doors(self.state.current_level, self.state.player, self.state.enemies)

        for pickup in self.state.pickups:
            pickup.update(self.state.player)

        for enemy in self.state.enemies:
            enemy.update(self.state.player, self.state.current_level)

        if shot_fired:
            hit = player_shoot(self.state.player, self.state.enemies, self.state.current_level)
            if hit:
                self.hud.trigger_hitmark()

        update_score(self.state)

        if self.state.player.health <= 0:
            print('Game Over')
            self.scene_manager.change_scene(GameState.GAME_OVER)

        if not self.state.sector_clean and all_enemies_dead(self.state.enemies):
            print('Сектор зачищен')
            self.state.sector_clean = True
            self.hud.show_message('СЕКТОР ЗАЧИЩЕН')

        if actions['E'] and not self.state.terminal_activated:
            if activate_terminal(self.state.player, self.state.current_level):
                if self.state.sector_clean:
                    add_sector_score(self.state)
                    self.state.terminal_activated = True
                    self.scene_manager.change_scene(GameState.SECTOR_CLEAR)
                else:
                    print('Сектор еще не зачищен')

    def render(self, screen):
        """Рисует мир, sprites, оружие, HUD и debug-карту."""
        pygame.draw.rect(screen, (66, 170, 255), (0, 0, WIDTH, HEIGHT_HALF))
        pygame.draw.rect(screen, (25, 25, 25), (0, HEIGHT_HALF, WIDTH, HEIGHT_HALF))
        ray_casting(screen, self.state.player, self.state.current_level)

        sprites = get_sprite_sorted(self.state.pickups, self.state.enemies, self.state.player)
        for sprite in sprites:
            if isinstance(sprite, Pickup):
                self.pickuprender.draw(sprite, screen, self.state.player, self.state.current_level)
            else:
                self.spriterender.draw(sprite, screen, self.state.player, self.state.current_level)

        self.weaponrender.draw(screen, self.state.player.weapon)
        self.hud.draw(screen, self.state)



class MainMenuScene(BaseScene):
    """Стартовое меню."""

    def __init__(self, state, scene_manager):
        """Создает шрифт главного меню."""
        super().__init__(state, scene_manager)
        self.font = pygame.font.SysFont('Arial', 52)
        self.options = [
            ('КАМПАНИЯ', GameState.CAMPAIGN),
            ('БЕСКОНЕЧНЫЙ РЕЖИМ', GameState.ENDLESS),
            ('НАСТРОЙКИ', GameState.SETTINGS),
            ('ВЫХОД', 'exit'),
        ]
        self.selected_index = 0

    def update(self, actions):
        """Запускает игру по нажатию E."""
        if actions['up_pressed']:
            self.selected_index = (self.selected_index - 1) % len(self.options)

        elif actions['down_pressed']:
            self.selected_index = (self.selected_index + 1) % len(self.options)

        if actions['E']:
            _, action = self.options[self.selected_index]

            if action == GameState.CAMPAIGN:
                start_new_game(self.state, GameState.CAMPAIGN)
                self.scene_manager.change_scene(GameState.PLAYING)

            elif action == GameState.ENDLESS:
                start_new_game(self.state, GameState.ENDLESS)
                self.scene_manager.change_scene(GameState.PLAYING)

            elif action == GameState.SETTINGS:
                self.scene_manager.change_scene(GameState.SETTINGS)

            elif action == 'exit':
                self.state.running = False

    def render(self, screen):
        """Рисует главное меню."""
        screen.fill((0, 0, 0))
        for index, (label, _) in enumerate(self.options):
            if index == self.selected_index:
                color = (0, 255, 0)
            else:
                color = (120, 120, 120)
            text = self.font.render(label, True, color)
            y = HEIGHT // 2 - 40 + index * 60
            screen.blit(text, text.get_rect(center=(WIDTH // 2, y)))

class SettingsScene(BaseScene):
    def __init__(self, state, scene_manager, display_settings):
        super().__init__(state, scene_manager)
        self.display_settings = display_settings
        self.font = pygame.font.SysFont('Arial', 52)
        self.selected_index = 0
        self.options = [
            'resolution',
            'fullscreen',
            'back'
        ]

    def update(self, actions):
        if actions['up_pressed']:
            self.selected_index = (self.selected_index - 1) % len(self.options)

        elif actions['down_pressed']:
            self.selected_index = (self.selected_index + 1) % len(self.options)

        selected_option = self.options[self.selected_index]

        if selected_option == 'resolution':
            if actions['left_pressed']:
                self.display_settings.change_resolution(-1)
            elif actions['right_pressed'] or actions['E']:
                self.display_settings.change_resolution(1)

        elif selected_option == 'fullscreen':
            if (
                actions['left_pressed']
                or actions['right_pressed']
                or actions['E']
            ):
                self.display_settings.toggle_fullscreen()

        elif selected_option == 'back' and actions['E']:
            self.scene_manager.change_scene(GameState.MAIN_MENU)

    def render(self, screen):
        screen.fill((0, 0, 0))

        width, height = self.display_settings.resolution
        if self.display_settings.fullscreen:
            fullscreen = 'ВКЛ'
        else:
            fullscreen = 'ВЫКЛ'

        labels = {
            'resolution': f'РАЗРЕШЕНИЕ: {width}x{height}',
            'fullscreen': f'ПОЛНЫЙ ЭКРАН: {fullscreen}',
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

class SectorClearScene(BaseScene):
    """Экран между секторами."""

    def __init__(self, state, scene_manager):
        """Создает шрифт экрана зачистки сектора."""
        super().__init__(state, scene_manager)
        self.font = pygame.font.SysFont('Arial', 52)

    def update(self, actions):
        """Переходит к следующему сектору или к финальной победе."""
        if actions['E']:
            if go_to_next_sector(self.state):
                self.scene_manager.change_scene(GameState.PLAYING)
            else:
                self.scene_manager.change_scene(GameState.FINAL_VICTORY)

    def render(self, screen):
        """Рисует экран зачистки сектора."""
        screen.fill((0, 0, 0))

        title = self.font.render('СЕКТОР ЗАЧИЩЕН', True, (0, 255, 0))
        hint = self.font.render('нажми E чтобы продолжить', True, (0, 255, 0))
        score = self.font.render(f'СЧЁТ: {self.state.score}', True, (0, 255, 0))

        screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 70)))
        screen.blit(score, score.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
        screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 70)))


class GameOverScene(BaseScene):
    """Экран поражения."""

    def __init__(self, state, scene_manager):
        """Создает шрифт экрана поражения."""
        super().__init__(state, scene_manager)
        self.font = pygame.font.SysFont('Arial', 52)

    def update(self, actions):
        """Закрывает игру по нажатию E."""
        if actions['E']:
            self.scene_manager.change_scene(GameState.MAIN_MENU)

    def render(self, screen):
        """Рисует экран поражения."""
        screen.fill((0, 0, 0))

        title = self.font.render('ИГРА ОКОНЧЕНА', True, (255, 0, 0))
        hint = self.font.render('нажми E чтобы выйти', True, (255, 0, 0))
        score = self.font.render(f'СЧЁТ: {self.state.score}', True, (255, 0, 0))

        screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 70)))
        screen.blit(score, score.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
        screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 70)))


class FinalVictoryScene(BaseScene):
    """Финальный экран победы."""

    def __init__(self, state, scene_manager):
        """Создает шрифт финального экрана."""
        super().__init__(state, scene_manager)
        self.font = pygame.font.SysFont('Arial', 52)

    def update(self, actions):
        """Закрывает игру по нажатию E."""
        if actions['E']:
            self.scene_manager.change_scene(GameState.MAIN_MENU)

    def render(self, screen):
        """Рисует финальный экран победы."""
        screen.fill((0, 0, 0))

        title = self.font.render('ПОБЕДА', True, (0, 255, 0))
        hint = self.font.render('нажми E чтобы выйти', True, (0, 255, 0))
        score = self.font.render(f'СЧЁТ: {self.state.score}', True, (0, 255, 0))

        screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 70)))
        screen.blit(score, score.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
        screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 70)))
