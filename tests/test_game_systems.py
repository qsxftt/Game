'''Тесты игровых систем и условий перехода'''

from types import SimpleNamespace

import src.systems.combat_system as combat_system
import src.systems.prd_system as prd_system
import src.systems.sector_system as sector_system
from src.models.door import Door
from src.models.enemy import Dwarf
from src.models.game_state import GameState
from src.systems.collision_system import is_wall
from src.systems.prd_system import PRD


def test_collision_detects_walls_doors_and_terminal():
    '''Коллизия различает препятствия и свободный пол'''
    door = Door(100, 100, 'vert', 100)
    level = SimpleNamespace(
        block_map={(0, 0)},
        doors={(100, 100): door},
        terminal_pos=(200, 200),
    )

    assert is_wall(50, 50, level) is True
    assert is_wall(150, 150, level) is True
    assert is_wall(250, 250, level) is True
    assert is_wall(350, 350, level) is False

    door.open_progress = 0.8

    assert is_wall(150, 150, level) is False


def test_player_shoot_damages_nearest_enemy(monkeypatch):
    '''Выстрел наносит урон ближайшему врагу под прицелом'''
    monkeypatch.setattr(
        combat_system,
        'enemy_near_crosshair',
        lambda enemy, player, level: True,
    )
    weapon = SimpleNamespace(damage=35, attack_distance=500)
    player = SimpleNamespace(x=0, y=0, weapon=weapon)
    near_enemy = Dwarf(100, 0)
    far_enemy = Dwarf(200, 0)

    target = combat_system.player_shoot(
        player,
        [far_enemy, near_enemy],
        level=None,
    )

    assert target is near_enemy
    assert near_enemy.health == 65
    assert far_enemy.health == 100


def test_prd_increases_chance_and_resets_after_success(monkeypatch):
    '''PRD повышает шанс после неудачи и сбрасывает после успеха'''
    values = iter([0.9, 0.3])
    monkeypatch.setattr(prd_system, 'random', lambda: next(values))
    distribution = PRD(0.2)

    assert distribution.roll() is False
    assert distribution.current_chance == 0.4
    assert distribution.roll() is True
    assert distribution.current_chance == 0.2


def test_all_enemies_dead_checks_every_enemy():
    '''Сектор считается чистым только после смерти всех врагов'''
    enemies = [SimpleNamespace(alive=False), SimpleNamespace(alive=True)]

    assert sector_system.all_enemies_dead(enemies) is False

    enemies[1].alive = False

    assert sector_system.all_enemies_dead(enemies) is True


def test_campaign_stops_after_fifth_sector(monkeypatch):
    '''Кампания завершается после пятого сектора'''
    loaded_sectors = []
    monkeypatch.setattr(
        sector_system,
        'load_sector',
        lambda state: loaded_sectors.append(state.sector_index),
    )

    state = SimpleNamespace(sector_index=3, game_mode=GameState.CAMPAIGN)

    assert sector_system.go_to_next_sector(state) is True
    assert loaded_sectors == [4]

    assert sector_system.go_to_next_sector(state) is False
    assert state.sector_index == 5


def test_endless_mode_keeps_loading_sectors(monkeypatch):
    '''Бесконечный режим продолжает создавать уровни после пятого сектора'''
    loaded_sectors = []
    monkeypatch.setattr(
        sector_system,
        'load_sector',
        lambda state: loaded_sectors.append(state.sector_index),
    )
    state = SimpleNamespace(sector_index=10, game_mode=GameState.ENDLESS)

    assert sector_system.go_to_next_sector(state) is True
    assert loaded_sectors == [11]
