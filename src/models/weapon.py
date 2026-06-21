'''Модели оружия'''


class Weapon:
    '''Базовое оружие: урон, патроны, cooldown и перезарядка'''

    def __init__(self):
        '''Создает пустое оружие, которое настраивается наследником'''
        self.name = ''
        self.damage = 0
        self.ammo = 0
        self.magazine_size = 0
        self.reserve_ammo = 0
        self.attack_distance = 0

        self.shoot_delay = 0
        self.shoot_cooldown = 0

        self.reload_delay = 0
        self.reload_cooldown = 0

    def update(self):
        '''Обновляет cooldown выстрела и завершает перезарядку'''
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        if self.reload_cooldown > 0:
            self.reload_cooldown -= 1
            if self.reload_cooldown == 0:
                need_ammo = self.magazine_size - self.ammo
                ammo_to = min(self.reserve_ammo, need_ammo)

                self.ammo += ammo_to
                self.reserve_ammo -= ammo_to

    def can_shoot(self):
        '''Проверяет возможность выстрела

        Returns:
            True, если есть патроны и закончились задержки
        '''
        if self.ammo > 0 and self.shoot_cooldown == 0 and self.reload_cooldown == 0:
            return True
        else:
            return False

    def shoot(self):
        '''Пытается выполнить выстрел

        Returns:
            True при успешном выстреле, иначе False
        '''
        if not self.can_shoot():
            return False

        self.ammo -= 1
        self.shoot_cooldown = self.shoot_delay

        return True

    def reload(self):
        '''Запускает перезарядку оружия

        Returns:
            True при запуске перезарядки, иначе False
        '''
        if self.ammo == self.magazine_size:
            return False

        if self.reload_cooldown > 0:
            return False

        if self.reserve_ammo <= 0:
            return False

        self.reload_cooldown = self.reload_delay

        return True


class Pistol(Weapon):
    '''Стартовый пистолет игрока'''

    def __init__(self):
        '''Настраивает урон, магазин, задержки и текстуры пистолета'''
        super().__init__()
        self.name = 'Pistol'
        self.damage = 20
        self.ammo = 10
        self.magazine_size = 10
        self.shoot_delay = 20
        self.reload_delay = 60
        self.reserve_ammo = 30
        self.attack_distance = 1200


class Shotgun(Weapon):
    '''Дробовик игрока'''

    def __init__(self):
        '''Настраивает характеристики дробовика'''
        super().__init__()
        self.name = 'Shotgun'
        self.damage = 50
        self.ammo = 2
        self.magazine_size = 2
        self.shoot_delay = 50
        self.reload_delay = 60
        self.reserve_ammo = 8
        self.attack_distance = 300
