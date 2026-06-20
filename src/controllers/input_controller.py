"""Контроллер ввода игрока."""

import pygame


class InputController:
    """Считывает клавиатуру и превращает ее состояние в словарь действий."""

    def __init__(self):
        """Создает флаги одноразовых нажатий."""
        self.E = False
        self.R = False
        self.Q = False
        self.SPACE = False
        self.UP = False
        self.DOWN = False
        self.LEFT = False
        self.RIGHT = False
        self.ESCAPE = False

    def get_actions(self):
        """Возвращает действия игрока за текущий кадр."""
        keys = pygame.key.get_pressed()

        actions = {
            'W': keys[pygame.K_w],
            'S': keys[pygame.K_s],
            'A': keys[pygame.K_a],
            'D': keys[pygame.K_d],
            'Q': self.Q,
            'left': keys[pygame.K_LEFT],
            'right': keys[pygame.K_RIGHT],
            'E': self.E,
            'space': self.SPACE,
            'R': self.R,
            'up_pressed': self.UP,
            'down_pressed': self.DOWN,
            'left_pressed': self.LEFT,
            'right_pressed': self.RIGHT,
            'esc': self.ESCAPE,
        }

        self.E = False
        self.R = False
        self.Q = False
        self.SPACE = False
        self.UP = False
        self.DOWN = False
        self.LEFT = False
        self.RIGHT = False
        self.ESCAPE = False

        return actions

    def handle_event(self, event):
        """Запоминает одноразовые действия по событию KEYDOWN."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                self.E = True
            if event.key == pygame.K_r:
                self.R = True
            if event.key == pygame.K_SPACE:
                self.SPACE = True
            if event.key == pygame.K_q:
                self.Q = True
            if event.key == pygame.K_UP:
                self.UP = True
            if event.key == pygame.K_DOWN:
                self.DOWN = True
            if event.key == pygame.K_LEFT:
                self.LEFT = True
            if event.key == pygame.K_RIGHT:
                self.RIGHT = True
            if event.key == pygame.K_ESCAPE:
                self.ESCAPE = True
