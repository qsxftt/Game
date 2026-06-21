'''Логика загрузки и переключения секторов'''

from src.core.config import TOTAL_SECTORS, block_size
from src.models.enemy import Dwarf, Dwarf2
from src.models.game_state import GameState
from src.models.level import Level
from src.models.pickup import Ammo, MedKit
from src.models.player import Player
from src.systems.level_generator import LevelGenerator
from src.systems.map_system import get_front_cell
from src.systems.prd_system import PRD


def all_enemies_dead(enemies):
    '''Возвращает True, если все враги сектора мертвы'''
    return all(not enemy.alive for enemy in enemies)

def activate_terminal(player, level):
    '''Проверяет, смотрит ли игрок на клетку терминала'''
    cell = get_front_cell(player)

    if cell == level.terminal_pos:
        return True

    return False

def load_sector(state):
    '''Генерирует сектор и создает его игровые сущности

    Args:
        state: общее состояние игровой сессии
    '''
    generator = create_generator_for_sector(state.sector_index)
    text_map = generator.generate()
    level = Level(block_size, text_map)

    state.current_level = level
    if not state.player:
        state.player = Player(*state.current_level.player_start)
    else:
        state.player.set_start_pos(*state.current_level.player_start)

    state.enemies = []
    for x, y in state.current_level.enemies_pos:
        if state.enemy_prd.roll():
            state.enemies.append(Dwarf2(x, y))
        else:
            state.enemies.append(Dwarf(x, y))

    state.pickups = []
    state.reset_sector_flags()

    for x, y, pickup_type in state.current_level.pickups_pos:
        if pickup_type == 'medkit':
            state.pickups.append(MedKit(x, y))
        elif pickup_type == 'ammo':
            state.pickups.append(Ammo(x, y))

def start_new_game(state, game_mode):
    '''Сбрасывает прошлую сессию и создает первый сектор

    Args:
        state: общее состояние игровой сессии
        game_mode: выбранный режим игры
    '''
    state.sector_index = 0
    state.score = 0
    state.game_mode = game_mode

    state.current_level = None
    state.player = None
    state.enemies = []
    state.pickups = []
    state.enemy_prd = PRD(0.1)

    state.reset_sector_flags()
    load_sector(state)

def go_to_next_sector(state):
    '''Переходит к следующему сектору

    Args:
        state: общее состояние игровой сессии

    Returns:
        True, если новый сектор загружен, иначе False
    '''
    state.sector_index += 1

    if state.game_mode == GameState.ENDLESS or state.sector_index < TOTAL_SECTORS:
        load_sector(state)
        return True

    return False

def create_generator_for_sector(sector_index):
    '''Создает генератор с параметрами сложности сектора

    Args:
        sector_index: индекс создаваемого сектора

    Returns:
        Настроенный генератор уровня
    '''
    i = min(sector_index, 4)

    widths = [20, 24, 28, 32, 36]
    heights = [16, 18, 20, 22, 24]
    enemies = [1, 3, 5, 7, 10]
    ammos = [2, 3, 4, 5, 6]
    medkits = [1, 1, 2, 2, 3]
    max_room_sizes = [5, 5, 6, 7, 8]
    bsp_depths = [2, 2, 3, 3, 3]

    extra = max(0, sector_index - 4)

    enemy_count = min(enemies[i] + extra, 25)
    ammo_count = min(ammos[i] + extra // 2, 12)
    medkit_count = min(medkits[i] + extra // 4, 6)

    return LevelGenerator(
        width=widths[i],
        height=heights[i],
        enemy_count=enemy_count,
        medkit_count=medkit_count,
        ammo_count=ammo_count,
        min_room_size=3,
        max_room_size=max_room_sizes[i],
        bsp_max_depth=bsp_depths[i],
        bsp_min_leaf_size=8,
    )
