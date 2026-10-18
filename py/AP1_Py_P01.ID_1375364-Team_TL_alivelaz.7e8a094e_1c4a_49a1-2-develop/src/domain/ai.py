"""ИИ и движение противников."""

from __future__ import annotations

import random
from collections import deque

from domain.combat import enemy_attack, is_adjacent, manhattan_distance
from domain.models import Enemy, EnemyType, GameSession, Level, Pos

CARDINAL_DIRS: list[tuple[int, int]] = [(1, 0), (-1, 0), (0, 1), (0, -1)]


def enemy_turn(rng: random.Random, session: GameSession) -> None:
    """Ход всех врагов."""
    if session.game_over:
        return

    for enemy in list(session.level.enemies.values()):
        if not enemy.alive():
            continue

        # мимик не двигается пока не раскрыт
        if enemy.enemy_type == EnemyType.MIMIC and enemy.disguised:
            continue

        _process_enemy(rng, session, enemy)

        if session.game_over:
            return


def _process_enemy(rng: random.Random, session: GameSession, enemy: Enemy) -> None:
    hero_pos = session.hero_pos
    level = session.level

    _update_special_state(rng, enemy, hero_pos)

    # отдых огра
    if enemy.enemy_type == EnemyType.OGRE and enemy.ogre_rest_turns > 0:
        enemy.ogre_rest_turns -= 1
        if enemy.ogre_rest_turns == 0:
            enemy.ogre_guaranteed_hit = True
        return

    # атака
    if is_adjacent(enemy.pos, hero_pos, allow_diagonal=True):
        enemy_attack(rng, session, enemy)
        return

    # преследование
    if manhattan_distance(enemy.pos, hero_pos) <= enemy.hostility:
        path = shortest_path(level, enemy.pos, hero_pos)

        if path and len(path) > 1:
            next_step = path[1]

            if next_step == hero_pos:
                enemy_attack(rng, session, enemy)
            elif can_move_to(level, enemy, next_step):
                enemy.pos = next_step

            return

    # патруль
    _patrol(rng, level, enemy)


def _update_special_state(rng: random.Random, enemy: Enemy, hero_pos: Pos) -> None:
    if enemy.enemy_type == EnemyType.GHOST:
        _update_ghost_visibility(rng, enemy, hero_pos)


def _update_ghost_visibility(rng: random.Random, enemy: Enemy, hero_pos: Pos) -> None:
    if enemy.ghost_engaged:
        enemy.ghost_visible = True
        return

    in_range = manhattan_distance(enemy.pos, hero_pos) <= enemy.hostility
    adjacent = is_adjacent(enemy.pos, hero_pos, allow_diagonal=True)

    if in_range or adjacent:
        enemy.ghost_visible = True
    else:
        enemy.ghost_visible = rng.random() > 0.35


def _patrol(rng: random.Random, level: Level, enemy: Enemy) -> None:
    match enemy.enemy_type:
        case EnemyType.GHOST:
            _patrol_ghost(rng, level, enemy)

        case EnemyType.OGRE:
            _patrol_ogre(rng, level, enemy)

        case EnemyType.SNAKE_MAGE:
            _patrol_snake(level, enemy)

        case _:
            _patrol_random(rng, level, enemy)


def _patrol_ghost(rng: random.Random, level: Level, enemy: Enemy) -> None:
    room = level.room_for(enemy.pos)
    if room is None:
        return

    cells = room.random_floor_cells()
    if cells:
        enemy.pos = rng.choice(cells)


def _patrol_ogre(rng: random.Random, level: Level, enemy: Enemy) -> None:
    dirs = CARDINAL_DIRS[:]
    rng.shuffle(dirs)

    for dx, dy in dirs:
        p1 = enemy.pos + (dx, dy)
        p2 = enemy.pos + (2 * dx, 2 * dy)

        if can_move_to(level, enemy, p1) and can_move_to(level, enemy, p2):
            enemy.pos = p2
            return


def _patrol_snake(level: Level, enemy: Enemy) -> None:
    dx, dy = enemy.snake_diag_dir
    target = enemy.pos + (dx, dy)

    if can_move_to(level, enemy, target):
        enemy.pos = target
        return

    enemy.snake_diag_dir = (-dx, -dy)

    target = enemy.pos + enemy.snake_diag_dir
    if can_move_to(level, enemy, target):
        enemy.pos = target


def _patrol_random(rng: random.Random, level: Level, enemy: Enemy) -> None:
    dirs = CARDINAL_DIRS[:]
    rng.shuffle(dirs)

    for dx, dy in dirs:
        target = enemy.pos + (dx, dy)
        if can_move_to(level, enemy, target):
            enemy.pos = target
            return


def can_move_to(level: Level, enemy: Enemy, pos: Pos) -> bool:
    if not level.is_walkable(pos):
        return False

    return not any(
        other.enemy_id != enemy.enemy_id and other.pos == pos
        for other in level.enemies.values()
    )


def shortest_path(level: Level, start: Pos, goal: Pos) -> list[Pos] | None:
    queue: deque[Pos] = deque([start])
    came_from: dict[tuple[int, int], tuple[int, int] | None] = {
        (start.x, start.y): None
    }

    while queue:
        current = queue.popleft()

        if current == goal:
            break

        for dx, dy in CARDINAL_DIRS:
            nxt = current + (dx, dy)
            key = (nxt.x, nxt.y)

            if key in came_from:
                continue

            if not level.is_walkable(nxt) and nxt != goal:
                continue

            came_from[key] = (current.x, current.y)
            queue.append(nxt)

    if (goal.x, goal.y) not in came_from:
        return None

    path: list[Pos] = []
    cur: tuple[int, int] | None = (goal.x, goal.y)

    while cur is not None:
        path.append(Pos(cur[0], cur[1]))
        cur = came_from[cur]

    path.reverse()
    return path