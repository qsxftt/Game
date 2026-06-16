from random import randint as rnd

from src.systems.level_validation import validate_level


class Room:
    """Прямоугольная комната в сетке уровня."""

    def __init__(self, x, y, width, height):
        """Сохраняет позицию левого верхнего угла и размер комнаты в клетках."""
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def get_center(self):
        """Возвращает координаты центральной клетки комнаты."""
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2

        return center_x, center_y

    def intersects(self, other, margin=0):
        """Проверяет пересечение с другой комнатой с дополнительным отступом."""
        return (
            self.x - margin < other.x + other.width
            and self.x + self.width + margin > other.x
            and self.y - margin < other.y + other.height
            and self.y + self.height + margin > other.y
        )


class LevelGenerator:
    """Создает текстовую карту сектора: комнаты, коридоры, игрока и объекты."""

    def __init__(self, width=12, height=8, enemy_count=1, medkit_count=1, ammo_count=1, room_count=3):
        """Сохраняет параметры генерации текущего сектора."""
        self.width = width
        self.height = height
        self.enemy_count = enemy_count
        self.medkit_count = medkit_count
        self.ammo_count = ammo_count
        self.room_count = room_count

    # Основной процесс генерации

    def generate(self):
        """Пробует собрать валидную карту и возвращает ее в текстовом виде."""
        for _ in range(100):
            text_map = self.build_map()

            if validate_level(text_map):
                return text_map

        raise RuntimeError('Ошибка генерации карты')

    def build_map(self):
        """Создает одну карту без повторных попыток валидации."""
        grid = self.create_filled_grid()

        rooms = self.create_rooms(grid, self.room_count)
        self.connect_rooms(grid, rooms)

        player_x, player_y = self.get_empty_cell(grid)
        self.set_tile(grid, player_x, player_y, 'P')
        self.place_terminal(grid)
        self.place_far_tiles(grid, player_x, player_y, 'E', self.enemy_count)
        self.place_random_tiles(grid, 'H', self.medkit_count)
        self.place_random_tiles(grid, 'A', self.ammo_count)

        return [''.join(row) for row in grid]

    # Создание базовой сетки

    def create_filled_grid(self):
        """Создает сетку, полностью заполненную стенами."""
        grid = []

        for y in range(self.height):
            row = []

            for x in range(self.width):
                row.append('W')

            grid.append(row)

        return grid

    def create_empty_grid(self):
        """Создает старую тестовую сетку: стены по краям, пол внутри."""
        grid = []

        for y in range(self.height):
            row = []

            for x in range(self.width):
                if x == 0 or y == 0 or x == self.width - 1 or y == self.height - 1:
                    row.append('W')
                else:
                    row.append('.')

            grid.append(row)

        return grid

    # Создание комнат

    def create_random_room(self):
        """Создает случайную комнату, которая помещается внутри границ карты."""
        room_width = rnd(4, 6)
        room_height = rnd(4, 6)

        x = rnd(1, self.width - room_width - 1)
        y = rnd(1, self.height - room_height - 1)

        return Room(x, y, room_width, room_height)

    def room_intersects_any(self, new_room, rooms):
        """Проверяет, пересекается ли новая комната с уже созданными комнатами."""
        for room in rooms:
            if new_room.intersects(room, margin=1):
                return True

        return False

    def create_room(self, grid, room):
        """Вырезает комнату в сетке, заменяя стены на пол."""
        for y in range(room.y, room.y + room.height):
            for x in range(room.x, room.x + room.width):
                self.set_tile(grid, x, y, '.')

    def create_rooms(self, grid, room_count, max_attempts=100):
        """Пытается создать нужное количество непересекающихся комнат."""
        rooms = []

        for _ in range(max_attempts):
            if len(rooms) >= room_count:
                break

            room = self.create_random_room()

            if not self.room_intersects_any(room, rooms):
                rooms.append(room)
                self.create_room(grid, room)

        return rooms

    # Соединение комнат

    def connect_rooms(self, grid, rooms):
        """Соединяет комнаты коридорами через ближайшие уже подключенные комнаты."""
        if len(rooms) < 2:
            return

        connected_rooms = [rooms[0]]

        for room in rooms[1:]:
            nearest_room = self.get_nearest_room(room, connected_rooms)
            self.create_corridor(grid, room, nearest_room)
            connected_rooms.append(room)

    def create_corridor(self, grid, start, end):
        """Создает Г-образный коридор между центрами двух комнат."""
        start_x, start_y = start.get_center()
        end_x, end_y = end.get_center()

        for x in range(min(start_x, end_x), max(start_x, end_x) + 1):
            self.set_tile(grid, x, start_y, '.')

        for y in range(min(start_y, end_y), max(start_y, end_y) + 1):
            self.set_tile(grid, end_x, y, '.')

    def get_room_distance(self, room1, room2):
        """Возвращает расстояние между центрами двух комнат."""
        x1, y1 = room1.get_center()
        x2, y2 = room2.get_center()

        return self.get_cell_distance(x1, y1, x2, y2)

    def get_nearest_room(self, room, rooms):
        """Ищет ближайшую комнату из переданного списка."""
        nearest_room = rooms[0]
        nearest_distance = self.get_room_distance(room, nearest_room)

        for other_room in rooms[1:]:
            distance = self.get_room_distance(room, other_room)

            if distance < nearest_distance:
                nearest_room = other_room
                nearest_distance = distance

        return nearest_room

    # Работа с клетками

    def set_tile(self, grid, x, y, tile):
        """Записывает символ тайла в указанную клетку сетки."""
        grid[y][x] = tile

    def is_empty(self, grid, x, y):
        """Проверяет, является ли клетка свободным полом."""
        return grid[y][x] == '.'

    def get_empty_cell(self, grid):
        """Возвращает случайную свободную клетку."""
        while True:
            x = rnd(1, self.width - 2)
            y = rnd(1, self.height - 2)
            if self.is_empty(grid, x, y):
                return x, y

    def get_wall_cell(self, grid):
        """Возвращает случайную клетку стены."""
        while True:
            x = rnd(0, self.width - 1)
            y = rnd(0, self.height - 1)
            if grid[y][x] == 'W':
                return x, y

    # Размещение объектов

    def place_random_tiles(self, grid, tile, count):
        """Ставит несколько тайлов в случайные свободные клетки."""
        for _ in range(count):
            self.set_tile(grid, *self.get_empty_cell(grid), tile)

    def place_far_tiles(self, grid, x, y, tile, count):
        """Ставит несколько тайлов на расстоянии от указанной клетки."""
        for _ in range(count):
            self.set_tile(grid, *self.get_far_cell(grid, x, y), tile)

    def place_terminal(self, grid):
        """Ставит терминал в стену, рядом с которой есть свободная клетка."""
        while True:
            wall_x, wall_y = self.get_wall_cell(grid)
            if self.can_place_terminal(grid, wall_x, wall_y):
                self.set_tile(grid, wall_x, wall_y, 'T')
                return

    def can_place_terminal(self, grid, wall_x, wall_y):
        """Проверяет, можно ли поставить терминал в выбранную стену."""
        near = [
            (wall_x + 1, wall_y),
            (wall_x - 1, wall_y),
            (wall_x, wall_y + 1),
            (wall_x, wall_y - 1),
        ]

        for x, y in near:
            if 0 <= x < self.width and 0 <= y < self.height:
                if self.is_empty(grid, x, y):
                    return True

        return False

    # Расстояния

    def get_cell_distance(self, x1, y1, x2, y2):
        """Возвращает евклидово расстояние между двумя клетками."""
        return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5

    def get_far_cell(self, grid, x, y, min_distance=4):
        """Ищет случайную свободную клетку не ближе заданной дистанции."""
        while True:
            x1, y1 = self.get_empty_cell(grid)

            if self.get_cell_distance(x, y, x1, y1) >= min_distance:
                return x1, y1
