'''Модель уровня, собранная из текстовой карты'''

from src.models.door import Door


class Level:
    '''Хранит стены, двери, старт игрока, врагов, терминал и ресурсы уровня'''

    def __init__(self, block_size, text_map):
        '''Создает уровень и разбирает текстовую карту

        Args:
            block_size: размер одной клетки в мировых координатах
            text_map: текстовая карта с обозначениями объектов
        '''
        self.block_size = block_size
        self.text_map = text_map
        self.block_map = set()
        self.door_positions = []
        self.doors = {}
        self.player_start = None
        self.enemies_pos = []
        self.terminal_pos = None
        self.pickups_pos = []

        self.build()

    def build(self):
        '''Переводит символы текстовой карты в игровые координаты и объекты'''
        y_block = 0

        for row in self.text_map:
            x_block = 0

            for tile in row:
                if tile == 'W':
                    self.block_map.add((x_block, y_block))
                elif tile == 'D':
                    self.door_positions.append((x_block, y_block))
                elif tile == 'P':
                    self.player_start = (
                        x_block + self.block_size // 2,
                        y_block + self.block_size // 2,
                    )
                elif tile == 'E':
                    self.enemies_pos.append(
                        (x_block + self.block_size // 2, y_block + self.block_size // 2)
                    )
                elif tile == 'T':
                    self.terminal_pos = (x_block, y_block)
                elif tile == 'H':
                    self.pickups_pos.append(
                        (
                            x_block + self.block_size // 2,
                            y_block + self.block_size // 2,
                            'medkit',
                        )
                    )
                elif tile == 'A':
                    self.pickups_pos.append(
                        (
                            x_block + self.block_size // 2,
                            y_block + self.block_size // 2,
                            'ammo',
                        )
                    )

                x_block += self.block_size

            y_block += self.block_size

        for x, y in self.door_positions:
            orient = self.get_orient_door(x, y)
            self.doors[(x, y)] = Door(x, y, orient, self.block_size)

    def get_orient_door(self, x, y):
        '''Определяет ориентацию двери по соседним стенам

        Args:
            x: мировая координата двери по горизонтали
            y: мировая координата двери по вертикали

        Returns:
            Строка hor или vert
        '''
        left = (x - self.block_size, y) in self.block_map
        right = (x + self.block_size, y) in self.block_map
        up = (x, y - self.block_size) in self.block_map
        down = (x, y + self.block_size) in self.block_map

        if left and right:
            return 'hor'

        if up and down:
            return 'vert'

        return 'vert'
