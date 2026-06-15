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
from src.models.game_state import GameState


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
        self.load_sector(self.state.sector_index)
        self.font = pygame.font.SysFont('Arial', 52)
        self.running = True

    def load_sector(self, sector_index):
        level = Level(block_size, sector_maps[sector_index])
        self.state.current_level = level
        self.state.player = Player(*self.state.current_level.player_start)
        self.state.enemies = [Dwarf(x, y) for x, y in self.state.current_level.enemies_pos]
        self.state.reset_sector_flags()

    def update(self):
        """Обновляет состояние игры за один кадр."""
        actions = self.inputcon.get_actions()
        if self.state.mode == GameState.SECTOR_CLEAR:
            self.update_sector_clear(actions)
        
        elif self.state.mode == GameState.GAME_OVER:
            self.update_exit_scene(actions)
        
        elif self.state.mode == GameState.FINAL_VICTORY:
            self.update_exit_scene(actions)

        elif self.state.mode == GameState.PLAYING:
            self.update_playing(actions)
                    
    def update_sector_clear(self, actions):
        if actions['E']:
            self.state.mode = GameState.PLAYING
            self.go_to_next_sector()
    
    def update_exit_scene(self, actions):
        if actions['E']:
            self.running = False
    
    def update_playing(self, actions):
        self.state.player.weapon.update()
        shot_fired = self.state.player.update(actions, self.state.current_level)
        update_doors(self.state.current_level)

        for enemy in self.state.enemies:
            enemy.update(self.state.player, self.state.current_level)

        if shot_fired:
            player_shoot(self.state.player, self.state.enemies, self.state.current_level)

        if self.state.player.health <= 0:
            print('Game Over')
            self.state.mode = GameState.GAME_OVER

        if not self.state.sector_clean and all_enemies_dead(self.state.enemies):
            print('Сектор зачищен')
            self.state.sector_clean = True

        if actions['E'] and not self.state.terminal_activated:
            if activate_terminal(self.state.player, self.state.current_level):
                if self.state.sector_clean:
                    print('Терминал активироан')
                    self.state.terminal_activated = True
                    self.state.mode = GameState.SECTOR_CLEAR
                else:
                    print('сектор еще не зачишен')

    def go_to_next_sector(self):
        self.state.sector_index += 1
        if self.state.sector_index < len(sector_maps):
            self.load_sector(self.state.sector_index)  
        else:
            print('Победа')
            self.state.mode = GameState.FINAL_VICTORY

    def render(self):
        """Рисует мир, врагов, оружие, HUD и debug-слой."""
        if self.state.mode == GameState.PLAYING:
            self.render_world()

            if DEBUG:
                self.render_debug()


        self.render_state_message()

        pygame.display.flip()
        pygame.display.set_caption(f'{self.clock.get_fps()}')

    def render_world(self):
        pygame.draw.rect(self.screen, (66, 170, 255), (0, 0, WIDTH, HEIGHT_HALF))
        pygame.draw.rect(self.screen, (25, 25, 25), (0, HEIGHT_HALF, WIDTH, HEIGHT_HALF))
        ray_casting(self.screen, self.state.player, self.state.current_level)

        self.spriterender.draw_enemies(self.state.enemies, self.screen, self.state.player, self.state.current_level)
        self.weaponrender.draw(self.screen, self.state.player.weapon)
        self.hud.draw_hud(self.screen, self.state.player)
        self.hud.draw_crossfire(self.screen)

    def render_state_message(self):
        if self.state.mode == GameState.SECTOR_CLEAR:
            self.draw_center_message('СЕКТОР ЗАЧИЩЕН', 'нажми E чтобы продолжить', (0, 255, 0))
        elif self.state.mode == GameState.GAME_OVER:
            self.draw_center_message('ИГРА ОКОНЧЕНА', 'нажмите E чтобы выйти', (255, 0, 0))
        elif self.state.mode == GameState.FINAL_VICTORY:
            self.draw_center_message('ПОБЕДА', 'нажмите E чтобы выйти', (0, 255, 0))

    def render_debug(self):
        draw_map(self.screen, self.state.player, self.state.current_level)
        for enemy in self.state.enemies:
            enemy.draw_debug(self.screen)

    def draw_center_message(self, title_text, hint_text, color):
        self.screen.fill((0, 0, 0))
        title = self.font.render(title_text, True, color)
        hint = self.font.render(hint_text, True, color)

        self.screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40)))
        self.screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40)))

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
