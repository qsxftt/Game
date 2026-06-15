class GameState:
    PLAYING = 'playing'
    SECTOR_CLEAR = 'sector_clear'
    GAME_OVER = 'game_over'
    FINAL_VICTORY = 'final_victory'
    MAIN_MENU = 'main_menu'

    def __init__(self):
        self.sector_index = 0
        self.sector_clean = False
        self.terminal_activated = False
        self.current_level = None
        self.player = None
        self.enemies = []
        self.running = True

    def reset_sector_flags(self):
        self.sector_clean = False
        self.terminal_activated = False