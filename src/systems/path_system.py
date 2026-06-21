'''A* поиск пути по текстовой карте уровня'''

from heapq import heappop, heappush

WALKABLE_TILES = {'.', 'P', 'E', 'H', 'A', 'C', 'D'}


def get_neighbors(cell, text_map):
    '''Возвращает соседние клетки внутри границ карты'''
    x, y = cell
    height = len(text_map)
    width = len(text_map[0])

    near = [
        (x + 1, y),
        (x - 1, y),
        (x, y + 1),
        (x, y - 1),
    ]

    valid_near = []

    for near_x, near_y in near:
        if 0 <= near_x < width and 0 <= near_y < height:
            valid_near.append((near_x, near_y))

    return valid_near


def heuristic(a, b):
    '''Возвращает манхэттенское расстояние между двумя клетками'''
    x1, y1 = a
    x2, y2 = b

    return abs(x1 - x2) + abs(y1 - y2)


def build_path(came_from, start, end):
    '''Восстанавливает путь от старта до цели по словарю came_from'''
    current = end
    path = []

    while current != start:
        path.append(current)
        current = came_from[current]

    path.append(start)
    path.reverse()

    return path


def find_path(text_map, start, end):
    '''Ищет путь от start до end через проходимые клетки карты'''
    frontier = []
    heappush(frontier, (0, start))

    came_from = {}
    cost_so_far = {}

    came_from[start] = None
    cost_so_far[start] = 0

    while frontier:
        current_priority, current = heappop(frontier)

        if current_priority > cost_so_far[current] + heuristic(current, end):
            continue

        if current == end:
            break

        for next_cell in get_neighbors(current, text_map):
            next_x, next_y = next_cell

            if text_map[next_y][next_x] not in WALKABLE_TILES:
                continue

            new_cost = cost_so_far[current] + 1

            if next_cell not in cost_so_far or new_cost < cost_so_far[next_cell]:
                cost_so_far[next_cell] = new_cost
                priority = new_cost + heuristic(next_cell, end)
                heappush(frontier, (priority, next_cell))
                came_from[next_cell] = current

    if end not in came_from:
        return []

    return build_path(came_from, start, end)
