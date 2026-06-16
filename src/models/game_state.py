"""Общее состояние текущей игровой сессии."""


class GameState:
    """Хранит активную сцену, сектор и основные игровые сущности."""

    PLAYING = 'playing'
    SECTOR_CLEAR = 'sector_clear'
    GAME_OVER = 'game_over'
    FINAL_VICTORY = 'final_victory'
    MAIN_MENU = 'main_menu'

    def __init__(self):
        """Создает начальное состояние игры."""
        self.sector_index = 0
        self.sector_clean = False
        self.terminal_activated = False
        self.current_level = None
        self.player = None
        self.enemies = []
        self.pickups = []
        self.running = True

    def reset_sector_flags(self):
        """Сбрасывает флаги, которые относятся только к текущему сектору."""
        self.sector_clean = False
        self.terminal_activated = False
