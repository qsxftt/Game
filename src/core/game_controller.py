"""Главный контроллер игрового цикла."""

import pygame

from src.controllers.input_controller import InputController
from src.core.config import DEBUG, FPS, HEIGHT, HEIGHT_HALF, WIDTH, block_size, sector_maps
from src.models.enemy import Dwarf
from src.models.player import Player
from src.systems.combat_system import player_shoot
from src.systems.door_system import update_doors
from src.views.hud_renderer import HUDrender
from src.views.raycast_renderer import draw_map, ray_casting
from src.views.sprite_renderer import SpriteRender
from src.views.weapon_renderer import WeaponRender
from src.systems.sector_system import all_enemies_dead, activate_terminal
from src.models.level import Level


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
        self.sector_index = 0
        self.load_sector(self.sector_index)
        self.font = pygame.font.SysFont('Arial', 52)
        self.running = True
        self.game_state = 'playing'

    def load_sector(self, sector_index):
        level = Level(block_size, sector_maps[sector_index])
        self.current_level = level
        self.player = Player(*self.current_level.player_start)
        self.enemies = [Dwarf(x, y) for x, y in self.current_level.enemies_pos]
        self.sector_clean = False
        self.terminal_activated = False

    def update(self):
        """Обновляет состояние игры за один кадр."""
        actions = self.inputcon.get_actions()
        if self.game_state == 'sector_clear':
            if actions['E']:
                self.game_state = 'playing'
                self.go_to_next_sector()
            return

        self.player.weapon.update()
        shot_fired = self.player.update(actions, self.current_level)
        update_doors(self.current_level)

        for enemy in self.enemies:
            enemy.update(self.player, self.current_level)

        if shot_fired:
            player_shoot(self.player, self.enemies, self.current_level)

        if self.player.health <= 0:
            print('Game Over')
            self.game_state = 'game_over'
            self.running = False

        if not self.sector_clean and all_enemies_dead(self.enemies):
            print('Сектор зачищен')
            self.sector_clean = True

        if actions['E'] and not self.terminal_activated:
            if activate_terminal(self.player, self.current_level):
                if self.sector_clean:
                    print('Терминал активироан')
                    self.terminal_activated = True
                    self.game_state = 'sector_clear'
                else:
                    print('сектор еще не зачишен')
                       
    def go_to_next_sector(self):
        self.sector_index += 1
        if self.sector_index < len(sector_maps):
            self.load_sector(self.sector_index)  
        else:
            print('Победа')
            self.game_state = 'final_victory'
            self.running = False

    def render(self):
        """Рисует мир, врагов, оружие, HUD и debug-слой."""
        pygame.draw.rect(self.screen, (66, 170, 255), (0, 0, WIDTH, HEIGHT_HALF))
        pygame.draw.rect(self.screen, (25, 25, 25), (0, HEIGHT_HALF, WIDTH, HEIGHT_HALF))
        ray_casting(self.screen, self.player, self.current_level)

        self.spriterender.draw_enemies(self.enemies, self.screen, self.player, self.current_level)
        self.weaponrender.draw(self.screen, self.player.weapon)
        self.hud.draw_hud(self.screen, self.player)
        self.hud.draw_crossfire(self.screen)

        if self.game_state == 'sector_clear':
            self.screen.fill((0, 0, 0))
            title = self.font.render('СЕКТОР ЗАЧИЩЕН', True, (0, 255, 0))
            hint = self.font.render('нажми Е чтобы продолжить', True, (0, 255, 0))

            self.screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40)))
            self.screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40)))

        if DEBUG:
            draw_map(self.screen, self.player, self.current_level)
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
                self.inputcon.handle_event(event)

            self.update()
            self.render()
            self.clock.tick(FPS)

        pygame.quit()
