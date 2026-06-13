"""Главный контроллер игрового цикла."""

import pygame

from src.controllers.input_controller import InputController
from src.core.config import DEBUG, FPS, HEIGHT, HEIGHT_HALF, WIDTH
from src.models.enemy import Dwarf
from src.models.player import Player
from src.systems.combat_system import player_shoot
from src.systems.door_system import update_doors
from src.views.hud_renderer import HUDrender
from src.views.raycast_renderer import draw_map, ray_casting
from src.views.sprite_renderer import SpriteRender
from src.views.weapon_renderer import WeaponRender


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
        self.player = Player()
        self.inputcon = InputController()
        self.enemies = [
            Dwarf(300, 200)
        ]
        self.running = True

    def update(self):
        """Обновляет состояние игры за один кадр."""
        actions = self.inputcon.get_actions()
        self.player.weapon.update()
        shot_fired = self.player.update(actions)
        update_doors()

        for enemy in self.enemies:
            enemy.update(self.player)

        if shot_fired:
            player_shoot(self.player, self.enemies)

        if self.player.health <= 0:
            print('Game Over')
            self.running = False

    def render(self):
        """Рисует мир, врагов, оружие, HUD и debug-слой."""
        pygame.draw.rect(self.screen, (66, 170, 255), (0, 0, WIDTH, HEIGHT_HALF))
        pygame.draw.rect(self.screen, (25, 25, 25), (0, HEIGHT_HALF, WIDTH, HEIGHT_HALF))
        ray_casting(self.screen, self.player)

        self.spriterender.draw_enemies(self.enemies, self.screen, self.player)
        self.weaponrender.draw(self.screen, self.player.weapon)
        self.hud.draw_hud(self.screen, self.player)
        self.hud.draw_crossfire(self.screen)

        if DEBUG:
            draw_map(self.screen, self.player)
            for enemy in self.enemies:
                enemy.draw_debug(self.screen)

        pygame.display.flip()
        pygame.display.set_caption(f'{self.clock.get_fps()}')

    def run(self):
        """Запускает игровой цикл и закрывает pygame после выхода."""
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.update()
            self.render()
            self.clock.tick(FPS)

        pygame.quit()
