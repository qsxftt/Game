'''Общие расчеты видимости и экранной позиции объектов мира'''

from math import atan2, pi

from src.core.config import DELTA_RAY, HALF_FOV, SCALE, WIDTH_HALF


def get_depth(obj, player):
    '''Возвращает расстояние от игрока до объекта

    Args:
        obj: объект игрового мира
        player: модель игрока

    Returns:
        Евклидово расстояние между объектами
    '''
    dx = player.x - obj.x
    dy = player.y - obj.y

    return (dx**2 + dy**2) ** 0.5

def get_angle(obj, player):
    '''Возвращает угол от игрока к объекту

    Args:
        obj: объект игрового мира
        player: модель игрока

    Returns:
        Угол направления в радианах
    '''
    dx = obj.x - player.x
    dy = obj.y - player.y

    return atan2(dy, dx)

def get_delta_angle(obj, player):
    '''Находит разницу между взглядом игрока и направлением на объект

    Args:
        obj: объект игрового мира
        player: модель игрока

    Returns:
        Нормализованная разница углов в радианах
    '''
    angle = get_angle(obj, player)
    delta_angle = angle - player.angle

    while delta_angle > pi:
        delta_angle -= 2 * pi

    while delta_angle < -pi:
        delta_angle += 2 * pi

    return delta_angle

def is_in_fov(obj, player):
    '''Проверяет попадание объекта в поле зрения игрока

    Args:
        obj: проверяемый объект
        player: модель игрока

    Returns:
        True, если объект находится внутри FOV
    '''
    delta_angle = get_delta_angle(obj, player)

    return abs(delta_angle) < HALF_FOV

def get_screen_x(obj, player):
    '''Вычисляет горизонтальную позицию объекта на экране

    Args:
        obj: объект игрового мира
        player: модель игрока

    Returns:
        Экранная координата по горизонтали
    '''
    delta_angle = get_delta_angle(obj, player)

    return WIDTH_HALF + delta_angle / DELTA_RAY * SCALE

def is_visible(obj, player, level):
    '''Проверяет, не перекрыт ли объект препятствием

    Args:
        obj: проверяемый объект
        player: модель игрока
        level: текущий уровень

    Returns:
        True, если объект расположен ближе ближайшего препятствия
    '''
    from src.views.raycast_renderer import cast_single_ray

    angle = get_angle(obj, player)
    _, _, wall_depth, _, _ = cast_single_ray(player, angle, level)
    obj_depth = get_depth(obj, player)

    return obj_depth < wall_depth

# ============================================================
# LINE OF SIGHT - ПОШАГОВАЯ ПРОВЕРКА ЛУЧА
# ============================================================

def has_line_of_sight(x1, y1, x2, y2, level, step=10):
    '''Проверяет свободный от препятствий отрезок между точками

    Args:
        x1: начальная мировая координата по горизонтали
        y1: начальная мировая координата по вертикали
        x2: конечная мировая координата по горизонтали
        y2: конечная мировая координата по вертикали
        level: текущий уровень
        step: расстояние между проверяемыми точками луча

    Returns:
        True, если между точками нет препятствий
    '''
    from src.systems.map_system import get_block_type

    dx = x2 - x1
    dy = y2 - y1
    distance = (dx**2 + dy**2) ** 0.5

    if distance == 0:
        return True

    steps = int(distance / step)

    for i in range(1, steps + 1):
        check_x = x1 + dx / steps * i
        check_y = y1 + dy / steps * i

        if get_block_type(check_x, check_y, level):
            return False

    return True
