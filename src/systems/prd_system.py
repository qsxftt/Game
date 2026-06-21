'''Псевдослучайное распределение с растущей вероятностью успеха'''

from random import random


# ============================================================
# PRD - СРЕДНИЙ АЛГОРИТМ
# ============================================================

class PRD:
    '''Повышает вероятность после неудачи и сбрасывает после успеха'''

    def __init__(self, base_chance):
        '''Создает распределение с указанным начальным шансом

        Args:
            base_chance: начальная вероятность успеха от 0 до 1
        '''
        self.base_chance = base_chance
        self.current_chance = base_chance

    def roll(self):
        '''Выполняет случайную попытку и обновляет вероятность

        Returns:
            True при успехе, иначе False
        '''
        if random() < self.current_chance:
            self.current_chance = self.base_chance
            return True

        self.current_chance = min(1.0, self.current_chance + self.base_chance)

        return False
