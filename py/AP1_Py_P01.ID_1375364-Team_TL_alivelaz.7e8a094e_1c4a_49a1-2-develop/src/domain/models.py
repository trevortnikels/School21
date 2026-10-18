"""Доменные модели игры Rogue.

Все основные сущности домена находятся здесь:
- карта и тайлы,
- игрок,
- враги,
- предметы,
- комнаты и коридоры,
- игровая сессия,
- статистика,
- сериализация / десериализация для JSON.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


def _rng_state_to_json(
    state: tuple[int, tuple[int, ...], float | None] | None,
) -> list | None:
    """Преобразует state random.Random в JSON-совместимый вид."""
    if state is None:
        return None
    version, internal_state, gauss_next = state
    return [version, list(internal_state), gauss_next]


def _rng_state_from_json(
    raw: list | None,
) -> tuple[int, tuple[int, ...], float | None] | None:
    """Восстанавливает state random.Random из JSON-представления."""
    if raw is None:
        return None
    version = int(raw[0])
    internal_state = tuple(int(x) for x in raw[1])
    gauss_next = float(raw[2]) if raw[2] is not None else None
    return (version, internal_state, gauss_next)


class Tile(str, Enum):
    WALL = "#"
    FLOOR = "."
    EXIT = ">"
    DOOR_RED = "R"
    DOOR_BLUE = "B"
    DOOR_YELLOW = "Y"


class ItemType(str, Enum):
    TREASURE = "treasure"
    FOOD = "food"
    ELIXIR = "elixir"
    SCROLL = "scroll"
    WEAPON = "weapon"
    KEY = "key"


class StatType(str, Enum):
    HP = "hp"
    MAX_HP = "max_hp"
    AGILITY = "agility"
    STRENGTH = "strength"


class EnemyType(str, Enum):
    ZOMBIE = "zombie"
    VAMPIRE = "vampire"
    GHOST = "ghost"
    OGRE = "ogre"
    SNAKE_MAGE = "snake_mage"
    MIMIC = "mimic"


@dataclass(slots=True, frozen=True)
class Pos:
    x: int
    y: int

    def __add__(self, other: tuple[int, int]) -> "Pos":
        return Pos(self.x + other[0], self.y + other[1])


@dataclass(slots=True)
class Item:
    item_type: ItemType
    name: str
    value: int
    stat: StatType | None = None
    duration: int = 0
    subtype: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "item_type": self.item_type.value,
            "name": self.name,
            "value": self.value,
            "stat": self.stat.value if self.stat else None,
            "duration": self.duration,
            "subtype": self.subtype,
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "Item":
        return Item(
            item_type=ItemType(data["item_type"]),
            name=str(data["name"]),
            value=int(data["value"]),
            stat=StatType(data["stat"]) if data.get("stat") else None,
            duration=int(data.get("duration", 0)),
            subtype=str(data.get("subtype", "")),
        )


@dataclass(slots=True)
class ActiveEffect:
    stat: StatType
    value: int
    turns_left: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "stat": self.stat.value,
            "value": self.value,
            "turns_left": self.turns_left,
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "ActiveEffect":
        return ActiveEffect(
            stat=StatType(data["stat"]),
            value=int(data["value"]),
            turns_left=int(data["turns_left"]),
        )


@dataclass(slots=True)
class Backpack:
    food: list[Item] = field(default_factory=list)
    elixir: list[Item] = field(default_factory=list)
    scroll: list[Item] = field(default_factory=list)
    weapon: list[Item] = field(default_factory=list)
    treasure: int = 0
    keys: list[str] = field(default_factory=list)

    _max_slot_size: int = field(default=9, init=False, repr=False)

    def add_item(self, item: Item) -> bool:
        if item.item_type == ItemType.TREASURE:
            self.treasure += item.value
            return True

        if item.item_type == ItemType.KEY:
            self.keys.append(item.name)
            return True

        bucket = self.bucket(item.item_type)
        if len(bucket) >= self._max_slot_size:
            return False

        bucket.append(item)
        return True

    def bucket(self, item_type: ItemType) -> list[Item]:
        match item_type:
            case ItemType.FOOD:
                return self.food
            case ItemType.ELIXIR:
                return self.elixir
            case ItemType.SCROLL:
                return self.scroll
            case ItemType.WEAPON:
                return self.weapon
            case _:
                raise ValueError(f"No inventory slot for item type {item_type!r}")

    def to_dict(self) -> dict[str, Any]:
        return {
            "food": [item.to_dict() for item in self.food],
            "elixir": [item.to_dict() for item in self.elixir],
            "scroll": [item.to_dict() for item in self.scroll],
            "weapon": [item.to_dict() for item in self.weapon],
            "treasure": self.treasure,
            "keys": list(self.keys),
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "Backpack":
        return Backpack(
            food=[Item.from_dict(x) for x in data.get("food", [])],
            elixir=[Item.from_dict(x) for x in data.get("elixir", [])],
            scroll=[Item.from_dict(x) for x in data.get("scroll", [])],
            weapon=[Item.from_dict(x) for x in data.get("weapon", [])],
            treasure=int(data.get("treasure", 0)),
            keys=list(data.get("keys", [])),
        )


@dataclass(slots=True)
class Character:
    max_hp: int
    hp: int
    agility: int
    strength: int
    weapon: Item | None = None

    def alive(self) -> bool:
        return self.hp > 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "max_hp": self.max_hp,
            "hp": self.hp,
            "agility": self.agility,
            "strength": self.strength,
            "weapon": self.weapon.to_dict() if self.weapon else None,
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "Character":
        weapon_data = data.get("weapon")
        return Character(
            max_hp=int(data["max_hp"]),
            hp=int(data["hp"]),
            agility=int(data["agility"]),
            strength=int(data["strength"]),
            weapon=Item.from_dict(weapon_data) if weapon_data else None,
        )


@dataclass(slots=True)
class Enemy:
    enemy_id: int
    enemy_type: EnemyType
    pos: Pos
    max_hp: int
    hp: int
    agility: int
    strength: int
    hostility: int
    symbol: str
    color: int

    ghost_visible: bool = True
    ghost_engaged: bool = False

    ogre_rest_turns: int = 0
    ogre_guaranteed_hit: bool = False

    snake_diag_dir: tuple[int, int] = (1, 1)
    vampire_first_hit_block: bool = True

    disguised: bool = False
    mimic_item_symbol: str | None = None

    def alive(self) -> bool:
        return self.hp > 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "enemy_id": self.enemy_id,
            "enemy_type": self.enemy_type.value,
            "pos": [self.pos.x, self.pos.y],
            "max_hp": self.max_hp,
            "hp": self.hp,
            "agility": self.agility,
            "strength": self.strength,
            "hostility": self.hostility,
            "symbol": self.symbol,
            "color": self.color,
            "ghost_visible": self.ghost_visible,
            "ghost_engaged": self.ghost_engaged,
            "ogre_rest_turns": self.ogre_rest_turns,
            "ogre_guaranteed_hit": self.ogre_guaranteed_hit,
            "snake_diag_dir": [self.snake_diag_dir[0], self.snake_diag_dir[1]],
            "vampire_first_hit_block": self.vampire_first_hit_block,
            "disguised": self.disguised,
            "mimic_item_symbol": self.mimic_item_symbol,
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "Enemy":
        diag = data.get("snake_diag_dir", [1, 1])
        return Enemy(
            enemy_id=int(data["enemy_id"]),
            enemy_type=EnemyType(data["enemy_type"]),
            pos=Pos(int(data["pos"][0]), int(data["pos"][1])),
            max_hp=int(data["max_hp"]),
            hp=int(data["hp"]),
            agility=int(data["agility"]),
            strength=int(data["strength"]),
            hostility=int(data["hostility"]),
            symbol=str(data["symbol"]),
            color=int(data["color"]),
            ghost_visible=bool(data.get("ghost_visible", True)),
            ghost_engaged=bool(data.get("ghost_engaged", False)),
            ogre_rest_turns=int(data.get("ogre_rest_turns", 0)),
            ogre_guaranteed_hit=bool(data.get("ogre_guaranteed_hit", False)),
            snake_diag_dir=(int(diag[0]), int(diag[1])),
            vampire_first_hit_block=bool(data.get("vampire_first_hit_block", True)),
            disguised=bool(data.get("disguised", False)),
            mimic_item_symbol=data.get("mimic_item_symbol"),
        )


@dataclass(slots=True)
class Room:
    room_id: int
    x1: int
    y1: int
    x2: int
    y2: int
    discovered: bool = False

    def contains(self, pos: Pos) -> bool:
        return self.x1 <= pos.x <= self.x2 and self.y1 <= pos.y <= self.y2

    def center(self) -> Pos:
        return Pos((self.x1 + self.x2) // 2, (self.y1 + self.y2) // 2)

    def random_floor_cells(self) -> list[Pos]:
        return [
            Pos(x, y)
            for y in range(self.y1 + 1, self.y2)
            for x in range(self.x1 + 1, self.x2)
        ]

    def to_dict(self) -> dict[str, Any]:
        return {
            "room_id": self.room_id,
            "x1": self.x1,
            "y1": self.y1,
            "x2": self.x2,
            "y2": self.y2,
            "discovered": self.discovered,
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "Room":
        return Room(
            room_id=int(data["room_id"]),
            x1=int(data["x1"]),
            y1=int(data["y1"]),
            x2=int(data["x2"]),
            y2=int(data["y2"]),
            discovered=bool(data.get("discovered", False)),
        )


@dataclass(slots=True)
class Corridor:
    corridor_id: int
    cells: list[Pos]

    def to_dict(self) -> dict[str, Any]:
        return {
            "corridor_id": self.corridor_id,
            "cells": [[p.x, p.y] for p in self.cells],
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "Corridor":
        return Corridor(
            corridor_id=int(data["corridor_id"]),
            cells=[Pos(int(p[0]), int(p[1])) for p in data.get("cells", [])],
        )


@dataclass(slots=True)
class Level:
    index: int
    width: int
    height: int
    tiles: list[list[str]]
    rooms: list[Room]
    corridors: list[Corridor]
    start_room_id: int
    exit_pos: Pos
    items: dict[tuple[int, int], Item] = field(default_factory=dict)
    enemies: dict[int, Enemy] = field(default_factory=dict)
    discovered_corridors: set[tuple[int, int]] = field(default_factory=set)

    _room_cache: dict[tuple[int, int], Room | None] = field(
        default_factory=dict,
        init=False,
        repr=False,
    )

    def tile_at(self, pos: Pos) -> str:
        return self.tiles[pos.y][pos.x]

    def set_tile(self, pos: Pos, tile: str) -> None:
        self.tiles[pos.y][pos.x] = tile

    def is_inside(self, pos: Pos) -> bool:
        return 0 <= pos.x < self.width and 0 <= pos.y < self.height

    def is_walkable(self, pos: Pos) -> bool:
        if not self.is_inside(pos):
            return False
        return self.tile_at(pos) in {Tile.FLOOR.value, Tile.EXIT.value}

    def room_for(self, pos: Pos) -> Room | None:
        key = (pos.x, pos.y)
        if key not in self._room_cache:
            self._room_cache[key] = next(
                (room for room in self.rooms if room.contains(pos)),
                None,
            )
        return self._room_cache[key]

    def to_dict(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "width": self.width,
            "height": self.height,
            "tiles": self.tiles,
            "rooms": [room.to_dict() for room in self.rooms],
            "corridors": [corridor.to_dict() for corridor in self.corridors],
            "start_room_id": self.start_room_id,
            "exit_pos": [self.exit_pos.x, self.exit_pos.y],
            "items": {
                f"{x},{y}": item.to_dict()
                for (x, y), item in self.items.items()
            },
            "enemies": {
                str(enemy_id): enemy.to_dict()
                for enemy_id, enemy in self.enemies.items()
            },
            "discovered_corridors": [list(p) for p in self.discovered_corridors],
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "Level":
        items: dict[tuple[int, int], Item] = {
            (int(sx), int(sy)): Item.from_dict(raw)
            for key, raw in data.get("items", {}).items()
            for sx, sy in [key.split(",")]
        }

        enemies = {
            int(enemy_id): Enemy.from_dict(raw)
            for enemy_id, raw in data.get("enemies", {}).items()
        }

        corridors = [
            Corridor.from_dict(raw)
            for raw in data.get("corridors", [])
        ]

        discovered_corridors = {
            (int(pt[0]), int(pt[1]))
            for pt in data.get("discovered_corridors", [])
        }

        return Level(
            index=int(data["index"]),
            width=int(data["width"]),
            height=int(data["height"]),
            tiles=[[str(cell) for cell in row] for row in data["tiles"]],
            rooms=[Room.from_dict(raw) for raw in data.get("rooms", [])],
            corridors=corridors,
            start_room_id=int(data["start_room_id"]),
            exit_pos=Pos(int(data["exit_pos"][0]), int(data["exit_pos"][1])),
            items=items,
            enemies=enemies,
            discovered_corridors=discovered_corridors,
        )


@dataclass(slots=True)
class RunStats:
    treasure: int = 0
    reached_level: int = 1
    kills: int = 0
    food_used: int = 0
    elixirs_used: int = 0
    scrolls_used: int = 0
    hits_dealt: int = 0
    hits_taken: int = 0
    steps: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "treasure": self.treasure,
            "reached_level": self.reached_level,
            "kills": self.kills,
            "food_used": self.food_used,
            "elixirs_used": self.elixirs_used,
            "scrolls_used": self.scrolls_used,
            "hits_dealt": self.hits_dealt,
            "hits_taken": self.hits_taken,
            "steps": self.steps,
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "RunStats":
        return RunStats(
            treasure=int(data.get("treasure", 0)),
            reached_level=int(data.get("reached_level", 1)),
            kills=int(data.get("kills", 0)),
            food_used=int(data.get("food_used", 0)),
            elixirs_used=int(data.get("elixirs_used", 0)),
            scrolls_used=int(data.get("scrolls_used", 0)),
            hits_dealt=int(data.get("hits_dealt", 0)),
            hits_taken=int(data.get("hits_taken", 0)),
            steps=int(data.get("steps", 0)),
        )


@dataclass(slots=True)
class GameSession:
    hero: Character
    hero_pos: Pos
    level: Level
    backpack: Backpack
    active_effects: list[ActiveEffect]
    stats: RunStats
    current_level: int

    sleep_turns: int = 0
    game_over: bool = False
    victory: bool = False
    message: str = ""

    rng_state: Any = None
    last_visible: set[tuple[int, int]] = field(default_factory=set, repr=False)

    difficulty_bias: int = 0
    level_damage_taken: int = 0
    flash_message: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "hero": self.hero.to_dict(),
            "hero_pos": [self.hero_pos.x, self.hero_pos.y],
            "level": self.level.to_dict(),
            "backpack": self.backpack.to_dict(),
            "active_effects": [effect.to_dict() for effect in self.active_effects],
            "stats": self.stats.to_dict(),
            "current_level": self.current_level,
            "sleep_turns": self.sleep_turns,
            "game_over": self.game_over,
            "victory": self.victory,
            "message": self.message,
            "rng_state": _rng_state_to_json(self.rng_state),
            "difficulty_bias": self.difficulty_bias,
            "level_damage_taken": self.level_damage_taken,
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "GameSession":
        raw_rng = data.get("rng_state")
        rng_state = _rng_state_from_json(raw_rng) if raw_rng is not None else None

        return GameSession(
            hero=Character.from_dict(data["hero"]),
            hero_pos=Pos(int(data["hero_pos"][0]), int(data["hero_pos"][1])),
            level=Level.from_dict(data["level"]),
            backpack=Backpack.from_dict(data["backpack"]),
            active_effects=[
                ActiveEffect.from_dict(raw)
                for raw in data.get("active_effects", [])
            ],
            stats=RunStats.from_dict(data.get("stats", {})),
            current_level=int(data.get("current_level", 1)),
            sleep_turns=int(data.get("sleep_turns", 0)),
            game_over=bool(data.get("game_over", False)),
            victory=bool(data.get("victory", False)),
            message=str(data.get("message", "")),
            rng_state=rng_state,
            difficulty_bias=int(data.get("difficulty_bias", 0)),
            level_damage_taken=int(data.get("level_damage_taken", 0)),
        )