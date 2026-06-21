'''Тесты поиска пути A*'''

from src.systems.path_system import WALKABLE_TILES, find_path


def test_find_path_returns_valid_route():
    '''A* находит путь вокруг стены'''
    text_map = [
        'WWWWW',
        'W...W',
        'W.W.W',
        'W...W',
        'WWWWW',
    ]

    path = find_path(text_map, (1, 1), (3, 3))

    assert path[0] == (1, 1)
    assert path[-1] == (3, 3)
    assert all(text_map[y][x] in WALKABLE_TILES for x, y in path)


def test_find_path_returns_empty_list_when_target_is_blocked():
    '''A* возвращает пустой список для недостижимой цели'''
    text_map = [
        'WWWWW',
        'W.W.W',
        'WWWWW',
        'W.W.W',
        'WWWWW',
    ]

    path = find_path(text_map, (1, 1), (3, 3))

    assert path == []
