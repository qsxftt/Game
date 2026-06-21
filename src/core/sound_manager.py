'''Загрузка и воспроизведение звуков Project GATE'''

import pygame

SOUND_PATHS = {
    'pistol_shot': 'assets/sounds/pistol_shot.wav',
    'pistol_reload': 'assets/sounds/pistol_reload.wav',
    'shotgun_shot': 'assets/sounds/shotgun_shot.wav',
    'shotgun_reload': 'assets/sounds/shotgun_reload.wav',
    'enemy_basic_attack': 'assets/sounds/enemy_basic_attack.wav',
    'enemy_heavy_attack': 'assets/sounds/enemy_heavy_attack.wav',
    'enemy_death': 'assets/sounds/enemy_death.wav',
    'player_hurt': 'assets/sounds/player_hurt.wav',
    'door_open': 'assets/sounds/door_open.wav',
    'door_close': 'assets/sounds/door_close.wav',
    'medkit_pickup': 'assets/sounds/medkit_pickup.wav',
    'ammo_pickup': 'assets/sounds/ammo_pickup.wav',
    'terminal_activate': 'assets/sounds/terminal_activate.wav',
    'menu_select': 'assets/sounds/menu_select.wav',
}

AMBIENT_PATH = 'assets/sounds/laboratory_ambient.ogg'


class SoundManager:
    '''Управляет звуковыми эффектами, музыкой и общей громкостью'''

    def __init__(self):
        '''Создает пустое хранилище звуков с громкостью 50%'''
        self.sounds = {}
        self.volume = 0.5
        self.music_loaded = False

    def load_sound(self, name, path):
        '''Загружает звуковой эффект и сохраняет его под именем'''
        sound = pygame.mixer.Sound(path)
        sound.set_volume(self.volume)
        self.sounds[name] = sound

    def play_sound(self, name):
        '''Воспроизводит эффект и сообщает, был ли он найден'''
        sound = self.sounds.get(name)

        if sound is None:
            return False

        sound.play()
        return True

    def load_music(self, path):
        '''Загружает фоновую музыку и применяет громкость'''
        pygame.mixer.music.load(path)
        pygame.mixer.music.set_volume(self.volume * 0.5)
        self.music_loaded = True

    def play_music(self):
        '''Запускает загруженную музыку в бесконечном цикле'''
        if not self.music_loaded:
            return False

        pygame.mixer.music.play(-1)
        return True

    def stop_music(self):
        '''Останавливает фоновую музыку'''
        pygame.mixer.music.stop()

    def set_volume(self, volume):
        '''Устанавливает общую громкость в диапазоне от 0 до 1'''
        self.volume = max(0.0, min(volume, 1.0))

        for sound in self.sounds.values():
            sound.set_volume(self.volume)

        pygame.mixer.music.set_volume(self.volume * 0.5)

    def load_all(self):
        '''Загружает все зарегистрированные эффекты и ambient'''
        for name, path in SOUND_PATHS.items():
            self.load_sound(name, path)

        self.load_music(AMBIENT_PATH)
