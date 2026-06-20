class DisplaySettings:
    """Хранит изменяемые настройки окна."""

    def __init__(self):
        self.resolutions = [
            (1280, 800),
            (1600, 1000),
            (1920, 1200),
        ]
        self.resolution_index = 0
        self.fullscreen = False
        self.changed = False

    @property
    def resolution(self):
        return self.resolutions[self.resolution_index]

    def change_resolution(self, direction):
        self.resolution_index = (
            self.resolution_index + direction
        ) % len(self.resolutions)
        self.changed = True

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        self.changed = True