"""Боевая система игры."""

from __future__ import annotations

import random

from domain.models import Enemy, EnemyType, GameSession, Item, ItemType, Level, Pos


def enemy_at(level: Level, pos: Pos) -> Enemy | None:
    """Возвращает врага в клетке (если есть и он видим)."""
    for enemy in level.enemies.values():
        if enemy.pos != pos:
            continue
        if enemy.enemy_type == EnemyType.GHOST and not enemy.ghost_visible:
            continue
        return enemy
    return None


def attack_hits(rng: random.Random, attacker_agility: int, target_agility: int) -> bool:
    """Проверка попадания."""
    chance = 0.55 + (attacker_agility - target_agility) * 0.03
    chance = max(0.10, min(0.90, chance))
    return rng.random() < chance


def compute_damage(rng: random.Random, strength: int, weapon_bonus: int) -> int:
    """Расчёт урона."""
    variance = rng.randint(0, max(1, strength // 2 + 1))
    weapon_roll = rng.randint(0, max(0, weapon_bonus))
    return max(1, strength + variance + weapon_roll)


def treasure_drop(rng: random.Random, enemy: Enemy) -> int:
    """Количество золота за убийство."""
    base = enemy.hostility + enemy.agility // 2 + enemy.strength + enemy.max_hp // 5
    return max(1, rng.randint(base // 3, base // 2 + 1))


def player_attack(rng: random.Random, session: GameSession, enemy: Enemy) -> str:
    """Атака игрока."""

    hero = session.hero

    if enemy.enemy_type == EnemyType.VAMPIRE and enemy.vampire_first_hit_block:
        enemy.vampire_first_hit_block = False
        return "First strike misses the vampire's mist form."

    if not attack_hits(rng, hero.agility, enemy.agility):
        return f"You miss {enemy.enemy_type.value}."

    weapon_bonus = hero.weapon.value if hero.weapon else 0
    damage = compute_damage(rng, hero.strength, weapon_bonus)

    enemy.hp -= damage
    session.stats.hits_dealt += 1

    if enemy.hp > 0:
        return f"You hit {enemy.enemy_type.value} for {damage}."

    # смерть врага
    gained = treasure_drop(rng, enemy)

    session.level.enemies.pop(enemy.enemy_id, None)
    session.stats.kills += 1

    session.backpack.add_item(
        Item(item_type=ItemType.TREASURE, name="treasure", value=gained)
    )
    session.stats.treasure = session.backpack.treasure

    return (
        f"You hit {enemy.enemy_type.value} for {damage} and kill it. "
        f"+{gained} treasure."
    )


def enemy_attack(rng: random.Random, session: GameSession, enemy: Enemy) -> None:
    """Атака врага."""

    hero = session.hero

    guaranteed = (
        enemy.enemy_type == EnemyType.OGRE
        and enemy.ogre_guaranteed_hit
    )

    if not guaranteed and not attack_hits(rng, enemy.agility, hero.agility):
        return

    damage = compute_damage(rng, enemy.strength, 0)

    hero.hp -= damage
    session.stats.hits_taken += 1

    # ✔ важно: учитываем для автобаланса
    session.level_damage_taken += damage

    if enemy.enemy_type == EnemyType.GHOST:
        enemy.ghost_engaged = True

    if enemy.enemy_type == EnemyType.VAMPIRE:
        _apply_vampire_drain(rng, session)

    elif enemy.enemy_type == EnemyType.SNAKE_MAGE:
        _apply_snake_sleep(rng, session)

    elif enemy.enemy_type == EnemyType.OGRE:
        _apply_ogre_rest(enemy)

    if hero.hp <= 0:
        session.game_over = True
        session.victory = False
        session.message = "You died."


def _apply_vampire_drain(rng: random.Random, session: GameSession) -> None:
    drain = rng.randint(1, 2)
    session.hero.max_hp = max(1, session.hero.max_hp - drain)
    session.hero.hp = min(session.hero.hp, session.hero.max_hp)


def _apply_snake_sleep(rng: random.Random, session: GameSession) -> None:
    if rng.random() < 0.30:
        session.sleep_turns = max(session.sleep_turns, 1)


def _apply_ogre_rest(enemy: Enemy) -> None:
    enemy.ogre_rest_turns = 1
    enemy.ogre_guaranteed_hit = False


def manhattan_distance(a: Pos, b: Pos) -> int:
    return abs(a.x - b.x) + abs(a.y - b.y)


def is_adjacent(a: Pos, b: Pos, *, allow_diagonal: bool) -> bool:
    dx = abs(a.x - b.x)
    dy = abs(a.y - b.y)

    if allow_diagonal:
        return max(dx, dy) == 1

    return dx + dy == 1