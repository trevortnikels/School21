"""Главный curses-контроллер приложения."""

from __future__ import annotations

import curses

from datalayer.storage import JsonDataLayer
from domain.engine import GameEngine
from domain.models import GameSession, ItemType
from presentation.input_handler import prompt_inventory_choice
from presentation.renderer import Renderer


class CursesApp:
    """Главный контроллер curses-приложения."""

    class Keys:
        UP = (curses.KEY_UP, ord('w'), ord('W'))
        DOWN = (curses.KEY_DOWN, ord('s'), ord('S'))
        LEFT = (curses.KEY_LEFT, ord('a'), ord('A'))
        RIGHT = (curses.KEY_RIGHT, ord('d'), ord('D'))
        ENTER = (curses.KEY_ENTER, 10, 13)
        CHANGE_2D_3D = (9, curses.KEY_BTAB)
        SAVE = (ord('q'), ord('Q'))
        ESC = 27
        WEAPON = ord('h')
        FOOD = ord('j')
        ELIXIR = ord('k')
        SCROLL = ord('e')
        NUMBS = (ord("1"), ord("2"), ord("3"), ord("4"), ord("5"))

    KEYS = Keys()

    def __init__(self, engine: GameEngine, data_layer: JsonDataLayer) -> None:
        self.engine = engine
        self.data_layer = data_layer
        self.first_person_mode: bool = False
        self.facing: int = 1

    def run(self) -> None:
        curses.wrapper(self._main)

    def _main(self, stdscr: curses.window) -> None:
        curses.curs_set(0)
        stdscr.nodelay(False)
        stdscr.keypad(True)

        renderer = Renderer(stdscr)

        while True:
            choice = self._menu(stdscr, renderer)
            match choice:
                case "new":
                    session = self.engine.new_session()
                    self.first_person_mode = False
                    self.facing = 1
                    self._game_loop(stdscr, renderer, session)
                case "continue":
                    session = self.data_layer.load_session()
                    if session is None:
                        renderer.show_message("No saved session found. Press any key.")
                        continue
                    self.first_person_mode = False
                    self.facing = 1
                    self._game_loop(stdscr, renderer, self.engine.from_saved(session))
                case "records":
                    renderer.show_records(self.data_layer.leaderboard())
                case "wiki":
                    renderer.show_small_wiki()
                case _:
                    return

    def _menu(self, stdscr: curses.window, renderer: Renderer) -> str:
        options = [
            ("new", "1. New game"),
            ("continue", "2. Continue"),
            ("records", "3. Leaderboard"),
            ("wiki", "4. Game wiki"),
            ("quit", "5. Quit"),
        ]
        selected = 0

        while True:
            stdscr.erase()
            renderer.safe_addstr(1, 2, "s21_Rogue (Python and curses)", curses.A_BOLD)
            renderer.safe_addstr(
                2, 2, "Use arrows, WASD or ""1-5"" to navigate, Enter or digit to select"
            )

            for idx, (_, label) in enumerate(options):
                attr = curses.A_REVERSE if idx == selected else curses.A_NORMAL
                renderer.safe_addstr(4 + idx, 4, label, attr)

            stdscr.refresh()
            key = stdscr.getch()
            
            if key in self.KEYS.UP:
                selected = (selected - 1) % len(options)
            elif key in self.KEYS.DOWN:
                selected = (selected + 1) % len(options)
            elif key in self.KEYS.ENTER:
                return options[selected][0]
            elif key in self.KEYS.NUMBS:
                return options[key - ord("1")][0]

    def _game_loop(
        self,
        stdscr: curses.window,
        renderer: Renderer,
        session: GameSession,
    ) -> None:
        while True:
            renderer.render_game(
                session,
                first_person=self.first_person_mode,
                facing=self.facing,
            )

            if session.game_over:
                self.data_layer.add_run_record(session.stats)
                self.data_layer.clear_session()

                ending = (
                    "Victory! You escaped the dungeon."
                    if session.victory
                    else "You died."
                )
                renderer.show_message(f"{ending} Press any key.")
                return

            prev_level = session.current_level
            key = stdscr.getch()

            if not self._handle_key(stdscr, renderer, session, key):
                return

            # Автосохранение после перехода на новый уровень
            if session.current_level != prev_level and not session.game_over:
                self.engine.save_rng_state(session)
                self.data_layer.save_session(session)

    def _handle_key(
        self,
        stdscr: curses.window,
        renderer: Renderer,
        session: GameSession,
        key: int,
    ) -> bool:
        # Переключение режима 2D / 3D
        if key in self.KEYS.CHANGE_2D_3D:
            self.first_person_mode = not self.first_person_mode
            session.message = (
                "3D mode enabled." if self.first_person_mode else "2D mode enabled."
            )
            return True

        # движение и поворот
        if key in self.KEYS.UP:
            if self.first_person_mode:
                dx, dy = self._facing_vector()
            else:
                dx, dy = (0, -1)
            self.engine.move_player(session, dx, dy)
        elif key in self.KEYS.DOWN:
            if self.first_person_mode:
                dx, dy = self._facing_vector()
            else:
                dx, dy = (0, -1)
            self.engine.move_player(session, -dx, -dy)
        elif key in self.KEYS.LEFT:
            if self.first_person_mode:
                self.facing = (self.facing - 1) % 4
                session.message = "You turn left."
            else:
                self.engine.move_player(session, -1, 0)
        elif key in self.KEYS.RIGHT:
            if self.first_person_mode:
                self.facing = (self.facing + 1) % 4
                session.message = "You turn right."
            else:
                self.engine.move_player(session, 1, 0) 

       
        # Инвентарь
        elif key == self.KEYS.WEAPON:
            idx = prompt_inventory_choice(
                stdscr, renderer, session, ItemType.WEAPON, allow_zero=True
            )
            if idx is not None:
                self.engine.use_item(session, ItemType.WEAPON, idx)

        elif key == self.KEYS.FOOD:
            idx = prompt_inventory_choice(stdscr, renderer, session, ItemType.FOOD)
            if idx is not None:
                self.engine.use_item(session, ItemType.FOOD, idx)

        elif key == self.KEYS.ELIXIR:
            idx = prompt_inventory_choice(stdscr, renderer, session, ItemType.ELIXIR)
            if idx is not None:
                self.engine.use_item(session, ItemType.ELIXIR, idx)

        elif key == self.KEYS.SCROLL:
            idx = prompt_inventory_choice(stdscr, renderer, session, ItemType.SCROLL)
            if idx is not None:
                self.engine.use_item(session, ItemType.SCROLL, idx)

        # Ручное сохранение
        elif key in self.KEYS.SAVE:
            self.engine.save_rng_state(session)
            self.data_layer.save_session(session)
            renderer.show_message("Game saved. Press any key.")

        # Выход без сохранения
        elif key == self.KEYS.ESC:
            renderer.show_message("Quit. Press any key.")
            return False

        return True

    def _facing_vector(self) -> tuple[int, int]:
        return {
            0: (0, -1),   # N
            1: (1, 0),    # E
            2: (0, 1),    # S
            3: (-1, 0),   # W
        }[self.facing % 4]