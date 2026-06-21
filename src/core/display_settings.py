'''Настройки разрешения и полноэкранного режима'''


class DisplaySettings:
    '''Хранит изменяемые настройки окна'''

    def __init__(self):
        '''Создает настройки окна со стартовым разрешением'''
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
        '''Возвращает выбранное разрешение окна'''
        return self.resolutions[self.resolution_index]

    def change_resolution(self, direction):
        '''Переключает разрешение на соседний вариант'''
        self.resolution_index = (self.resolution_index + direction) % len(
            self.resolutions
        )
        self.changed = True

    def toggle_fullscreen(self):
        '''Переключает полноэкранный режим'''
        self.fullscreen = not self.fullscreen
        self.changed = True
