"""Общие расчеты видимости и экранной позиции объектов мира."""

from math import atan2, pi

from src.core.config import DELTA_RAY, HALF_FOV, SCALE, WIDTH_HALF


def get_depth(obj, player):
    """Возвращает расстояние от игрока до объекта."""
    dx = player.x - obj.x
    dy = player.y - obj.y

    return (dx ** 2 + dy ** 2) ** 0.5


def get_angle(obj, player):
    """Возвращает угол от игрока к объекту."""
    dx = obj.x - player.x
    dy = obj.y - player.y

    return atan2(dy, dx)


def get_delta_angle(obj, player):
    """Возвращает разницу между направлением взгляда игрока и объектом."""
    angle = get_angle(obj, player)
    delta_angle = angle - player.angle

    while delta_angle > pi:
        delta_angle -= 2 * pi

    while delta_angle < -pi:
        delta_angle += 2 * pi

    return delta_angle


def is_in_fov(obj, player):
    """Проверяет, попадает ли объект в поле зрения игрока."""
    delta_angle = get_delta_angle(obj, player)

    return abs(delta_angle) < HALF_FOV


def get_screen_x(obj, player):
    """Возвращает X-координату объекта на экране."""
    delta_angle = get_delta_angle(obj, player)

    return WIDTH_HALF + delta_angle / DELTA_RAY * SCALE


def is_visible(obj, player, level):
    """Проверяет, не перекрыт ли объект стеной, дверью или терминалом."""
    from src.views.raycast_renderer import cast_single_ray

    angle = get_angle(obj, player)
    _, _, wall_depth, _, _ = cast_single_ray(player, angle, level)
    obj_depth = get_depth(obj, player)

    return obj_depth < wall_depth
