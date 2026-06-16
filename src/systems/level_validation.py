def get_walkable_cells(text_map):
    walkable = set()

    for y, row in enumerate(text_map):
        for x, tile in enumerate(row):
            if tile in ('.', 'P', 'E', 'H', 'A'):
                walkable.add((x, y))

    return walkable

def find_tile(text_map, target_tile):
    for y, row in enumerate(text_map):
        for x, tile in enumerate(row):
            if tile == target_tile:
                return x, y
            
    return None

def get_neighbors(cell):
    x, y = cell

    return [
        (x + 1, y),
        (x - 1, y),
        (x, y + 1),
        (x, y - 1)
    ]

def get_reachable_cells(text_map, start):
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

def find_all_tiles(text_map, target_tile):
    pos = []

    for y, row in enumerate(text_map):
        for x, tile in enumerate(row):
            if tile == target_tile:
                pos.append((x, y))

    return pos

def all_pos_reachable(positions, reachable):
    for pos in positions:
        if pos not in reachable:
            return False
        
    return True

def reachable_neighbor(tile, reachable):
    positions = get_neighbors(tile)

    for pos in positions:
        if pos in reachable:
            return True
        
    return False

def validate_level(text_map):
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

    if not all_pos_reachable(enemies, reachable):
        return False
    
    if not all_pos_reachable(medkits, reachable):
        return False
    
    if not all_pos_reachable(ammos, reachable):
        return False
    
    if not reachable_neighbor(terminal, reachable):
        return False
    
    return True
