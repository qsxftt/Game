'''Начисление очков за врагов и завершенные секторы'''

SECTOR_COMPLETE_SCORE = 500


def update_score(state):
    '''Однократно начисляет очки за уничтоженных врагов

    Args:
        state: общее состояние игровой сессии
    '''
    for enemy in state.enemies:
        if not enemy.alive and not enemy.score_awarded:
            state.score += enemy.score_value
            enemy.score_awarded = True

def add_sector_score(state):
    '''Начисляет очки за завершение сектора

    Args:
        state: общее состояние игровой сессии
    '''
    state.score += SECTOR_COMPLETE_SCORE
