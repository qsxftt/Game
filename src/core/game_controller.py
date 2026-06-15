"""Главный контроллер игрового цикла."""

import pygame

from src.controllers.input_controller import InputController
from src.core.config import FPS, HEIGHT, WIDTH
from src.views.hud_renderer import HUDrender
from src.views.sprite_renderer import SpriteRender
from src.views.weapon_renderer import WeaponRender
from src.systems.sector_system import load_sector
from src.models.game_state import GameState
from src.core.scene_manager import SceneManager
from src.scenes.scenes import *

class GameController:
    """Собирает игру и управляет циклом update/render.

    Сейчас этот класс временно хранит ссылки на игрока, врагов, renderer'ы и
    systems. Позже часть состояния можно будет вынести в GameState и Level.
    """

    def __init__(self):
        """Инициализирует pygame, окно и основные объекты прототипа."""
        pygame.init()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.hud = HUDrender()
        self.weaponrender = WeaponRender()
        self.spriterender = SpriteRender()
        self.clock = pygame.time.Clock()
        self.inputcon = InputController()
        self.state = GameState()
        self.scene_manager = SceneManager()
        load_sector(self.state)

        self.scene_manager.register(GameState.MAIN_MENU, MainMenuScene(self.state, self.scene_manager))
        self.scene_manager.register(GameState.PLAYING, PlayingScene(self.state, self.scene_manager, self.weaponrender, self.spriterender, self.hud))
        self.scene_manager.register(GameState.SECTOR_CLEAR, SectorClearScene(self.state, self.scene_manager))
        self.scene_manager.register(GameState.GAME_OVER, GameOverScene(self.state, self.scene_manager))
        self.scene_manager.register(GameState.FINAL_VICTORY, FinalVictoryScene(self.state, self.scene_manager))

        self.scene_manager.change_scene(GameState.MAIN_MENU)

    def run(self):
        """Запускает игровой цикл и закрывает pygame после выхода."""
        while self.state.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.state.running = False
                self.inputcon.handle_event(event)

            actions = self.inputcon.get_actions()

            self.scene_manager.update(actions)
            self.scene_manager.render(self.screen)
            
            pygame.display.flip()
            pygame.display.set_caption(f'{self.clock.get_fps()}')
            self.clock.tick(FPS)

        pygame.quit()
