"""Фабрика противников."""

from __future__ import annotations

import random
from dataclasses import dataclass

from domain.models import Enemy, EnemyType, Pos


@dataclass(frozen=True, slots=True)
class _EnemyTemplate:
    symbol: str
    color: int
    hp_base: int
    hp_scale: int
    agility_base: int
    strength_base: int
    strength_scale: int
    hostility: int


_TEMPLATES: dict[EnemyType, _EnemyTemplate] = {
    EnemyType.ZOMBIE: _EnemyTemplate(
        symbol="z",
        color=2,
        hp_base=10,
        hp_scale=3,
        agility_base=5,
        strength_base=6,
        strength_scale=1,
        hostility=7,
    ),
    EnemyType.VAMPIRE: _EnemyTemplate(
        symbol="v",
        color=1,
        hp_base=14,
        hp_scale=3,
        agility_base=10,
        strength_base=8,
        strength_scale=1,
        hostility=10,
    ),
    EnemyType.GHOST: _EnemyTemplate(
        symbol="g",
        color=5,
        hp_base=8,
        hp_scale=2,
        agility_base=8,
        strength_base=3,
        strength_scale=1,
        hostility=5,
    ),
    EnemyType.OGRE: _EnemyTemplate(
        symbol="O",
        color=3,
        hp_base=22,
        hp_scale=4,
        agility_base=4,
        strength_base=12,
        strength_scale=2,
        hostility=8,
    ),
    EnemyType.SNAKE_MAGE: _EnemyTemplate(
        symbol="s",
        color=5,
        hp_base=12,
        hp_scale=2,
        agility_base=13,
        strength_base=7,
        strength_scale=1,
        hostility=10,
    ),
    EnemyType.MIMIC: _EnemyTemplate(
        symbol="m",
        color=5,
        hp_base=16,
        hp_scale=3,
        agility_base=11,
        strength_base=4,
        strength_scale=1,
        hostility=3,
    ),
}


def create_enemy(
    enemy_id: int,
    enemy_type: EnemyType,
    level_index: int,
    rng: random.Random,
) -> Enemy:
    """Создаёт врага с характеристиками, масштабированными по глубине."""

    template = _TEMPLATES[enemy_type]
    lvl_bonus = max(-2, level_index // 3)

    hp = template.hp_base + lvl_bonus * template.hp_scale
    agility = template.agility_base + lvl_bonus
    strength = template.strength_base + lvl_bonus * template.strength_scale

    hp = max(1, hp + rng.randint(-1, 1))
    agility = max(1, agility + rng.randint(-1, 1))
    strength = max(1, strength + rng.randint(-1, 1))

    extra: dict = {}

    if enemy_type == EnemyType.SNAKE_MAGE:
        extra["snake_diag_dir"] = (1, 1)

    if enemy_type == EnemyType.MIMIC:
        extra["disguised"] = True
        extra["mimic_item_symbol"] = rng.choice(["!", "?", "/", "$"])

    return Enemy(
        enemy_id=enemy_id,
        enemy_type=enemy_type,
        pos=Pos(1, 1),
        max_hp=hp,
        hp=hp,
        agility=agility,
        strength=strength,
        hostility=template.hostility,
        symbol=template.symbol,
        color=template.color,
        **extra,
    )


def enemy_pool_by_depth(level_index: int) -> list[EnemyType]:
    """Возвращает пул доступных врагов по глубине."""

    pool: list[EnemyType] = [EnemyType.ZOMBIE, EnemyType.GHOST]

    if level_index >= 2:
        pool.append(EnemyType.VAMPIRE)
    if level_index >= 3:
        pool.append(EnemyType.OGRE)
    if level_index >= 4:
        pool.append(EnemyType.SNAKE_MAGE)
    if level_index >= 5:
        pool.append(EnemyType.MIMIC)
    if level_index >= 8:
        pool.extend([EnemyType.OGRE, EnemyType.SNAKE_MAGE])

    return pool