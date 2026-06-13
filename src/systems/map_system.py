from math import cos, sin
from src.core.config import *


def get_cell(x, y):
    '''
    Возвращает координаты клетки карты по переданным координатам
    '''
    endX = x // block_size * block_size
    endY = y // block_size * block_size

    return endX, endY


def get_front_cell(player):
    '''
    Возвращает координаты клетки, находящейся перед игроком
    '''
    front_x = player.x + cos(player.angle) * block_size
    front_y = player.y + sin(player.angle) * block_size

    cell = get_cell(front_x, front_y)

    return cell

def get_block_type(x, y):
    '''
    Возвращает тип блока в указанной клетке карты
    '''
    cell = get_cell(x, y)

    if cell in block_map:
        return 'wall'

    if cell in doors and doors[cell].open_progress < 1.0:
        return 'door'

    return None