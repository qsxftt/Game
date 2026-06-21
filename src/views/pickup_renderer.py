'''Renderer подбираемых ресурсов'''

import pygame

from src.core.config import (
    AMMO_TEXTURE,
    HEIGHT,
    MEDKIT_TEXTURE,
    SCREEN_DISTANCE,
    block_size,
)
from src.models.pickup import Ammo, MedKit
from src.systems.visibility_system import get_depth, get_screen_x, is_in_fov, is_visible

PICKUP_TEXTURES = {
    Ammo: {
        'texture': AMMO_TEXTURE,
        'frame_count': 1,
    },
    MedKit: {
        'texture': MEDKIT_TEXTURE,
        'frame_count': 1,
    },
}

def convert_pickup_textures():
    '''Оптимизирует прозрачные текстуры ресурсов под формат дисплея'''
    for visual in PICKUP_TEXTURES.values():
        visual['texture'] = visual['texture'].convert_alpha()


class PickupRender:
    '''Рисует pickups как псевдо-3D спрайты'''

    def get_frame(self, pickup):
        '''Выбирает текущий кадр анимации ресурса

        Args:
            pickup: отображаемый ресурс

        Returns:
            Кадр и его исходные размеры
        '''
        visual = PICKUP_TEXTURES[type(pickup)]
        texture = visual['texture']
        frame_count = visual['frame_count']

        frame_width = texture.get_width() / frame_count
        frame_height = texture.get_height()

        frame_index = round(
            (1 - pickup.animation_cooldown / pickup.animation_speed) * (frame_count - 1)
        )
        x = frame_index * frame_width

        frame = texture.subsurface(x, 0, frame_width, frame_height)

        return frame, frame_width, frame_height

    def draw(self, pickup, screen, player, level):
        '''Рисует видимый ресурс как псевдо-3D спрайт

        Args:
            pickup: отображаемый ресурс
            screen: внутренняя поверхность игры
            player: модель игрока
            level: текущий уровень
        '''
        if pickup.is_pickedup:
            return False

        if not is_in_fov(pickup, player):
            return False

        if not is_visible(pickup, player, level):
            return False

        frame, frame_width, frame_height = self.get_frame(pickup)

        depth = max(get_depth(pickup, player), 50)
        screen_x = get_screen_x(pickup, player)
        pickup_height = int(block_size * SCREEN_DISTANCE / depth * 0.5)
        pickup_width = int(frame_width * pickup_height / frame_height)

        frame = pygame.transform.scale(frame, (pickup_width, pickup_height))
        screen.blit(
            frame, (screen_x - pickup_width // 2, (HEIGHT - pickup_height // 2) * 0.55)
        )
