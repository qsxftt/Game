from src.systems.map_system import get_front_cell
from src.models.level import Level
from src.models.player import Player
from src.models.enemy import Dwarf
from src.models.pickup import MedKit, Ammo
from src.systems.level_generator import LevelGenerator
from src.core.config import *

def all_enemies_dead(enemies):
    return all(not enemy.alive for enemy in enemies)

def activate_terminal(player, level):
    cell = get_front_cell(player)

    if cell == level.terminal_pos:
        return True
    
    return False

def load_sector(state):
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
    state.sector_index += 1
    if state.sector_index < TOTAL_SECTORS:
        load_sector(state)
        return True 
    else:
        return False
    
def create_generator_for_sector(sector_index):
    return LevelGenerator(
        width=12 + sector_index * 2,
        height=8 + sector_index,
        enemy_count=1 + sector_index,
        medkit_count=1,
        ammo_count=1 + sector_index
    )