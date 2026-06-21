'''Менеджер игровых сцен'''


# ============================================================
# FSM ИГРОВЫХ СЦЕН
# ============================================================


class SceneManager:
    '''Хранит сцены и перенаправляет update/render в текущую сцену'''

    def __init__(self):
        '''Создает пустой менеджер сцен'''
        self.scenes = {}
        self.current_scene = None

    def register(self, name, scene):
        '''Регистрирует сцену по строковому имени'''
        self.scenes[name] = scene

    def change_scene(self, name):
        '''Переключает текущую сцену'''
        self.current_scene = self.scenes[name]

    def update(self, actions):
        '''Обновляет текущую сцену'''
        if self.current_scene:
            self.current_scene.update(actions)

    def render(self, screen):
        '''Рисует текущую сцену'''
        if self.current_scene:
            self.current_scene.render(screen)
