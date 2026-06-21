'''Renderer оружия игрока'''

import pygame

from src.core.config import (
    HEIGHT_HALF,
    PISTOL_TEXTURE,
    PISTOLR_TEXTURE,
    SHOTGUN_TEXTURE,
    SHOTGUNR_TEXTURE,
    WIDTH,
)
from src.models.weapon import Pistol, Shotgun

WEAPON_TEXTURES = {
    Pistol: {
        'main': PISTOL_TEXTURE,
        'reload': PISTOLR_TEXTURE,
        'frame_count': 5,
    },
    Shotgun: {
        'main': SHOTGUN_TEXTURE,
        'reload': SHOTGUNR_TEXTURE,
        'frame_count': 5,
    },
}


def convert_weapon_textures():
    '''Оптимизирует прозрачные текстуры оружия под формат дисплея'''
    for textures in WEAPON_TEXTURES.values():
        textures['main'] = textures['main'].convert_alpha()
        textures['reload'] = textures['reload'].convert_alpha()


class WeaponRender:
    '''Рисует оружие от первого лица'''

    def get_frame(self, weapon, texture, frame_count, status=None):
        '''Возвращает текущий кадр анимации оружия'''
        frame_width = texture.get_width() // frame_count
        frame_height = texture.get_height()

        if status == 'shoot':
            frame_index = round(
                (1 - weapon.shoot_cooldown / weapon.shoot_delay) * (frame_count - 1)
            )
        elif status == 'reload':
            frame_index = round(
                (1 - weapon.reload_cooldown / weapon.reload_delay) * (frame_count - 1)
            )
        else:
            frame_index = 0

        x = frame_width * frame_index
        frame = texture.subsurface(x, 0, frame_width, frame_height)

        return frame, frame_width, frame_height

    def draw(self, screen, weapon):
        '''Рисует оружие с учетом текущей анимации'''
        textures = WEAPON_TEXTURES[type(weapon)]
        frame_count = textures['frame_count']

        if weapon.shoot_cooldown > 0:
            frame, frame_width, frame_height = self.get_frame(
                weapon, textures['main'], frame_count, 'shoot'
            )
        elif weapon.reload_cooldown > 0:
            frame, frame_width, frame_height = self.get_frame(
                weapon, textures['reload'], frame_count, 'reload'
            )
        else:
            frame, frame_width, frame_height = self.get_frame(
                weapon, textures['main'], frame_count
            )

        screen_width = frame_width * HEIGHT_HALF / frame_height
        frame = pygame.transform.scale(frame, (screen_width, HEIGHT_HALF))

        screen.blit(frame, (WIDTH - screen_width, HEIGHT_HALF))
