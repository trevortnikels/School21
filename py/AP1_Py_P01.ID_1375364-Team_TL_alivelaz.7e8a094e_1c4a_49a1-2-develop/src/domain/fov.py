"""FOV и туман войны."""

from __future__ import annotations

from domain.models import GameSession, Level, Pos, Tile


def bresenham_line(a: Pos, b: Pos) -> list[Pos]:
    """Возвращает список клеток на прямой между a и b включительно."""

    points: list[Pos] = []
    x0, y0 = a.x, a.y
    x1, y1 = b.x, b.y

    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy

    while True:
        points.append(Pos(x0, y0))
        if x0 == x1 and y0 == y1:
            return points
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def compute_visible_cells(
    session: GameSession,
    radius: int = 12,
) -> set[tuple[int, int]]:
    """Вычисляет видимые клетки методом ray casting."""

    origin = session.hero_pos
    level = session.level
    visible: set[tuple[int, int]] = {(origin.x, origin.y)}

    for edge_x in range(origin.x - radius, origin.x + radius + 1):
        for edge_y in (origin.y - radius, origin.y + radius):
            _cast_ray(level, origin, Pos(edge_x, edge_y), visible)

    for edge_y in range(origin.y - radius + 1, origin.y + radius):
        for edge_x in (origin.x - radius, origin.x + radius):
            _cast_ray(level, origin, Pos(edge_x, edge_y), visible)

    return visible


def _cast_ray(
    level: Level,
    src: Pos,
    dst: Pos,
    visible: set[tuple[int, int]],
) -> None:
    """Пускает один луч и заполняет множество видимости."""

    for point in bresenham_line(src, dst):
        if not level.is_inside(point):
            return

        visible.add((point.x, point.y))

        if point != src and level.tile_at(point) in {
            Tile.WALL.value,
            Tile.DOOR_RED.value,
            Tile.DOOR_BLUE.value,
            Tile.DOOR_YELLOW.value,
        }:
            return


def update_discovery(
    session: GameSession,
    visible: set[tuple[int, int]] | None = None,
) -> None:
    """Обновляет discovered для комнат и коридоров."""

    if visible is None:
        visible = compute_visible_cells(session)

    level = session.level

    current_room = level.room_for(session.hero_pos)
    if current_room is not None:
        current_room.discovered = True

    for room in level.rooms:
        if room.discovered:
            continue

        for y in range(room.y1, room.y2 + 1):
            for x in range(room.x1, room.x2 + 1):
                if (x, y) in visible:
                    room.discovered = True
                    break
            if room.discovered:
                break

    for x, y in visible:
        if level.room_for(Pos(x, y)) is None:
            level.discovered_corridors.add((x, y))