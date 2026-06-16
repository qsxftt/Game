from random import randint as rnd


class LevelGenerator:
    def __init__(self, width=12, height=8, enemy_count=1, medkit_count=1, ammo_count=1):
        self.width = width
        self.height = height
        self.enemy_count = enemy_count
        self.medkit_count = medkit_count
        self.ammo_count = ammo_count

    def generate(self):
        grid = self.create_empty_grid()

        player_x, player_y = self.get_empty_cell(grid)
        self.set_tile(grid, player_x, player_y, 'P')
        self.place_terminal(grid)
        self.place_far_tiles(grid, player_x, player_y, 'E', self.enemy_count)
        self.place_random_tiles(grid, 'H', self.medkit_count)
        self.place_random_tiles(grid, 'A', self.ammo_count)

        return [''.join(row) for row in grid]
    
    def create_empty_grid(self):
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
    
    def set_tile(self, grid, x, y, tile):
        grid[y][x] = tile

    def is_empty(self, grid, x, y):
        return grid[y][x] == '.'

    def get_empty_cell(self, grid):
        while True:
            x = rnd(1, self.width - 2)
            y = rnd(1, self.height - 2)
            if self.is_empty(grid, x, y):
                return x, y
            
    def place_random_tiles(self, grid, tile, count):
        for _ in range(count):
            self.set_tile(grid, *self.get_empty_cell(grid), tile)

    def place_far_tiles(self, grid, x, y, tile, count):
        for _ in range(count):
            self.set_tile(grid, *self.get_far_cell(grid, x, y), tile)

    def get_cell_distance(self, x1, y1, x2, y2):
        return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
    
    def get_far_cell(self, grid, x, y, min_distance=4):
        while True:
            x1, y1 = self.get_empty_cell(grid)

            if self.get_cell_distance(x, y, x1, y1) >= min_distance:
                return x1, y1

    def place_terminal(self, grid):
        while True:
            wall_x, wall_y = self.get_wall_cell(grid)
            if self.can_place_terminal(grid, wall_x, wall_y):
                self.set_tile(grid, wall_x, wall_y, 'T')
                return

    def can_place_terminal(self, grid, wall_x, wall_y):
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


    def get_wall_cell(self, grid):
        while True:
            x = rnd(0, self.width - 1)
            y = rnd(0, self.height - 1)
            if grid[y][x] == 'W':
                return x, y