from src.models.player import Player

class GameState:
    def __init__(self):
        self.mode = 'playing'
        self.sector_index = 0
        self.sector_clean = False
        self.terminal_activated = False
        self.current_level = None
        self.player = None
        self.enemies = []

    def reset_sector_flags(self):
        self.sector_clean = False
        self.terminal_activated = False