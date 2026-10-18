"""Игровой движок: оркестратор игровой сессии."""

from __future__ import annotations

import random

from domain.ai import enemy_turn
from domain.combat import enemy_at, player_attack
from domain.fov import compute_visible_cells, update_discovery
from domain.generator import generate_level
from domain.models import (
    ActiveEffect,
    Backpack,
    Character,
    Enemy,
    EnemyType,
    GameSession,
    Item,
    ItemType,
    Level,
    Pos,
    RunStats,
    StatType,
    Tile,
)

DIAGONAL_DIRS: list[tuple[int, int]] = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
CARDINAL_DIRS: list[tuple[int, int]] = [(1, 0), (-1, 0), (0, 1), (0, -1)]

_HERO_MAX_HP = 35
_HERO_AGILITY = 9
_HERO_STRENGTH = 6


class GameEngine:
    """Оркестратор игровой сессии."""

    def __init__(self, seed: int | None = None) -> None:
        self.rng = random.Random(seed)

    def new_session(self) -> GameSession:
        """Создаёт новую игровую сессию."""

        level, start_pos = generate_level(1, self.rng)

        hero = Character(
            max_hp=_HERO_MAX_HP,
            hp=_HERO_MAX_HP,
            agility=_HERO_AGILITY,
            strength=_HERO_STRENGTH,
        )

        session = GameSession(
            hero=hero,
            hero_pos=start_pos,
            level=level,
            backpack=Backpack(),
            active_effects=[],
            stats=RunStats(),
            current_level=1,
            message="Find the exit of level 1.",
        )

        visible = compute_visible_cells(session)
        update_discovery(session, visible)
        session.last_visible = visible
        return session

    def from_saved(self, session: GameSession) -> GameSession:
        """Восстанавливает сессию из сохранения."""

        if session.rng_state is not None:
            self.rng.setstate(session.rng_state)

        visible = compute_visible_cells(session)
        update_discovery(session, visible)
        session.last_visible = visible
        return session

    def save_rng_state(self, session: GameSession) -> None:
        """Сохраняет RNG state в сессию перед записью на диск."""
        session.rng_state = self.rng.getstate()

    def move_player(self, session: GameSession, dx: int, dy: int) -> str:
        """Обрабатывает ход игрока."""

        if session.game_over:
            return session.message

        if session.sleep_turns > 0:
            session.sleep_turns -= 1
            self._end_turn(session)
            session.message = "You are asleep and miss this turn."
            return session.message

        target = session.hero_pos + (dx, dy)

        if not session.level.is_inside(target):
            session.message = "You bump into darkness."
            return session.message

        if not session.level.is_walkable(target):
            tile = session.level.tile_at(target)
            doors = {
                Tile.DOOR_RED.value: "red",
                Tile.DOOR_BLUE.value: "blue",
                Tile.DOOR_YELLOW.value: "yellow",
            }

            if tile in doors:
                color = doors[tile]
                if color in session.backpack.keys:
                    session.level.set_tile(target, Tile.FLOOR.value)
                    session.message = f"You unlocked the {color} door."
                    self._end_turn(session)
                    return session.message

                session.message = f"You need the {color} key to open this door."
                return session.message

            session.message = "A wall blocks your path."
            return session.message

        enemy = enemy_at(session.level, target)
        if enemy is not None:
            reveal_msg = ""
            if enemy.enemy_type == EnemyType.MIMIC and enemy.disguised:
                enemy.disguised = False
                reveal_msg = "The item suddenly transforms into a Mimic! "

            attack_msg = self._handle_attack(session, enemy)

            if reveal_msg:
                session.flash_message = reveal_msg + attack_msg

            return attack_msg

        session.hero_pos = target
        session.stats.steps += 1
        msg_parts: list[str] = []

        pickup_msg = self._handle_pickup(session, target)
        if pickup_msg:
            msg_parts.append(pickup_msg)

        if target == session.level.exit_pos:
            msg_parts.append(self._advance_level(session))
        else:
            self._end_turn(session)

        session.message = " ".join(msg_parts) if msg_parts else "You move."
        return session.message

    def use_item(self, session: GameSession, item_type: ItemType, index: int) -> str:
        """Применяет предмет из рюкзака."""

        if session.game_over:
            return session.message

        if item_type == ItemType.WEAPON and index == 0:
            return self._unequip_weapon(session)

        bucket = session.backpack.bucket(item_type)
        if index < 1 or index > len(bucket):
            session.message = "Invalid item index."
            return session.message

        item = bucket[index - 1]
        msg = ""

        if item_type == ItemType.FOOD:
            msg = self._use_food(session, bucket, index)
        elif item_type == ItemType.ELIXIR:
            msg = self._use_elixir(session, bucket, index, item)
        elif item_type == ItemType.SCROLL:
            msg = self._use_scroll(session, bucket, index, item)
        elif item_type == ItemType.WEAPON:
            msg = self._equip_weapon(session, bucket, index)

        if not session.game_over:
            self._end_turn(session)

        session.message = msg
        return msg

    def _unequip_weapon(self, session: GameSession) -> str:
        if session.hero.weapon is None:
            session.message = "You are already unarmed."
            return session.message

        session.backpack.weapon.append(session.hero.weapon)
        session.hero.weapon = None
        self._end_turn(session)
        session.message = "You put weapon away."
        return session.message

    def _use_food(self, session: GameSession, bucket: list[Item], index: int) -> str:
        item = bucket.pop(index - 1)
        old_hp = session.hero.hp
        session.hero.hp = min(session.hero.max_hp, session.hero.hp + item.value)
        healed = session.hero.hp - old_hp
        session.stats.food_used += 1
        return f"You eat {item.name} and heal {healed} HP."

    def _use_elixir(
        self,
        session: GameSession,
        bucket: list[Item],
        index: int,
        item: Item,
    ) -> str:
        bucket.pop(index - 1)

        self._apply_stat_delta(session, item.stat, item.value)
        session.active_effects.append(
            ActiveEffect(
                stat=item.stat or StatType.STRENGTH,
                value=item.value,
                turns_left=item.duration,
            )
        )

        session.stats.elixirs_used += 1
        return f"You drink {item.name}. +{item.value} {item.stat} for {item.duration} turns."

    def _use_scroll(
        self,
        session: GameSession,
        bucket: list[Item],
        index: int,
        item: Item,
    ) -> str:
        bucket.pop(index - 1)
        self._apply_stat_delta(session, item.stat, item.value)
        session.stats.scrolls_used += 1
        return f"You read {item.name}. Permanent +{item.value} {item.stat}."

    def _equip_weapon(self, session: GameSession, bucket: list[Item], index: int) -> str:
        chosen = bucket.pop(index - 1)
        old_weapon = session.hero.weapon
        session.hero.weapon = chosen
        msg = f"You equip {chosen.name} (+{chosen.value} power)."

        if old_weapon is not None:
            drop_pos = self._free_adjacent_pos(session.level, session.hero_pos)
            if drop_pos:
                session.level.items[(drop_pos.x, drop_pos.y)] = old_weapon
                msg += " Old weapon dropped nearby."
            else:
                session.backpack.weapon.append(old_weapon)
                msg += " No free cell nearby, old weapon returned to backpack."

        return msg

    def _handle_attack(self, session: GameSession, enemy: Enemy) -> str:
        if enemy.enemy_type == EnemyType.GHOST:
            enemy.ghost_engaged = True

        msg = player_attack(self.rng, session, enemy)

        if not session.game_over:
            self._end_turn(session)

        return msg

    def _handle_pickup(self, session: GameSession, pos: Pos) -> str:
        found_item = session.level.items.pop((pos.x, pos.y), None)
        if found_item is None:
            return ""

        if session.backpack.add_item(found_item):
            if found_item.item_type == ItemType.TREASURE:
                session.stats.treasure = session.backpack.treasure
            if found_item.item_type == ItemType.KEY:
                return f"Picked up {found_item.name} key."
            return f"Picked up {found_item.name}."

        session.level.items[(pos.x, pos.y)] = found_item
        return f"Backpack slot for {found_item.item_type.value} is full."

    def _advance_level(self, session: GameSession) -> str:
        """Переходит на следующий уровень или завершает игру победой."""

        if session.current_level >= 21:
            session.victory = True
            session.game_over = True
            session.stats.reached_level = 21
            return "You escaped the final dungeon level. Victory!"

        session.current_level += 1
        session.stats.reached_level = session.current_level
        session.difficulty_bias = self._update_difficulty_bias(session)
        session.backpack.keys.clear()

        level, start_pos = generate_level(
            session.current_level,
            self.rng,
            difficulty_bias=session.difficulty_bias,
        )

        session.level = level
        session.hero_pos = start_pos
        session.level_damage_taken = 0

        visible = compute_visible_cells(session)
        update_discovery(session, visible)
        session.last_visible = visible

        return f"You descend to level {session.current_level}."

    def _end_turn(self, session: GameSession) -> None:
        if session.game_over:
            return

        revealed_mimic = self._reveal_mimics(session)

        enemy_turn(self.rng, session)

        if not session.game_over:
            self._tick_effects(session)

        visible = compute_visible_cells(session)
        update_discovery(session, visible)
        session.last_visible = visible

        if revealed_mimic:
            session.flash_message = "The item suddenly transforms into a Mimic!"

    def _reveal_mimics(self, session: GameSession) -> bool:
        hero = session.hero_pos
        revealed = False

        for enemy in session.level.enemies.values():
            if enemy.enemy_type == EnemyType.MIMIC and enemy.disguised:
                dx = abs(enemy.pos.x - hero.x)
                dy = abs(enemy.pos.y - hero.y)
                if dx <= 1 and dy <= 1:
                    enemy.disguised = False
                    revealed = True

        return revealed

    def _tick_effects(self, session: GameSession) -> None:
        expired: list[ActiveEffect] = []

        for effect in session.active_effects:
            effect.turns_left -= 1
            if effect.turns_left <= 0:
                expired.append(effect)

        for effect in expired:
            session.active_effects.remove(effect)
            self._apply_stat_delta(session, effect.stat, -effect.value)

        if session.hero.hp <= 0:
            session.hero.hp = 1

    def _apply_stat_delta(
        self,
        session: GameSession,
        stat: StatType | None,
        delta: int,
    ) -> None:
        if stat is None:
            return

        hero = session.hero

        if stat == StatType.AGILITY:
            hero.agility = max(1, hero.agility + delta)

        elif stat == StatType.STRENGTH:
            hero.strength = max(1, hero.strength + delta)

        elif stat == StatType.MAX_HP:
            hero.max_hp = max(1, hero.max_hp + delta)
            hero.hp += delta
            hero.hp = max(1, hero.hp)
            hero.hp = min(hero.hp, hero.max_hp)

        elif stat == StatType.HP:
            hero.hp = min(hero.max_hp, max(1, hero.hp + delta))

    def _update_difficulty_bias(self, session: GameSession) -> int:
        lost_ratio = session.level_damage_taken / max(1, session.hero.max_hp)

        current = session.difficulty_bias

        if lost_ratio < 0.20:
            delta = 1
        elif lost_ratio > 0.70:
            delta = -2
        elif lost_ratio > 0.50:
            delta = -1
        else:
            delta = 0

        return max(-3, min(5, current + delta))

    def _free_adjacent_pos(self, level: Level, pos: Pos) -> Pos | None:
        candidates = [pos + d for d in CARDINAL_DIRS + DIAGONAL_DIRS]
        self.rng.shuffle(candidates)

        for c in candidates:
            if not level.is_walkable(c):
                continue
            if (c.x, c.y) in level.items:
                continue
            if any(enemy.pos == c for enemy in level.enemies.values()):
                continue
            return c

        return None