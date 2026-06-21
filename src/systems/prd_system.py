from random import random


class PRD:
    def __init__(self, base_chance):
        self.base_chance = base_chance
        self.current_chance = base_chance

    def roll(self):
        if random() < self.current_chance:
            self.current_chance = self.base_chance
            return True
        
        self.current_chance = min(1.0, self.current_chance + self.base_chance)
        
        return False

    