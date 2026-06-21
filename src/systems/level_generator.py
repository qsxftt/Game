'''Процедурная генерация BSP-уровней Project GATE'''

from heapq import heappop, heappush
from random import randint as rnd

from src.systems.level_validation import validate_level


# ============================================================
# BSP DUNGEON GENERATION - СЛОЖНЫЙ АЛГОРИТМ
# ============================================================


class Room:
    '''Прямоугольная комната в сетке уровня'''

    def __init__(self, x, y, width, height):
        '''Сохраняет позицию левого верхнего угла и размер комнаты в клетках'''
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def get_center(self):
        '''Возвращает координаты центральной клетки комнаты'''
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2

        return center_x, center_y


class BSPNode:
    '''Узел BSP-дерева: прямоугольная область карты, которую можно разделить'''

    def __init__(self, x, y, width, height, depth=0):
        '''Сохраняет область узла, его глубину и ссылки на дочерние узлы'''
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.depth = depth

        self.left = None
        self.right = None
        self.room = None

    def is_leaf(self):
        '''Возвращает True, если узел больше не разделен на дочерние области'''
        return self.left is None and self.right is None

    def can_split(self, min_leaf_size):
        '''Проверяет, достаточно ли узел большой для следующего разделения'''
        return self.width >= min_leaf_size * 2 or self.height >= min_leaf_size * 2

    def choose_split(self):
        '''Выбирает направление разделения: вертикальное или горизонтальное'''
        if self.width > self.height:
            return 'vert'

        if self.height > self.width:
            return 'hor'

        if rnd(0, 1) == 0:
            return 'vert'

        return 'hor'

    def split(self, min_leaf_size):
        '''Делит текущий узел на два дочерних узла, если места достаточно'''
        if not self.can_split(min_leaf_size):
            return False

        split_type = self.choose_split()

        if split_type == 'vert':
            split_x = rnd(min_leaf_size, self.width - min_leaf_size)

            self.left = BSPNode(self.x, self.y, split_x, self.height, self.depth + 1)

            self.right = BSPNode(
                self.x + split_x,
                self.y,
                self.width - split_x,
                self.height,
                self.depth + 1,
            )

            return True

        if split_type == 'hor':
            split_y = rnd(min_leaf_size, self.height - min_leaf_size)

            self.left = BSPNode(self.x, self.y, self.width, split_y, self.depth + 1)

            self.right = BSPNode(
                self.x,
                self.y + split_y,
                self.width,
                self.height - split_y,
                self.depth + 1,
            )

            return True

        return False

    def split_recursive(self, max_depth, min_leaf_size):
        '''Рекурсивно делит узел, пока не достигнут лимит глубины или размера'''
        if self.depth >= max_depth:
            return

        if not self.split(min_leaf_size):
            return

        self.left.split_recursive(max_depth, min_leaf_size)
        self.right.split_recursive(max_depth, min_leaf_size)

    def get_leaves(self):
        '''Возвращает все конечные узлы BSP-дерева'''
        if self.is_leaf():
            return [self]

        leaves = []
        leaves += self.left.get_leaves()
        leaves += self.right.get_leaves()

        return leaves

    def create_room_inside(self, min_room_size, max_room_size):
        '''Создает комнату внутри области узла с отступом от границ'''
        room_width = rnd(min_room_size, min(max_room_size, self.width - 2))
        room_height = rnd(min_room_size, min(max_room_size, self.height - 2))

        room_x = rnd(self.x + 1, self.x + self.width - room_width - 1)
        room_y = rnd(self.y + 1, self.y + self.height - room_height - 1)

        self.room = Room(room_x, room_y, room_width, room_height)

        return self.room

    def get_room(self):
        '''Возвращает комнату этого узла или первую найденную комнату ниже по дереву'''
        if self.room:
            return self.room

        if self.left:
            room = self.left.get_room()
            if room:
                return room

        if self.right:
            room = self.right.get_room()
            if room:
                return room

        return None


class LevelGenerator:
    '''Создает текстовую карту сектора: комнаты, коридоры, игрока и объекты'''

    def __init__(
        self,
        width=12,
        height=8,
        enemy_count=1,
        medkit_count=1,
        ammo_count=1,
        min_room_size=4,
        max_room_size=6,
        bsp_max_depth=3,
        bsp_min_leaf_size=8,
    ):
        '''Сохраняет параметры генерации текущего сектора'''
        self.width = width
        self.height = height
        self.enemy_count = enemy_count
        self.medkit_count = medkit_count
        self.ammo_count = ammo_count
        self.min_room_size = min_room_size
        self.max_room_size = max_room_size
        self.bsp_max_depth = bsp_max_depth
        self.bsp_min_leaf_size = bsp_min_leaf_size

    # Основной процесс генерации

    def generate(self):
        '''Пробует создать валидную BSP-карту и возвращает ее в текстовом виде'''
        for _ in range(100):
            text_map = self.build_bsp_map()

            if validate_level(text_map):
                return text_map

        raise RuntimeError('Ошибка генерации карты')

    def build_bsp_map(self):
        '''Создает одну BSP-карту без повторных попыток валидации'''
        grid = self.create_filled_grid()

        self.create_bsp_rooms(grid, self.bsp_max_depth, self.bsp_min_leaf_size)

        player_x, player_y = self.get_empty_cell(grid)
        self.place_door(grid)
        self.set_tile(grid, player_x, player_y, 'P')
        self.place_terminal(grid, player_x, player_y, self.max_room_size)
        self.place_far_tiles(
            grid, player_x, player_y, 'E', self.enemy_count, self.max_room_size
        )
        self.place_random_tiles(grid, 'H', self.medkit_count)
        self.place_random_tiles(grid, 'A', self.ammo_count)

        return [''.join(row) for row in grid]

    # Создание базовой сетки

    def create_filled_grid(self):
        '''Создает сетку, полностью заполненную стенами'''
        grid = []

        for y in range(self.height):
            row = []

            for x in range(self.width):
                row.append('W')

            grid.append(row)

        return grid

    # Создание комнат через BSP

    def create_bsp_rooms(self, grid, max_depth=3, min_leaf_size=8):
        '''Создает BSP-дерево, вырезает комнаты в листьях и соединяет их'''
        root = BSPNode(0, 0, self.width, self.height)
        root.split_recursive(max_depth, min_leaf_size)

        rooms = []

        for leaf in root.get_leaves():
            room = leaf.create_room_inside(self.min_room_size, self.max_room_size)
            rooms.append(room)
            self.create_room(grid, room)

        self.connect_bsp_rooms(grid, root)

        return rooms

    def create_room(self, grid, room):
        '''Вырезает комнату в сетке, заменяя стены на пол'''
        for y in range(room.y, room.y + room.height):
            for x in range(room.x, room.x + room.width):
                self.set_tile(grid, x, y, '.')

    # Соединение комнат коридорами

    def connect_bsp_rooms(self, grid, node):
        '''Соединяет комнаты из соседних веток BSP-дерева'''
        if node.is_leaf():
            return

        self.connect_bsp_rooms(grid, node.left)
        self.connect_bsp_rooms(grid, node.right)

        left_room = node.left.get_room()
        right_room = node.right.get_room()

        if left_room and right_room:
            self.create_corridor(grid, left_room, right_room)

    def create_corridor(self, grid, start, end):
        '''Прокладывает коридор между центрами двух комнат'''
        start_point = start.get_center()
        end_point = end.get_center()

        for x, y in self.find_corridor_path(grid, start_point, end_point):
            if grid[y][x] == 'W':
                self.set_tile(grid, x, y, 'C')

    # ============================================================
    # АЛГОРИТМ ДЕЙКСТРЫ
    # ============================================================

    def build_corridor_path(self, came_from, start, end):
        '''Восстанавливает найденный путь коридора от конца к началу'''
        current = end
        path = []

        while current != start:
            path.append(current)
            current = came_from[current]

        path.append(start)
        path.reverse()

        return path

    def find_corridor_path(self, grid, start, end):
        '''Ищет путь коридора алгоритмом Дейкстры с весами тайлов'''
        frontier = []
        heappush(frontier, (0, start))

        came_from = {}
        cost_so_far = {}

        came_from[start] = None
        cost_so_far[start] = 0

        while frontier:
            current_priority, current = heappop(frontier)

            if current_priority > cost_so_far[current]:
                continue

            if current == end:
                break

            for next_cell in self.get_neighbors(*current):
                next_x, next_y = next_cell
                new_cost = cost_so_far[current] + self.get_corridor_cost(
                    grid, next_x, next_y
                )

                if next_cell not in cost_so_far or new_cost < cost_so_far[next_cell]:
                    cost_so_far[next_cell] = new_cost
                    heappush(frontier, (new_cost, next_cell))
                    came_from[next_cell] = current

        return self.build_corridor_path(came_from, start, end)

    # Размещение объектов

    def place_door(self, grid):
        '''Ставит двери в подходящие клетки коридоров'''
        doors = []

        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if self.can_place_door(grid, x, y):
                    if not self.is_near_door(doors, x, y):
                        doors.append((x, y))

        for x, y in doors:
            self.set_tile(grid, x, y, 'D')

    def place_terminal(self, grid, x, y, distance):
        '''Ставит терминал в стену рядом ровно с одной свободной клеткой'''
        while True:
            wall_x, wall_y = self.get_far_cell_wall(grid, x, y, distance)
            if self.can_place_terminal(grid, wall_x, wall_y):
                self.set_tile(grid, wall_x, wall_y, 'T')
                return

    def place_random_tiles(self, grid, tile, count):
        '''Ставит несколько тайлов в случайные свободные клетки комнат'''
        for _ in range(count):
            self.set_tile(grid, *self.get_empty_cell(grid), tile)

    def place_far_tiles(self, grid, x, y, tile, count, distance=4):
        '''Ставит несколько тайлов на расстоянии от указанной клетки'''
        for _ in range(count):
            self.set_tile(grid, *self.get_far_cell(grid, x, y, distance), tile)

    # Проверки размещения объектов

    def can_place_door(self, grid, x, y):
        '''Проверяет, подходит ли клетка коридора для двери'''
        if grid[y][x] != 'C':
            return False

        up = grid[y - 1][x]
        down = grid[y + 1][x]
        left = grid[y][x - 1]
        right = grid[y][x + 1]

        if up == 'W' and down == 'W' and (left == '.' or right == '.'):
            return True

        if left == 'W' and right == 'W' and (up == '.' or down == '.'):
            return True

        return False

    def can_place_terminal(self, grid, wall_x, wall_y):
        '''Проверяет, можно ли поставить терминал в выбранную стену'''
        near = [
            (wall_x + 1, wall_y),
            (wall_x - 1, wall_y),
            (wall_x, wall_y + 1),
            (wall_x, wall_y - 1),
        ]
        count = 0

        for x, y in near:
            if 0 <= x < self.width and 0 <= y < self.height:
                if grid[y][x] in ('D', 'C'):
                    return False
                if self.is_empty(grid, x, y):
                    count += 1

        return count == 1

    def is_near_door(self, doors, x, y, min_distance=3):
        '''Проверяет, расположена ли рядом уже созданная дверь'''
        for door_x, door_y in doors:
            if self.get_cell_distance(door_x, door_y, x, y) < min_distance:
                return True

        return False

    # Работа с клетками

    def set_tile(self, grid, x, y, tile):
        '''Записывает символ тайла в указанную клетку сетки'''
        grid[y][x] = tile

    def is_empty(self, grid, x, y):
        '''Проверяет, является ли клетка свободным полом комнаты'''
        return grid[y][x] == '.'

    def get_empty_cell(self, grid):
        '''Возвращает случайную свободную клетку комнаты'''
        while True:
            x = rnd(1, self.width - 2)
            y = rnd(1, self.height - 2)
            if self.is_empty(grid, x, y):
                return x, y

    def get_wall_cell(self, grid):
        '''Возвращает случайную клетку стены'''
        while True:
            x = rnd(0, self.width - 1)
            y = rnd(0, self.height - 1)
            if grid[y][x] == 'W':
                return x, y

    # Расстояния

    def is_near_room(self, grid, x, y):
        '''Проверяет соседство клетки со свободным полом комнаты'''
        near = [
            (x + 1, y),
            (x - 1, y),
            (x, y + 1),
            (x, y - 1),
            (x + 1, y + 1),
            (x - 1, y - 1),
            (x + 1, y - 1),
            (x - 1, y + 1),
        ]

        for near_x, near_y in near:
            if 0 <= near_x < self.width and 0 <= near_y < self.height:
                if grid[near_y][near_x] == '.':
                    return True

        return False

    def get_neighbors(self, x, y):
        '''Возвращает соседние клетки внутри рабочих границ карты'''
        near = [
            (x + 1, y),
            (x - 1, y),
            (x, y + 1),
            (x, y - 1),
        ]

        valid_near = []

        for near_x, near_y in near:
            if 1 <= near_x < self.width - 1 and 1 <= near_y < self.height - 1:
                valid_near.append((near_x, near_y))

        return valid_near

    def get_corridor_cost(self, grid, x, y):
        '''Возвращает стоимость прохождения тайла при создании коридора'''
        tile = grid[y][x]

        if tile == 'W':
            if self.is_near_room(grid, x, y):
                return 30

            return 12

        if tile == 'C':
            return 1

        if tile == '.':
            return 25

        return 100

    def get_cell_distance(self, x1, y1, x2, y2):
        '''Возвращает евклидово расстояние между двумя клетками'''
        return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

    def get_far_cell(self, grid, x, y, min_distance=4):
        '''Ищет свободную клетку не ближе заданной дистанции'''
        while True:
            x1, y1 = self.get_empty_cell(grid)

            if self.get_cell_distance(x, y, x1, y1) >= min_distance:
                return x1, y1

    def get_far_cell_wall(self, grid, x, y, min_distance=4):
        '''Ищет стену не ближе заданной дистанции от исходной клетки'''
        while True:
            x1, y1 = self.get_wall_cell(grid)

            if self.get_cell_distance(x, y, x1, y1) >= min_distance:
                return x1, y1
