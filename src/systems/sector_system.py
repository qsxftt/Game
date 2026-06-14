from src.systems.map_system import get_front_cell


def all_enemies_dead(enemies):
    return all(not enemy.alive for enemy in enemies)

def activate_terminal(player, level):
    cell = get_front_cell(player)

    if cell == level.terminal_pos:
        return True
    
    return False