from src.core.config import *
from math import cos, sin
from src.systems.map_system import get_cell, get_front_cell

def get_door(x, y):
    '''
    Возвращает объект двери по переданным координатам
    '''
    cell = get_cell(x, y)
    return doors.get(cell)


def open_door(player):
    '''
    Пытается открыть дверь, находящуюся перед игроком
    Если перед игроком есть дверь, вызывается её метод open()
    '''
    cell = get_front_cell(player)

    if cell in doors:
        return doors[cell].open()

    return False


def update_doors():
    '''
    Обновляет состояние всех дверей на карте
    '''
    for door in doors.values():
        door.update()