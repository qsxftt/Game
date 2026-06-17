"""Логика загрузки и переключения секторов."""

from src.core.config import TOTAL_SECTORS, block_size
from src.models.enemy import Dwarf
from src.models.level import Level
from src.models.pickup import Ammo, MedKit
from src.models.player import Player
from src.systems.level_generator import LevelGenerator
from src.systems.map_system import get_front_cell


def all_enemies_dead(enemies):
    """Возвращает True, если все враги сектора мертвы."""
    return all(not enemy.alive for enemy in enemies)


def activate_terminal(player, level):
    """Проверяет, смотрит ли игрок на клетку терминала."""
    cell = get_front_cell(player)

    if cell == level.terminal_pos:
        return True

    return False


def load_sector(state):
    """Генерирует сектор и пересоздает состояние игрока, врагов и ресурсов."""
    generator = create_generator_for_sector(state.sector_index)
    text_map = generator.generate()
    level = Level(block_size, text_map)

    state.current_level = level
    state.player = Player(*state.current_level.player_start)
    state.enemies = [Dwarf(x, y) for x, y in state.current_level.enemies_pos]
    state.pickups = []
    state.reset_sector_flags()

    for x, y, pickup_type in state.current_level.pickups_pos:
        if pickup_type == 'medkit':
            state.pickups.append(MedKit(x, y))
        elif pickup_type == 'ammo':
            state.pickups.append(Ammo(x, y))


def go_to_next_sector(state):
    """Переходит к следующему сектору или сообщает, что игра дошла до финала."""
    state.sector_index += 1

    if state.sector_index < TOTAL_SECTORS:
        load_sector(state)
        return True

    return False


def create_generator_for_sector(sector_index):
    """Создает генератор с параметрами сложности для указанного сектора."""
    return LevelGenerator(
        width=24 + sector_index * 2,
        height=20 + sector_index,
        enemy_count=1 + sector_index,
        medkit_count=1,
        ammo_count=1 + sector_index,
        min_room_size=3,
        max_room_size=5 + sector_index,
        bsp_max_depth=2 + sector_index // 2,
        bsp_min_leaf_size=8
    )
