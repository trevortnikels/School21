"""Процедурная генерация уровней."""

from __future__ import annotations

import random
from collections import deque

from domain.enemy_factory import create_enemy, enemy_pool_by_depth
from domain.fov import bresenham_line
from domain.models import Corridor, Item, ItemType, Level, Pos, Room, StatType, Tile

CARDINAL_DIRS: list[tuple[int, int]] = [(1, 0), (-1, 0), (0, 1), (0, -1)]

_ITEM_WEIGHT_FOOD = 0.30
_ITEM_WEIGHT_ELIXIR = 0.30
_ITEM_WEIGHT_SCROLL = 0.25


def generate_level(
    index: int,
    rng: random.Random,
    width: int = 78,
    height: int = 19,
    difficulty_bias: int = 0,
) -> tuple[Level, Pos]:
    """Генерирует один уровень."""
    tiles, rooms = _generate_rooms(rng, width, height)
    corridors = _carve_corridors(rng, rooms, tiles, width, height)
    start_room, exit_room = _select_start_and_exit(rng, rooms)

    start_pos = rng.choice(start_room.random_floor_cells())
    exit_pos = rng.choice(exit_room.random_floor_cells())
    tiles[exit_pos.y][exit_pos.x] = Tile.EXIT.value

    level = Level(
        index=index,
        width=width,
        height=height,
        tiles=tiles,
        rooms=rooms,
        corridors=corridors,
        start_room_id=start_room.room_id,
        exit_pos=exit_pos,
    )

    _assert_connected(level, start_pos)
    _add_doors_and_keys(level, start_pos, rng)
    _populate_level(level, rng, start_room.room_id, difficulty_bias)

    return level, start_pos


def _generate_rooms(
    rng: random.Random,
    width: int,
    height: int,
) -> tuple[list[list[str]], list[Room]]:
    """Генерирует 9 комнат, по одной в каждой секции 3x3."""
    tiles = [[Tile.WALL.value for _ in range(width)] for _ in range(height)]
    rooms: list[Room] = []

    section_w = width // 3
    section_h = height // 3
    room_id = 0

    for row in range(3):
        for col in range(3):
            sec_x1 = col * section_w
            sec_y1 = row * section_h
            sec_x2 = (col + 1) * section_w - 1
            sec_y2 = (row + 1) * section_h - 1

            room = _make_room(
                rng,
                room_id,
                sec_x1,
                sec_y1,
                sec_x2,
                sec_y2,
                tiles,
            )
            rooms.append(room)
            room_id += 1

    return tiles, rooms


def _make_room(
    rng: random.Random,
    room_id: int,
    sec_x1: int,
    sec_y1: int,
    sec_x2: int,
    sec_y2: int,
    tiles: list[list[str]],
) -> Room:
    max_room_w = max(5, sec_x2 - sec_x1 - 2)
    max_room_h = max(3, sec_y2 - sec_y1 - 2)

    room_w = rng.randint(5, max_room_w)
    room_h = rng.randint(3, max_room_h)

    x1 = rng.randint(sec_x1 + 1, sec_x2 - room_w - 1)
    y1 = rng.randint(sec_y1 + 1, sec_y2 - room_h - 1)
    x2 = x1 + room_w
    y2 = y1 + room_h

    for y in range(y1, y2 + 1):
        for x in range(x1, x2 + 1):
            if x in (x1, x2) or y in (y1, y2):
                tiles[y][x] = Tile.WALL.value
            else:
                tiles[y][x] = Tile.FLOOR.value

    return Room(room_id=room_id, x1=x1, y1=y1, x2=x2, y2=y2)


def _carve_corridors(
    rng: random.Random,
    rooms: list[Room],
    tiles: list[list[str]],
    width: int,
    height: int,
) -> list[Corridor]:
    """Соединяет комнаты коридорами так, чтобы граф был связным."""
    corridors: list[Corridor] = []
    corridor_id = 0

    def carve(from_room: Room, to_room: Room) -> None:
        nonlocal corridor_id

        a = from_room.center()
        b = to_room.center()
        mid = Pos(b.x, a.y) if rng.random() < 0.5 else Pos(a.x, b.y)

        path = bresenham_line(a, mid) + bresenham_line(mid, b)[1:]

        for point in path:
            if 0 <= point.y < height and 0 <= point.x < width:
                tiles[point.y][point.x] = Tile.FLOOR.value

        corridors.append(Corridor(corridor_id=corridor_id, cells=path))
        corridor_id += 1

    for r in range(3):
        for c in range(2):
            carve(rooms[r * 3 + c], rooms[r * 3 + c + 1])

    for c in range(3):
        for r in range(2):
            carve(rooms[r * 3 + c], rooms[(r + 1) * 3 + c])

    return corridors


def _select_start_and_exit(
    rng: random.Random,
    rooms: list[Room],
) -> tuple[Room, Room]:
    start_room = rng.choice(rooms)
    exit_room = rng.choice([room for room in rooms if room.room_id != start_room.room_id])
    return start_room, exit_room


def _populate_level(
    level: Level,
    rng: random.Random,
    start_room_id: int,
    difficulty_bias: int,
) -> None:
    """Заполняет уровень предметами и врагами."""
    enemy_level = level.index + difficulty_bias
    enemy_count = min(max(2, 2 + enemy_level + difficulty_bias), 20)
    item_count = max(12 - level.index // 2 - difficulty_bias, 3)
    food_bias = max(0.0, -difficulty_bias * 0.05)

    floor_cells: list[Pos] = []
    for room in level.rooms:
        if room.room_id != start_room_id:
            floor_cells.extend(room.random_floor_cells())

    rng.shuffle(floor_cells)

    item_cells = floor_cells[:]
    enemy_cells = floor_cells[:]

    _place_items(level, rng, item_cells, item_count, food_bias)
    _place_enemies(level, rng, enemy_cells, enemy_level, enemy_count)


def _place_items(
    level: Level,
    rng: random.Random,
    floor_cells: list[Pos],
    item_count: int,
    food_bias: float = 0.0,
) -> None:
    for _ in range(item_count):
        item = _roll_item(rng, level.index, food_bias)
        _place_entity(level, floor_cells, item)


def _roll_item(
    rng: random.Random,
    level_index: int,
    food_bias: float = 0.0,
) -> Item:
    roll = rng.random()
    cumulative = 0.0

    cumulative += _ITEM_WEIGHT_FOOD + food_bias
    if roll < cumulative:
        return Item(
            item_type=ItemType.FOOD,
            name="ration",
            value=rng.randint(4, 10),
            stat=StatType.HP,
        )

    cumulative += _ITEM_WEIGHT_ELIXIR
    if roll < cumulative:
        stat = rng.choice([StatType.AGILITY, StatType.STRENGTH, StatType.MAX_HP])
        return Item(
            item_type=ItemType.ELIXIR,
            name=f"elixir of {stat.value}",
            value=rng.randint(1, 3),
            stat=stat,
            duration=15,
        )

    cumulative += _ITEM_WEIGHT_SCROLL
    if roll < cumulative:
        stat = rng.choice([StatType.AGILITY, StatType.STRENGTH, StatType.MAX_HP])
        return Item(
            item_type=ItemType.SCROLL,
            name=f"scroll of {stat.value}",
            value=rng.randint(1, 3),
            stat=stat,
        )

    return Item(
        item_type=ItemType.WEAPON,
        name=rng.choice(["dagger", "mace", "axe", "spear"]),
        value=rng.randint(2, 8) + level_index // 3,
        stat=StatType.STRENGTH,
        subtype="weapon",
    )


def _place_enemies(
    level: Level,
    rng: random.Random,
    floor_cells: list[Pos],
    enemy_level: int,
    enemy_count: int,
) -> None:
    if not floor_cells:
        return

    pool = enemy_pool_by_depth(enemy_level)

    for enemy_id in range(enemy_count):
        enemy_type = rng.choice(pool)
        enemy = create_enemy(enemy_id, enemy_type, enemy_level, rng)

        pos = _pick_free_cell(level, floor_cells, rng)
        if pos is None:
            continue

        enemy.pos = pos
        level.enemies[enemy.enemy_id] = enemy


def _place_entity(
    level: Level,
    floor_cells: list[Pos],
    item: Item,
) -> bool:
    while floor_cells:
        pos = floor_cells.pop()

        if (pos.x, pos.y) == (level.exit_pos.x, level.exit_pos.y):
            continue
        if (pos.x, pos.y) in level.items:
            continue
        if any(enemy.pos == pos for enemy in level.enemies.values()):
            continue

        level.items[(pos.x, pos.y)] = item
        return True

    return False


def _pick_free_cell(
    level: Level,
    floor_cells: list[Pos],
    rng: random.Random,
    max_attempts: int = 300,
) -> Pos | None:
    for _ in range(max_attempts):
        pos = rng.choice(floor_cells)

        if (pos.x, pos.y) == (level.exit_pos.x, level.exit_pos.y):
            continue
        if (pos.x, pos.y) in level.items:
            continue
        if any(enemy.pos == pos for enemy in level.enemies.values()):
            continue

        return pos

    return None


def _assert_connected(level: Level, start: Pos) -> None:
    """Проверяет связность уровня через BFS."""
    visited: set[tuple[int, int]] = set()
    queue: deque[Pos] = deque([start])

    while queue:
        current = queue.popleft()
        key = (current.x, current.y)

        if key in visited:
            continue

        visited.add(key)

        for dx, dy in CARDINAL_DIRS:
            nxt = current + (dx, dy)
            if level.is_walkable(nxt) and (nxt.x, nxt.y) not in visited:
                queue.append(nxt)

    for room in level.rooms:
        center = room.center()
        if (center.x, center.y) not in visited:
            raise RuntimeError(
                f"Generated level is not connected: room {room.room_id} unreachable"
            )

    if (level.exit_pos.x, level.exit_pos.y) not in visited:
        raise RuntimeError("Generated level is not connected: exit unreachable")


def _assert_connected_with_keys(level: Level, start: Pos) -> bool:
    """Проверяет, что уровень проходим с учетом дверей и ключей."""
    visited: set[tuple[int, int]] = {(start.x, start.y)}
    queue: deque[Pos] = deque([start])

    keys_held: set[str] = set()
    blocked_doors: list[tuple[str, Pos]] = []

    door_map = {
        Tile.DOOR_RED.value: "red",
        Tile.DOOR_BLUE.value: "blue",
        Tile.DOOR_YELLOW.value: "yellow",
    }

    while queue:
        current = queue.popleft()

        item = level.items.get((current.x, current.y))
        if item and item.item_type == ItemType.KEY and item.name not in keys_held:
            keys_held.add(item.name)

            reopened: list[tuple[str, Pos]] = []
            for color, door_pos in blocked_doors:
                if color in keys_held and (door_pos.x, door_pos.y) not in visited:
                    visited.add((door_pos.x, door_pos.y))
                    queue.append(door_pos)
                else:
                    reopened.append((color, door_pos))
            blocked_doors = reopened

        for dx, dy in CARDINAL_DIRS:
            nxt = current + (dx, dy)
            key = (nxt.x, nxt.y)

            if not level.is_inside(nxt):
                continue
            if key in visited:
                continue

            tile = level.tile_at(nxt)

            if tile in door_map:
                color = door_map[tile]
                if color in keys_held:
                    visited.add(key)
                    queue.append(nxt)
                else:
                    blocked_doors.append((color, nxt))
            elif tile in {Tile.FLOOR.value, Tile.EXIT.value}:
                visited.add(key)
                queue.append(nxt)

    for room in level.rooms:
        center = room.center()
        if (center.x, center.y) not in visited:
            return False

    return (level.exit_pos.x, level.exit_pos.y) in visited


def _add_doors_and_keys(level: Level, start: Pos, rng: random.Random) -> None:
    """Добавляет двери и ключи без софтлока."""
    if not _assert_connected_with_keys(level, start):
        raise RuntimeError("Base level is not connected")

    num_doors = min(level.index // 2 + 1, 3)
    if num_doors <= 0 or not level.corridors:
        return

    floor_cells: list[Pos] = []
    for room in level.rooms:
        if room.room_id != level.start_room_id:
            floor_cells.extend(room.random_floor_cells())

    for _ in range(100):
        if _try_place_doors_and_keys(level, start, rng, num_doors, floor_cells):
            return


def _try_place_doors_and_keys(
    level: Level,
    start: Pos,
    rng: random.Random,
    num_doors: int,
    floor_cells: list[Pos],
) -> bool:
    door_tiles = [Tile.DOOR_RED, Tile.DOOR_BLUE, Tile.DOOR_YELLOW]
    colors = ["red", "blue", "yellow"]

    k = min(rng.randint(1, num_doors), len(level.corridors))

    chosen_color_indices = rng.sample(range(3), k)
    chosen_corridors = rng.sample(level.corridors, k)

    placed_doors: list[tuple[Pos, str]] = []
    placed_items: list[tuple[int, int]] = []
    door_to_color: dict[Pos, str] = {}

    valid = _place_doors_for_attempt(
        level,
        k,
        chosen_color_indices,
        chosen_corridors,
        colors,
        door_tiles,
        door_to_color,
        placed_doors,
    )

    if valid:
        valid = _place_keys_for_attempt(
            level,
            start,
            rng,
            k,
            floor_cells,
            door_to_color,
            placed_items,
        )

    if valid and _assert_connected_with_keys(level, start):
        return True

    _revert_doors_and_keys(level, placed_doors, placed_items)
    return False


def _place_doors_for_attempt(
    level: Level,
    k: int,
    chosen_color_indices: list[int],
    chosen_corridors: list[Corridor],
    colors: list[str],
    door_tiles: list[Tile],
    door_to_color: dict[Pos, str],
    placed_doors: list[tuple[Pos, str]],
) -> bool:
    for i in range(k):
        color_idx = chosen_color_indices[i]
        color = colors[color_idx]
        door_tile = door_tiles[color_idx].value
        corridor = chosen_corridors[i]

        corridor_only = [
            p for p in corridor.cells
            if not any(room.contains(p) for room in level.rooms)
        ]

        if not corridor_only:
            return False

        door_pos = corridor_only[len(corridor_only) // 2]

        if level.tile_at(door_pos) != Tile.FLOOR.value:
            return False
        if (door_pos.x, door_pos.y) == (level.exit_pos.x, level.exit_pos.y):
            return False

        level.set_tile(door_pos, door_tile)
        door_to_color[door_pos] = color
        placed_doors.append((door_pos, Tile.FLOOR.value))

    return True


def _place_keys_for_attempt(
    level: Level,
    start: Pos,
    rng: random.Random,
    k: int,
    floor_cells: list[Pos],
    door_to_color: dict[Pos, str],
    placed_items: list[tuple[int, int]],
) -> bool:
    visited: set[tuple[int, int]] = {(start.x, start.y)}
    queue: deque[Pos] = deque([start])

    unlocked_doors: set[Pos] = set()
    bumped_doors: dict[Pos, str] = {}
    placed_keys_count = 0

    valid_key_cells = set((cell.x, cell.y) for cell in floor_cells)
    accessible_key_cells: list[Pos] = []

    while placed_keys_count < k:
        while queue:
            curr = queue.popleft()
            curr_key = (curr.x, curr.y)

            if curr_key in valid_key_cells:
                if curr_key not in level.items and curr_key != (level.exit_pos.x, level.exit_pos.y):
                    accessible_key_cells.append(curr)
                valid_key_cells.remove(curr_key)

            for dx, dy in CARDINAL_DIRS:
                nxt = curr + (dx, dy)
                nxt_key = (nxt.x, nxt.y)

                if not level.is_inside(nxt):
                    continue
                if nxt_key in visited:
                    continue

                tile = level.tile_at(nxt)

                if nxt in door_to_color:
                    if nxt in unlocked_doors:
                        visited.add(nxt_key)
                        queue.append(nxt)
                    else:
                        bumped_doors[nxt] = door_to_color[nxt]
                elif tile in {Tile.FLOOR.value, Tile.EXIT.value}:
                    visited.add(nxt_key)
                    queue.append(nxt)

        if not bumped_doors or not accessible_key_cells:
            return False

        chosen_door_pos = rng.choice(list(bumped_doors.keys()))
        chosen_door_color = bumped_doors.pop(chosen_door_pos)

        key_pos = rng.choice(accessible_key_cells)
        accessible_key_cells.remove(key_pos)

        level.items[(key_pos.x, key_pos.y)] = Item(
            item_type=ItemType.KEY,
            name=chosen_door_color,
            value=0,
        )
        placed_items.append((key_pos.x, key_pos.y))

        unlocked_doors.add(chosen_door_pos)
        visited.add((chosen_door_pos.x, chosen_door_pos.y))
        queue.append(chosen_door_pos)
        placed_keys_count += 1

    return True


def _revert_doors_and_keys(
    level: Level,
    placed_doors: list[tuple[Pos, str]],
    placed_items: list[tuple[int, int]],
) -> None:
    for pos, old_tile in placed_doors:
        level.set_tile(pos, old_tile)

    for key_pos in placed_items:
        level.items.pop(key_pos, None)