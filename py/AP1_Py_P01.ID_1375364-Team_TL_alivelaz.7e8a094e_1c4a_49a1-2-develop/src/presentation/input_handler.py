"""Обработчик выбора предметов из инвентаря."""

from __future__ import annotations

import curses

from domain.models import GameSession, ItemType
from presentation.renderer import Renderer

_TITLE_OFFSET = 5
_MIN_HEIGHT = 14
_MAX_VISIBLE_ITEMS = 9



def prompt_inventory_choice(
    stdscr: curses.window,
    renderer: Renderer,
    session: GameSession,
    item_type: ItemType,
    allow_zero: bool = False,
) -> int | None:
    """Показывает диалог выбора предмета."""

    items = session.backpack.bucket(item_type)
    has_equipped_weapon = (
        item_type == ItemType.WEAPON and session.hero.weapon is not None
    )

    if not items and not (allow_zero and has_equipped_weapon):
        session.message = f"No {item_type.value} in backpack."
        return None

    _draw_inventory_dialog(
        stdscr=stdscr,
        renderer=renderer,
        session=session,
        item_type=item_type,
        items=items,
        allow_zero=allow_zero,
    )

    return _read_inventory_key(stdscr, items, allow_zero)


def _draw_inventory_dialog(
    stdscr: curses.window,
    renderer: Renderer,
    session: GameSession,
    item_type: ItemType,
    items: list,
    allow_zero: bool,
) -> None:
    """Рисует окно выбора предмета под картой."""

    level = session.level
    y0 = min(level.height + _TITLE_OFFSET, curses.LINES - _MIN_HEIGHT)

    stdscr.move(y0, 0)
    stdscr.clrtobot()

    digits = "0-9" if allow_zero else "1-9"
    title = f"Choose {item_type.value} ({digits}), Q to cancel:"
    renderer.safe_addstr(y0, 0, title, curses.A_BOLD)

    row = y0 + 1

    if allow_zero:
        current = session.hero.weapon
        weapon_name = f"{current.name} (+{current.value})" if current else "none"
        renderer.safe_addstr(row, 2, f"0. Unequip current weapon [{weapon_name}]")
        row += 1

    for idx, item in enumerate(items[:_MAX_VISIBLE_ITEMS], start=1):
        desc = f"{idx}. {item.name}"

        if item.stat is not None:
            desc += f" [{item.stat.value} +{item.value}]"
        elif item.value:
            desc += f" [+{item.value}]"

        if item.duration:
            desc += f" ({item.duration} turns)"

        renderer.safe_addstr(row, 2, desc)
        row += 1

    stdscr.refresh()


def _read_inventory_key(
    stdscr: curses.window,
    items: list,
    allow_zero: bool,
) -> int | None:
    """Читает выбор игрока."""

    while True:
        key = stdscr.getch()

        if key in (27, ord("q"), ord("Q")):
            return None

        if ord("0") <= key <= ord("9"):
            idx = key - ord("0")

            if idx == 0 and allow_zero:
                return 0

            if 1 <= idx <= min(9, len(items)):
                return idx