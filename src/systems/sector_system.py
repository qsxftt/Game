from src.systems.map_system import get_front_cell
from src.core.config import current_level


def all_enemies_dead(enemies):
    return all(not enemy.alive for enemy in enemies)

def activate_terminal(player):
    cell = get_front_cell(player)

    if cell == current_level.terminal_pos:
        print('терминал ативирован')
        return True
    
    return False