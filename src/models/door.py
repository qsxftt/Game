"""Модель двери."""


class Door:
    """Дверь с простым FSM: closed -> opening -> open -> closing."""

    def __init__(self, x, y, orient, block_size):
        """Создает дверь в клетке карты."""
        self.x = x
        self.y = y
        self.orient = orient
        self.block_size = block_size
        self.state = 'closed'
        self.open_progress = 0.0
        self.open_speed = 0.03
        self.delay = 240
        self.cooldown = 0

    def open(self):
        """Начинает открытие двери, если она сейчас закрыта."""
        if self.state != 'closed':
            return False

        self.state = 'opening'
        return True

    def update(self):
        """Обновляет анимацию и состояние двери на один кадр."""
        if self.state == 'opening':
            self.open_progress += self.open_speed

            if self.open_progress >= 1.0:
                self.open_progress = 1.0
                self.state = 'open'
                self.cooldown = self.delay

        elif self.state == 'open':
            if self.cooldown > 0:
                self.cooldown -= 1
            else:
                self.state = 'closing'

        elif self.state == 'closing':
            self.open_progress -= self.open_speed

            if self.open_progress <= 0:
                self.open_progress = 0.0
                self.state = 'closed'

    def get_panel_segment(self):
        """Возвращает отрезок дверной панели для проверки пересечения лучом."""
        offset = self.block_size * self.open_progress

        if self.orient == 'hor':
            y = self.y + self.block_size // 2
            x1 = self.x + offset
            x2 = self.x + self.block_size

            return 'hor', x1, y, x2, y

        x = self.x + self.block_size // 2
        y1 = self.y + offset
        y2 = self.y + self.block_size

        return 'vert', x, y1, x, y2
