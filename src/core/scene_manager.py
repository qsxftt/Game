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
        '''Регистрирует сцену по строковому имени

        Args:
            name: уникальное имя сцены
            scene: объект регистрируемой сцены
        '''
        self.scenes[name] = scene

    def change_scene(self, name):
        '''Переключает текущую сцену

        Args:
            name: имя ранее зарегистрированной сцены
        '''
        self.current_scene = self.scenes[name]

    def update(self, actions):
        '''Обновляет текущую сцену

        Args:
            actions: словарь действий пользователя
        '''
        if self.current_scene:
            self.current_scene.update(actions)

    def render(self, screen):
        '''Рисует текущую сцену

        Args:
            screen: внутренняя поверхность игры
        '''
        if self.current_scene:
            self.current_scene.render(screen)
