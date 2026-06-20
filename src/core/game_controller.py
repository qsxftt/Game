"""Главный контроллер игрового цикла."""

import pygame

from src.controllers.input_controller import InputController
from src.core.config import FPS, HEIGHT, WIDTH
from src.core.scene_manager import SceneManager
from src.models.game_state import GameState
from src.scenes.scenes import (
    FinalVictoryScene,
    GameOverScene,
    MainMenuScene,
    PlayingScene,
    SectorClearScene,
    SettingsScene
)
from src.views.hud_renderer import HUDrender
from src.views.pickup_renderer import PickupRender
from src.views.sprite_renderer import SpriteRender
from src.views.weapon_renderer import WeaponRender
from src.views.raycast_renderer import convert_textures
from src.core.display_settings import DisplaySettings


class GameController:
    """Собирает игру и управляет циклом update/render."""

    def __init__(self):
        """Инициализирует pygame, окно, состояние, renderers и сцены."""
        pygame.init()

        self.display_settings = DisplaySettings()
        self.display = pygame.display.set_mode(self.display_settings.resolution)
        self.screen = pygame.Surface((WIDTH, HEIGHT)).convert()

        convert_textures()
        self.hud = HUDrender()
        self.weaponrender = WeaponRender()
        self.spriterender = SpriteRender()
        self.pickuprender = PickupRender()
        self.clock = pygame.time.Clock()
        self.inputcon = InputController()
        self.state = GameState()
        self.scene_manager = SceneManager()

        self.scene_manager.register(GameState.MAIN_MENU, MainMenuScene(self.state, self.scene_manager))
        self.scene_manager.register(GameState.SETTINGS, SettingsScene(self.state, self.scene_manager, self.display_settings))
        self.scene_manager.register(
            GameState.PLAYING,
            PlayingScene(
                self.state,
                self.scene_manager,
                self.weaponrender,
                self.spriterender,
                self.hud,
                self.pickuprender,
            ),
        )
        self.scene_manager.register(GameState.SECTOR_CLEAR, SectorClearScene(self.state, self.scene_manager))
        self.scene_manager.register(GameState.GAME_OVER, GameOverScene(self.state, self.scene_manager))
        self.scene_manager.register(GameState.FINAL_VICTORY, FinalVictoryScene(self.state, self.scene_manager))

        self.scene_manager.change_scene(GameState.MAIN_MENU)

    def apply_display_settings(self):
        """Применяет настройки настоящего окна."""
        if self.display_settings.fullscreen:
            size = (0, 0)
            flags = pygame.FULLSCREEN
        else:
            size = self.display_settings.resolution
            flags = 0

        self.display = pygame.display.set_mode(size, flags)

        # Повторно оптимизируем поверхности под новый режим экрана.
        self.screen = self.screen.convert()
        convert_textures()

        self.display_settings.changed = False

    def present_frame(self):
        """Выводит внутренний кадр в настоящее окно."""
        internal_width, internal_height = self.screen.get_size()
        display_width, display_height = self.display.get_size()

        scale = min(display_width / internal_width, display_height / internal_height)

        frame_size = (int(internal_width * scale), int(internal_height * scale))

        if frame_size == self.screen.get_size():
            frame = self.screen
        else:
            frame = pygame.transform.scale(self.screen, frame_size)

        frame_x = (display_width - frame_size[0]) // 2
        frame_y = (display_height - frame_size[1]) // 2

        self.display.fill((0, 0, 0))
        self.display.blit(frame, (frame_x, frame_y))
        pygame.display.flip()

    def run(self):
        """Запускает игровой цикл и закрывает pygame после выхода."""
        while self.state.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.state.running = False
                self.inputcon.handle_event(event)

            actions = self.inputcon.get_actions()

            self.scene_manager.update(actions)

            if self.display_settings.changed:
                self.apply_display_settings()

            self.scene_manager.render(self.screen)
            self.present_frame()
            pygame.display.set_caption(f'{self.clock.get_fps()}')
            self.clock.tick(FPS)

        pygame.quit()
