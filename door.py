class Door:
    def __init__(self, x, y, orient, block_size):
        self.x = x
        self.y = y
        self.orient = orient
        self.block_size = block_size
        self.is_open = False
        self.is_opening = False
        self.open_progress = 0.0
        self.open_speed = 0.03
        self.delay = 240
        self.cooldown = 0

    def open(self):
        if self.is_open or self.is_opening:
            return False

        self.is_opening = True
        return True
    
    def update(self):
        if self.cooldown > 0:
            self.cooldown -= 1

        if self.is_opening and self.cooldown == 0:
            self.open_progress += self.open_speed

            if self.open_progress > 1.0:
                self.open_progress = 1.0
                self.is_open = True
                self.cooldown = self.delay
                self.open_speed = -self.open_speed
            
            if self.open_progress < 0.0:
                self.open_progress = 0.0
                self.is_opening = False
                self.is_open = False
                self.open_speed = -self.open_speed

    def get_panel_rect(self, thickness=8):
        offset = self.block_size * self.open_progress

        if self.orient == "hor":
            return (
                self.x + offset,
                self.y + self.block_size // 2 - thickness // 2,
                self.block_size - offset,
                thickness
            )

        return (
            self.x + self.block_size // 2 - thickness // 2,
            self.y + offset,
            thickness,
            self.block_size - offset
        )
    
    def get_panel_segment(self):
        offset = self.block_size * self.open_progress

        if self.orient == "hor":
            y = self.y + self.block_size // 2
            x1 = self.x + offset
            x2 = self.x + self.block_size

            return "hor", x1, y, x2, y

        x = self.x + self.block_size // 2
        y1 = self.y + offset
        y2 = self.y + self.block_size

        return "vert", x, y1, x, y2