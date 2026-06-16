import pygame
from src.models.game_state import GameState
from src.core.config import *
from src.systems.sector_system import go_to_next_sector, all_enemies_dead, activate_terminal
from src.systems.door_system import update_doors
from src.systems.combat_system import player_shoot
from src.views.raycast_renderer import ray_casting, draw_map
from src.systems.map_system import get_sprite_sorted
from src.models.pickup import Pickup


class BaseScene:
    def __init__(self, state, scene_manager):
        self.state = state
        self.scene_manager = scene_manager

    def handle_event(self, event):
        pass

    def update(self, actions):
        pass

    def render(self, screen):
        pass

class PlayingScene(BaseScene):
    def __init__(self, state, scene_manager, weaponrender, spriterender, hud, pickuprender):
        super().__init__(state, scene_manager)
        self.weaponrender = weaponrender
        self.spriterender = spriterender
        self.hud = hud
        self.pickuprender = pickuprender

    def update(self, actions):
        self.state.player.weapon.update()
        shot_fired = self.state.player.update(actions, self.state.current_level)
        update_doors(self.state.current_level)

        for pickup in self.state.pickups:
            pickup.update(self.state.player)

        for enemy in self.state.enemies:
            enemy.update(self.state.player, self.state.current_level)

        if shot_fired:
            player_shoot(self.state.player, self.state.enemies, self.state.current_level)

        if self.state.player.health <= 0:
            print('Game Over')
            self.scene_manager.change_scene(GameState.GAME_OVER)

        if not self.state.sector_clean and all_enemies_dead(self.state.enemies):
            print('Сектор зачищен')
            self.state.sector_clean = True

        if actions['E'] and not self.state.terminal_activated:
            if activate_terminal(self.state.player, self.state.current_level):
                if self.state.sector_clean:
                    print('Терминал активироан')
                    self.state.terminal_activated = True
                    self.scene_manager.change_scene(GameState.SECTOR_CLEAR)
                else:
                    print('сектор еще не зачишен')

    def render(self, screen):
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
        self.hud.draw_hud(screen, self.state.player)
        self.hud.draw_crossfire(screen)

        if DEBUG:
            draw_map(screen, self.state.player, self.state.current_level)
            for enemy in self.state.enemies:
                enemy.draw_debug(screen)


class MainMenuScene(BaseScene):
    def __init__(self, state, scene_manager):
        super().__init__(state, scene_manager)
        self.font = pygame.font.SysFont('Arial', 52)

    def update(self, actions):
        if actions['E']:
            self.scene_manager.change_scene(GameState.PLAYING)

    def render(self, screen):
        screen.fill((0, 0, 0))
        title = self.font.render('ГЛАВНОЕ МЕНЮ', True, (0, 255, 0))
        hint = self.font.render('нажми Е чтобы начать', True, (0, 255, 0))

        screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40)))
        screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40)))

class SectorClearScene(BaseScene):
    def __init__(self, state, scene_manager):
        super().__init__(state, scene_manager)
        self.font = pygame.font.SysFont('Arial', 52)

    def update(self, actions):
        if actions['E']:
            if go_to_next_sector(self.state):
                self.scene_manager.change_scene(GameState.PLAYING)
            else:
                self.scene_manager.change_scene(GameState.FINAL_VICTORY)

    def render(self, screen):
        screen.fill((0, 0, 0))

        title = self.font.render('СЕКТОР ЗАЧИЩЕН', True, (0, 255, 0))
        hint = self.font.render('нажми E чтобы продолжить', True, (0, 255, 0))

        screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40)))
        screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40)))

class GameOverScene(BaseScene):
    def __init__(self, state, scene_manager):
        super().__init__(state, scene_manager)
        self.font = pygame.font.SysFont('Arial', 52)

    def update(self, actions):
        if actions['E']:
            self.state.running = False

    def render(self, screen):
        screen.fill((0, 0, 0))

        title = self.font.render('ИГРА ОКОНЧЕНА', True, (255, 0, 0))
        hint = self.font.render('нажми E чтобы выйти', True, (255, 0, 0))

        screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40)))
        screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40)))

class FinalVictoryScene(BaseScene):
    def __init__(self, state, scene_manager):
        super().__init__(state, scene_manager)
        self.font = pygame.font.SysFont('Arial', 52)

    def update(self, actions):
        if actions['E']:
            self.state.running = False

    def render(self, screen):
        screen.fill((0, 0, 0))

        title = self.font.render('ПОБЕДА', True, (0, 255, 0))
        hint = self.font.render('нажми E чтобы выйти', True, (0, 255, 0))

        screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40)))
        screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40)))
