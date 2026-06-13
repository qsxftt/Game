import pygame


class InputController:
    def get_actions(self):
        keys = pygame.key.get_pressed()

        actions = {
            'W': keys[pygame.K_w],
            'S': keys[pygame.K_s],
            'A': keys[pygame.K_a],
            'D': keys[pygame.K_d],
            'left': keys[pygame.K_LEFT],
            'right': keys[pygame.K_RIGHT],
            'E': keys[pygame.K_e],
            'space': keys[pygame.K_SPACE],
            'R': keys[pygame.K_r]
        }

        return actions