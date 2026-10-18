"""Точка входа в приложение Rogue 1980."""

from datalayer.storage import JsonDataLayer
from domain.engine import GameEngine
from presentation.curses_app import CursesApp


def main() -> None:
    """Создаёт зависимости и запускает curses-приложение."""
    engine = GameEngine()
    data_layer = JsonDataLayer("savegame.json")
    app = CursesApp(engine, data_layer)
    app.run()


if __name__ == "__main__":
    main()
