'''Тесты BFS-валидации и генерации уровней'''

from src.systems.level_generator import LevelGenerator
from src.systems.level_validation import get_reachable_cells, validate_level


def test_bfs_finds_reachable_cells():
    '''BFS обходит только связанную свободную область'''
    text_map = [
        'WWWWW',
        'WP..W',
        'W.W.W',
        'W...W',
        'WWWWW',
    ]

    reachable = get_reachable_cells(text_map, (1, 1))

    assert (3, 3) in reachable
    assert (2, 2) not in reachable


def test_validate_level_rejects_unreachable_enemy():
    '''Валидация отклоняет карту с изолированным врагом'''
    text_map = [
        'WWWWWWW',
        'WP...TW',
        'WWWWWWW',
        'WE....W',
        'WWWWWWW',
    ]

    assert validate_level(text_map) is False


def test_generated_level_contains_required_objects():
    '''Генератор создаёт валидную карту с нужными объектами'''
    generator = LevelGenerator(
        width=20,
        height=16,
        enemy_count=2,
        medkit_count=1,
        ammo_count=1,
        min_room_size=3,
        max_room_size=5,
        bsp_max_depth=2,
        bsp_min_leaf_size=8,
    )

    text_map = generator.generate()
    all_tiles = ''.join(text_map)

    assert validate_level(text_map) is True
    assert all_tiles.count('P') == 1
    assert all_tiles.count('T') == 1
    assert all_tiles.count('E') == 2
    assert all_tiles.count('H') == 1
    assert all_tiles.count('A') == 1
