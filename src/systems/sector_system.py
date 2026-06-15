from src.systems.map_system import get_front_cell
from src.models.level import Level
from src.models.player import Player
from src.models.enemy import Dwarf
from src.core.config import *

def all_enemies_dead(enemies):
    return all(not enemy.alive for enemy in enemies)

def activate_terminal(player, level):
    cell = get_front_cell(player)

    if cell == level.terminal_pos:
        return True
    
    return False

def load_sector(state):
    level = Level(block_size, sector_maps[state.sector_index])
    state.current_level = level
    state.player = Player(*state.current_level.player_start)
    state.enemies = [Dwarf(x, y) for x, y in state.current_level.enemies_pos]
    state.reset_sector_flags()

def go_to_next_sector(state):
    state.sector_index += 1
    if state.sector_index < len(sector_maps):
        load_sector(state)
        return True 
    else:
        return False