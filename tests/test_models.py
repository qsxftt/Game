'''Тесты основных игровых моделей'''

from types import SimpleNamespace

from src.models.door import Door
from src.models.pickup import Ammo, MedKit
from src.models.weapon import Pistol


def test_door_opens_and_closes():
    '''Дверь проходит полный цикл открытия и закрытия'''
    door = Door(0, 0, 'vert', 100)

    assert door.open() is True

    for _ in range(34):
        door.update()

    assert door.state == 'open'
    assert door.open_progress == 1.0

    door.cooldown = 0
    door.update()

    for _ in range(34):
        door.update()

    assert door.state == 'closed'
    assert door.open_progress == 0.0


def test_blocked_door_stays_open():
    '''Занятая дверь не начинает закрываться'''
    door = Door(0, 0, 'vert', 100)
    door.state = 'open'
    door.open_progress = 1.0
    door.cooldown = 0

    door.update(blocked=True)

    assert door.state == 'open'
    assert door.cooldown == door.delay


def test_pistol_shoots_and_reloads():
    '''Пистолет расходует патрон и правильно перезаряжается'''
    pistol = Pistol()

    assert pistol.shoot() is True
    assert pistol.ammo == 9
    assert pistol.shoot() is False

    for _ in range(pistol.shoot_delay):
        pistol.update()

    assert pistol.reload() is True

    for _ in range(pistol.reload_delay):
        pistol.update()

    assert pistol.ammo == pistol.magazine_size
    assert pistol.reserve_ammo == 29


def test_medkit_is_not_used_at_full_health():
    '''Аптечка остается на карте при полном здоровье'''
    player = SimpleNamespace(x=100, y=100, health=100, max_health=100)
    medkit = MedKit(100, 100)

    assert medkit.update(player) is False
    assert medkit.is_pickedup is False

    player.health = 90

    assert medkit.update(player) is True
    assert player.health == 100


def test_ammo_increases_weapon_reserve():
    '''Патроны пополняют запас текущего оружия один раз'''
    weapon = SimpleNamespace(reserve_ammo=5)
    player = SimpleNamespace(x=100, y=100, weapon=weapon)
    ammo = Ammo(100, 100)

    assert ammo.update(player) is True
    assert weapon.reserve_ammo == 15
    assert ammo.update(player) is False
    assert weapon.reserve_ammo == 15
