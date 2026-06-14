"""Контроллер ввода игрока."""

import pygame


class InputController:
    """Считывает клавиатуру и превращает её состояние в словарь действий."""
    def __init__(self):
        self.E = False
        self.R = False
        self.SPACE = False

    def get_actions(self):
        """Возвращает действия игрока за текущий кадр."""
        keys = pygame.key.get_pressed()

        actions = {
            'W': keys[pygame.K_w],
            'S': keys[pygame.K_s],
            'A': keys[pygame.K_a],
            'D': keys[pygame.K_d],
            'left': keys[pygame.K_LEFT],
            'right': keys[pygame.K_RIGHT],
            'E': self.E,
            'space': self.SPACE,
            'R': self.R
        }
        
        self.E = False
        self.R = False
        self.SPACE = False
        
        return actions
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                self.E = True
            if event.key == pygame.K_r:
                self.R = True
            if event.key == pygame.K_SPACE:
                self.SPACE = True

            

