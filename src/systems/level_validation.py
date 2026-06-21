'''Проверка сгенерированной текстовой карты на достижимость важных объектов'''


def get_walkable_cells(text_map):
    '''Возвращает все клетки, по которым можно ходить'''
    walkable = set()

    for y, row in enumerate(text_map):
        for x, tile in enumerate(row):
            if tile in ('.', 'P', 'E', 'H', 'A', 'C', 'D'):
                walkable.add((x, y))

    return walkable


def find_tile(text_map, target_tile):
    '''Возвращает первую позицию указанного тайла или None'''
    for y, row in enumerate(text_map):
        for x, tile in enumerate(row):
            if tile == target_tile:
                return x, y

    return None


def find_all_tiles(text_map, target_tile):
    '''Возвращает все позиции указанного тайла'''
    pos = []

    for y, row in enumerate(text_map):
        for x, tile in enumerate(row):
            if tile == target_tile:
                pos.append((x, y))

    return pos


def get_neighbors(cell):
    '''Возвращает четыре соседние клетки'''
    x, y = cell

    return [
        (x + 1, y),
        (x - 1, y),
        (x, y + 1),
        (x, y - 1),
    ]


def get_reachable_cells(text_map, start):
    '''Находит все достижимые клетки через BFS от стартовой позиции'''
    walkable = get_walkable_cells(text_map)

    visited = set()
    queue = [start]

    while queue:
        current = queue.pop(0)

        if current in visited:
            continue

        visited.add(current)

        for neighbor in get_neighbors(current):
            if neighbor in walkable and neighbor not in visited:
                queue.append(neighbor)

    return visited


def all_pos_reachable(positions, reachable):
    '''Проверяет, входят ли все позиции в множество достижимых клеток'''
    for pos in positions:
        if pos not in reachable:
            return False

    return True


def reachable_neighbor(tile, reachable):
    '''Проверяет, есть ли рядом с тайлом хотя бы одна достижимая клетка'''
    positions = get_neighbors(tile)

    for pos in positions:
        if pos in reachable:
            return True

    return False


def validate_level(text_map):
    '''Проверяет, что игрок, терминал, враги и ресурсы доступны на карте'''
    player_pos = find_tile(text_map, 'P')

    if player_pos is None:
        return False

    terminal = find_tile(text_map, 'T')

    if terminal is None:
        return False

    reachable = get_reachable_cells(text_map, player_pos)
    enemies = find_all_tiles(text_map, 'E')
    medkits = find_all_tiles(text_map, 'H')
    ammos = find_all_tiles(text_map, 'A')
    doors = find_all_tiles(text_map, 'D')

    if not all_pos_reachable(doors, reachable):
        return False

    if not all_pos_reachable(enemies, reachable):
        return False

    if not all_pos_reachable(medkits, reachable):
        return False

    if not all_pos_reachable(ammos, reachable):
        return False

    if not reachable_neighbor(terminal, reachable):
        return False

    return True
