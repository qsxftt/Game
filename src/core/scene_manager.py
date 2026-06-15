class SceneManager:
    def __init__(self):
        self.scenes = {}
        self.current_scene = None

    def register(self, name, scene):
        self.scenes[name] = scene

    def change_scene(self, name):
        self.current_scene = self.scenes[name]

    def handle_event(self, event):
        if self.current_scene:
            self.current_scene.handle_event(event)

    def update(self, actions):
        if self.current_scene:
            self.current_scene.update(actions)

    def render(self, screen):
        if self.current_scene:
            self.current_scene.render(screen)
    

    

    

    