"""Рендерер игры на curses."""

# Структура Renderer
# ├── 3D Rendering (15 методов)
# ├── 2D Rendering (8 методов)  
# ├── HUD (12 методов)
# ├── Utility (5 методов)
# └── Public Interface (4 метода)

from __future__ import annotations

import curses
import math
from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Optional, Tuple, List

from domain.models import (
    EnemyType, GameSession, Item, ItemType, Level, Pos, RunStats, Tile
)

# CONSTANTS ==================================================

# Terminal
_MIN_LINES = 24
_MIN_COLS = 80
_HUD_OFFSET = 1

# 3D Rendering
_MAX_RAY_DEPTH = 24.0
_RAY_STEP = 0.08
_FOV = math.pi / 3
_HALF_FOV = _FOV / 2
_WALL_SHADES = "@#%*+=-:."

# 3D Viewport
_MIN_VIEW_WIDTH = 34
_MAX_VIEW_WIDTH = 110
_MIN_VIEW_HEIGHT = 14
_MAX_VIEW_HEIGHT = 36
_MIN_HUD_LINES = 10
_VIEWPORT_X = 1
_VIEWPORT_Y = 1

# 3D Distances & Thresholds
_MIN_SPRITE_DISTANCE = 0.35
_MIN_CORRECTED_DISTANCE = 0.10
_MIN_WALL_DISTANCE = 0.12
_MAX_SPRITE_FOV_ANGLE = 0.14
_SPRITE_DEPTH_OFFSET = 0.05
_ITEM_DEPTH_TOLERANCE = 0.10
_EXIT_DEPTH_TOLERANCE = 0.10
_WIDE_SPRITE_DISTANCE = 2.2
_DIM_SPRITE_DISTANCE = 7.0

# Wall Rendering
_WALL_CLOSE_DISTANCE = 3.0
_WALL_MEDIUM_DISTANCE = 6.0
_WALL_FAR_DISTANCE = 8.0
_WALL_SHADE_MULTIPLIER = 0.8
_WALL_PATTERN_DISTANCE = 4.5
_DOOR_CLOSE_DISTANCE = 2.3
_DOOR_MEDIUM_DISTANCE = 5.0

# Sprite Scaling
_MIN_SPRITE_SCALE_DISTANCE = 0.22
_DEFAULT_ENEMY_SCALE = 1.0
_DEFAULT_ITEM_SCALE = 0.55
_DEFAULT_EXIT_SCALE = 0.62

# Minimap
_MIN_MINIMAP_WIDTH = 14
_MAX_MINIMAP_WIDTH = 22
_MIN_MINIMAP_HEIGHT = 8
_MAX_MINIMAP_HEIGHT = 12
_MINI_SCREEN_DIV_W = 4
_MINI_SCREEN_DIV_H = 5
_MIN_MINI_OFFSET_W = 10
_MIN_MINI_OFFSET_H = 6

# HUD
_HUD_3D_Y = 1
_HUD_MIN_LINES = 7
_LEVEL_HEIGHT_ESTIMATE = 21

# Records
_RECORDS_HEADER_Y = 3
_RECORDS_START_Y = 4
_RECORDS_MARGIN_Y = 7

# Wiki
_WIKI_TITLE_Y = 1      
_WIKI_TITLE_X = 2      
_WIKI_CONTENT_Y = 2      
_WIKI_X_MARGIN = 2     
_WIKI_RETURN_Y_OFFSET = 2  
_WIKI_HEADER_INDICES = {0, 10, 13, 19}

# CONSTANTS ==================================================


@dataclass
class Viewport:
    """Размеры области просмотра."""
    x: int
    y: int
    width: int
    height: int


@dataclass
class Sprite:
    """3D спрайт для рендеринга."""
    distance: float
    angle: float
    symbol: str
    attr: int
    scale: float


class ColorPairs(Enum):
    """Цветовые пары для curses."""
    RED = 1
    GREEN = 2
    YELLOW = 3
    CYAN = 4
    WHITE = 5
    BLUE = 6
    MAGENTA = 7


class Renderer:
    """Отвечает за весь вывод в curses."""

    def __init__(self, stdscr: curses.window) -> None:
        self.stdscr = stdscr
        self._init_colors()

    def render_game(
        self,
        session: GameSession,
        first_person: bool = False,
        facing: int = 1,
    ) -> None:
        if not self._check_terminal_size():
            return

        self.stdscr.erase()

        if first_person:
            self._render_first_person(session, facing)
        else:
            self._render_top_down(session, facing)

        self.stdscr.refresh()

    def _render_first_person(self, session: GameSession, facing: int) -> None:
        """Рендеринг вида от первого лица."""
        viewport = self._calculate_viewport()
        self._draw_box(0, 0, viewport.height + 2, viewport.width + 2, " First Person ")
        
        self._render_sky_and_ground(viewport)
        self._render_3d_walls(session, viewport, facing)
        self._render_3d_sprites(session, viewport, facing)
        self._draw_crosshair(viewport)
        self._render_minimap(session, viewport, facing)
        self._render_hud(session, "3D", facing)

    def _render_top_down(self, session: GameSession, facing: int) -> None:
        """Рендеринг вида сверху."""
        level = session.level
        visible = session.last_visible

        self._render_tiles(session, visible)
        self._render_items(level, visible)
        self._render_enemies(level, visible)
        self._render_hero(session)
        self._render_hud(session, "2D", facing)

    # ---------------- 3D Rendering ----------------

    def _calculate_viewport(self) -> Viewport:
        """Вычисляет размеры области 3D вида."""
        view_w = max(_MIN_VIEW_WIDTH, min(curses.COLS - 2, _MAX_VIEW_WIDTH))
        view_h = max(_MIN_VIEW_HEIGHT, min(curses.LINES - _MIN_HUD_LINES, _MAX_VIEW_HEIGHT))
        return Viewport(_VIEWPORT_X, _VIEWPORT_Y, view_w, view_h)

    def _render_sky_and_ground(self, viewport: Viewport) -> None:
        """Рендерит небо и землю."""
        horizon = viewport.height // 2
        
        for y in range(viewport.height):
            for x in range(viewport.width):
                if y < horizon:
                    ch, attr = self._sky_pixel(horizon, y)
                else:
                    ch, attr = self._ground_pixel(horizon, y, viewport.height)
                self.safe_addstr(viewport.y + y, viewport.x + x, ch, attr)

    def _sky_pixel(self, horizon: int, y: int) -> Tuple[str, int]:
        """Пиксель неба."""
        t = (horizon - y) / max(1, horizon)
        ch = " " if t > 0.55 else "."
        return ch, curses.color_pair(ColorPairs.CYAN.value) | curses.A_DIM

    def _ground_pixel(self, horizon: int, y: int, height: int) -> Tuple[str, int]:
        """Пиксель земли."""
        t = (y - horizon) / max(1, height - horizon)
        if t < 0.20:
            ch = "."
        elif t < 0.55:
            ch = ","
        else:
            ch = ";"
        return ch, curses.color_pair(ColorPairs.CYAN.value) | curses.A_DIM

    def _render_3d_walls(self, session: GameSession, viewport: Viewport, facing: int) -> None:
        """Рендерит стены в 3D."""
        level = session.level
        hero_pos = session.hero_pos
        dir_angle = self._direction_angle(facing)
        depth_buffer = [_MAX_RAY_DEPTH] * viewport.width

        for col in range(viewport.width):
            ray_angle = dir_angle - _FOV / 2 + (col / max(1, viewport.width - 1)) * _FOV
            dist, hit_tile = self._cast_ray(level, hero_pos, ray_angle)
            corrected_dist = max(_MIN_WALL_DISTANCE, dist * math.cos(ray_angle - dir_angle))
            depth_buffer[col] = corrected_dist

            self._draw_wall_column(viewport, col, corrected_dist, hit_tile)

    def _draw_wall_column(self, viewport: Viewport, col: int, distance: float, hit_tile: Optional[str]) -> None:
        """Рисует колонну стены."""
        wall_h = min(viewport.height, int(viewport.height / distance))
        top = max(0, (viewport.height - wall_h) // 2)
        bottom = min(viewport.height - 1, top + wall_h)

        wall_char = self._wall_texture(distance, hit_tile)
        wall_attr = self._wall_color(hit_tile, distance)

        for y in range(top, bottom + 1):
            draw_ch = wall_char
            if (y - top) % 2 == 1 and distance > _WALL_PATTERN_DISTANCE:
                draw_ch = wall_char.lower() if wall_char.isalpha() else wall_char
            self.safe_addstr(viewport.y + y, viewport.x + col, draw_ch, wall_attr)

    def _cast_ray(self, level: Level, hero_pos: Pos, angle: float) -> Tuple[float, Optional[str]]:
        """Бросает луч для определения расстояния до стены."""
        x, y = hero_pos.x + 0.5, hero_pos.y + 0.5
        dist = 0.0

        while dist < _MAX_RAY_DEPTH:
            dist += _RAY_STEP
            x += math.cos(angle) * _RAY_STEP
            y += math.sin(angle) * _RAY_STEP

            pos = Pos(int(x), int(y))
            if not level.is_inside(pos):
                return _MAX_RAY_DEPTH, None

            tile = level.tile_at(pos)
            if self._is_wall(tile):
                return dist, tile

        return _MAX_RAY_DEPTH, None

    def _is_wall(self, tile: str) -> bool:
        """Проверяет, является ли тайл стеной."""
        return tile in {
            Tile.WALL.value,
            Tile.DOOR_RED.value,
            Tile.DOOR_BLUE.value,
            Tile.DOOR_YELLOW.value,
        }

    def _wall_texture(self, distance: float, hit_tile: Optional[str]) -> str:
        """Текстура стены в зависимости от типа и расстояния."""
        if hit_tile in {Tile.DOOR_RED.value, Tile.DOOR_BLUE.value, Tile.DOOR_YELLOW.value}:
            if distance < _DOOR_CLOSE_DISTANCE:
                return "H"
            if distance < _DOOR_MEDIUM_DISTANCE:
                return "I"
            return "|"

        idx = min(len(_WALL_SHADES) - 1, int(distance * _WALL_SHADE_MULTIPLIER))
        return _WALL_SHADES[idx]

    def _wall_color(self, hit_tile: Optional[str], distance: float) -> int:
        """Цвет стены."""
        if hit_tile == Tile.DOOR_RED.value:
            attr = curses.color_pair(ColorPairs.RED.value) | curses.A_BOLD
        elif hit_tile == Tile.DOOR_BLUE.value:
            attr = curses.color_pair(ColorPairs.BLUE.value) | curses.A_BOLD
        elif hit_tile == Tile.DOOR_YELLOW.value:
            attr = curses.color_pair(ColorPairs.YELLOW.value) | curses.A_BOLD
        else:
            base_attr = curses.color_pair(ColorPairs.BLUE.value)
            if distance < _WALL_CLOSE_DISTANCE:
                attr = base_attr | curses.A_BOLD
            elif distance < _WALL_MEDIUM_DISTANCE:
                attr = base_attr
            else:
                attr = base_attr | curses.A_DIM

        if distance > _WALL_FAR_DISTANCE:
            attr |= curses.A_DIM
        return attr

    def _render_3d_sprites(self, session: GameSession, viewport: Viewport, facing: int) -> None:
        """Рендерит спрайты в 3D."""
        sprites = self._collect_sprites(session, viewport, facing)
        sprites.sort(reverse=True, key=lambda s: s.distance)

        depth_buffer = [_MAX_RAY_DEPTH] * viewport.width
        hero_x, hero_y = session.hero_pos.x + 0.5, session.hero_pos.y + 0.5

        for sprite in sprites:
            self._draw_sprite(viewport, sprite, depth_buffer, hero_x, hero_y)

    def _collect_sprites(
        self, 
        session: GameSession, 
        viewport: Viewport, 
        facing: int
    ) -> List[Sprite]:
        """Собирает все видимые спрайты."""
        sprites: List[Sprite] = []
        dir_angle = self._direction_angle(facing)
        hero_x, hero_y = session.hero_pos.x + 0.5, session.hero_pos.y + 0.5

        # Enemies
        sprites.extend(self._collect_enemy_sprites(session, dir_angle, hero_x, hero_y))
        
        # Items
        sprites.extend(self._collect_item_sprites(session.level, dir_angle, hero_x, hero_y))
        
        # Exit
        sprites.extend(self._collect_exit_sprite(session, dir_angle, hero_x, hero_y))

        return sprites

    def _collect_enemy_sprites(
        self, 
        session: GameSession, 
        dir_angle: float, 
        hero_x: float, 
        hero_y: float
    ) -> List[Sprite]:
        """Собирает спрайты врагов."""
        sprites = []
        level = session.level
        
        for enemy in level.enemies.values():
            if enemy.enemy_type == EnemyType.GHOST and not enemy.ghost_visible:
                continue

            sprite_info = self._enemy_sprite_info(enemy, hero_x, hero_y, dir_angle, level)
            if sprite_info:
                dist, rel_angle, symbol, attr, scale = sprite_info
                sprites.append(Sprite(dist, rel_angle, symbol, attr | curses.A_BOLD, scale))
        
        return sprites

    def _enemy_sprite_info(
        self,
        enemy,
        hero_x: float,
        hero_y: float,
        dir_angle: float,
        level: Level
    ) -> Optional[Tuple[float, float, str, int, float]]:
        """Информация о спрайте врага."""
        dx = enemy.pos.x + 0.5 - hero_x
        dy = enemy.pos.y + 0.5 - hero_y
        raw_dist = math.hypot(dx, dy)

        if raw_dist < _MIN_SPRITE_DISTANCE or raw_dist > _MAX_RAY_DEPTH:
            return None

        rel_angle = self._norm_angle(math.atan2(dy, dx) - dir_angle)
        if abs(rel_angle) > _HALF_FOV + _MAX_SPRITE_FOV_ANGLE:
            return None

        center_dist, _ = self._cast_ray(level, Pos(int(hero_x), int(hero_y)), dir_angle + rel_angle)
        corrected_dist = max(_MIN_CORRECTED_DISTANCE, raw_dist * math.cos(rel_angle))
        
        if corrected_dist > center_dist + _ITEM_DEPTH_TOLERANCE:
            return None

        symbol = enemy.symbol if not (enemy.enemy_type == EnemyType.MIMIC and enemy.disguised) else enemy.mimic_item_symbol or "?"
        return corrected_dist, rel_angle, symbol, curses.color_pair(enemy.color), _DEFAULT_ENEMY_SCALE

    def _collect_item_sprites(
        self, 
        level: Level, 
        dir_angle: float, 
        hero_x: float, 
        hero_y: float
    ) -> List[Sprite]:
        """Собирает спрайты предметов."""
        sprites = []
        hero_pos = Pos(int(hero_x), int(hero_y))
        
        for (x, y), item in level.items.items():
            dx = x + 0.5 - hero_x
            dy = y + 0.5 - hero_y
            raw_dist = math.hypot(dx, dy)

            if raw_dist < _MIN_SPRITE_DISTANCE or raw_dist > _MAX_RAY_DEPTH:
                continue

            rel_angle = self._norm_angle(math.atan2(dy, dx) - dir_angle)
            if abs(rel_angle) > _HALF_FOV + _MAX_SPRITE_FOV_ANGLE:
                continue

            center_dist, _ = self._cast_ray(level, hero_pos, dir_angle + rel_angle)
            corrected_dist = max(_MIN_CORRECTED_DISTANCE, raw_dist * math.cos(rel_angle))
            if corrected_dist > center_dist + _MIN_CORRECTED_DISTANCE:
                continue

            sym, attr = self._item_symbol(item)
            sprites.append(Sprite(corrected_dist, rel_angle, sym, attr, _DEFAULT_ITEM_SCALE))
        
        return sprites

    def _collect_exit_sprite(
        self, 
        session: GameSession, 
        dir_angle: float, 
        hero_x: float, 
        hero_y: float
    ) -> List[Sprite]:
        """Собирает спрайт выхода."""
        sprites = []
        level = session.level
        hero_pos = Pos(int(hero_x), int(hero_y))
        
        exit_pos = level.exit_pos
        if exit_pos == session.hero_pos:
            return sprites

        dx = exit_pos.x + 0.5 - hero_x
        dy = exit_pos.y + 0.5 - hero_y
        raw_dist = math.hypot(dx, dy)

        if _MIN_SPRITE_DISTANCE < raw_dist <= _MAX_RAY_DEPTH:
            rel_angle = self._norm_angle(math.atan2(dy, dx) - dir_angle)
            if abs(rel_angle) <= _HALF_FOV + _MAX_SPRITE_FOV_ANGLE:
                center_dist, _ = self._cast_ray(level, hero_pos, dir_angle + rel_angle)
                corrected_dist = max(_MIN_CORRECTED_DISTANCE, raw_dist * math.cos(rel_angle))
                if corrected_dist <= center_dist + _EXIT_DEPTH_TOLERANCE:
                    sprites.append(Sprite(
                        corrected_dist, rel_angle, Tile.EXIT.value, 
                        curses.color_pair(ColorPairs.WHITE.value) | curses.A_BOLD, _DEFAULT_EXIT_SCALE
                    ))
        return sprites

    def _draw_sprite(
        self, 
        viewport: Viewport, 
        sprite: Sprite, 
        depth_buffer: List[float], 
        hero_x: float, 
        hero_y: float
    ) -> None:
        """Рисует спрайт с учетом Z-буфера."""
        center_col = int(((sprite.angle + _HALF_FOV) / _FOV) * (viewport.width - 1))
        sprite_h = max(1, min(viewport.height - 2, int((viewport.height / max(_MIN_SPRITE_SCALE_DISTANCE, sprite.distance)) * sprite.scale)))
        sprite_w = 1 if sprite.distance > _WIDE_SPRITE_DISTANCE else 2

        top = max(0, viewport.height // 2 - sprite_h // 2 + (2 if sprite.scale < _DEFAULT_ENEMY_SCALE else 0))
        bottom = min(viewport.height - 1, top + sprite_h - 1)
        left = center_col - sprite_w // 2
        right = left + sprite_w - 1

        for col in range(left, right + 1):
            if col < 0 or col >= viewport.width or sprite.distance >= depth_buffer[col] - _SPRITE_DEPTH_OFFSET:
                continue

            draw_attr = sprite.attr | (curses.A_DIM if sprite.distance > _DIM_SPRITE_DISTANCE else 0)

            for row in range(top, bottom + 1):
                self.safe_addstr(viewport.y + row, viewport.x + col, sprite.symbol, draw_attr)

            depth_buffer[col] = sprite.distance

    def _draw_crosshair(self, viewport: Viewport) -> None:
        """Рисует прицел."""
        cross_x = viewport.x + viewport.width // 2
        cross_y = viewport.y + viewport.height // 2
        self.safe_addstr(cross_y, cross_x, "+", curses.color_pair(ColorPairs.WHITE.value) | curses.A_BOLD)

    def _render_minimap(self, session: GameSession, viewport: Viewport, facing: int) -> None:
        """Рендерит миникарту."""
        mini_w = min(_MAX_MINIMAP_WIDTH, max(_MIN_MINIMAP_WIDTH, curses.COLS // _MINI_SCREEN_DIV_W))
        mini_h = min(_MAX_MINIMAP_HEIGHT, max(_MIN_MINIMAP_HEIGHT, curses.LINES // _MINI_SCREEN_DIV_H))
        mini_w = min(mini_w, max(_MIN_MINI_OFFSET_W, viewport.width - 4))
        mini_h = min(mini_h, max(_MIN_MINI_OFFSET_H, viewport.height - 4))
        mini_x = max(2, viewport.width - mini_w)
        mini_y = 0

        self._draw_box(mini_y, mini_x, mini_h + 2, mini_w + 2, " Map ")
        self._draw_minimap_content(session, facing, mini_x + 1, mini_y + 1, mini_w, mini_h)

    def _draw_minimap_content(
        self, 
        session: GameSession, 
        facing: int, 
        x0: int, 
        y0: int, 
        width: int, 
        height: int
    ) -> None:
        """Рендерит содержимое миникарты."""
        level = session.level
        visible = session.last_visible
        half_w, half_h = width // 2, height // 2

        for sy in range(height):
            my = session.hero_pos.y - half_h + sy
            for sx in range(width):
                mx = session.hero_pos.x - half_w + sx
                self._draw_minimap_cell(level, visible, session, facing, x0 + sx, y0 + sy, mx, my)

    def _draw_minimap_cell(
        self,
        level: Level,
        visible: set[tuple[int, int]],
        session: GameSession,
        facing: int,
        x: int,
        y: int,
        mx: int,
        my: int
    ) -> None:
        """Рисует одну клетку миникарты."""
        pos = Pos(mx, my)
        if not level.is_inside(pos):
            self.safe_addstr(y, x, " ")
            return

        if not self._is_minimap_visible(level, visible, mx, my):
            self.safe_addstr(y, x, " ")
            return

        ch, attr = self._minimap_cell_content(level, visible, session, mx, my, facing)
        self.safe_addstr(y, x, ch, attr)

    def _is_minimap_visible(self, level: Level, visible: set[tuple[int, int]], x: int, y: int) -> bool:
        """Проверяет видимость клетки на миникарте."""
        room = level.room_for(Pos(x, y))
        return ((x, y) in visible or 
                (x, y) in level.discovered_corridors or 
                (room is not None and room.discovered))

    def _minimap_cell_content(
        self,
        level: Level,
        visible: set[tuple[int, int]],
        session: GameSession,
        x: int,
        y: int,
        facing: int
    ) -> Tuple[str, int]:
        """Определяет символ и цвет клетки миникарты."""
        # Проверяем героя
        if (x, y) == (session.hero_pos.x, session.hero_pos.y):
            return ["^", ">", "v", "<"][facing % 4], curses.color_pair(ColorPairs.WHITE.value) | curses.A_BOLD

        # Проверяем предметы
        item = level.items.get((x, y))
        if item is not None and (x, y) in visible:
            return self._item_symbol(item)

        # Проверяем врагов
        enemy = next((e for e in level.enemies.values() if e.pos.x == x and e.pos.y == y), None)
        if enemy is not None and (x, y) in visible and not (enemy.enemy_type == EnemyType.GHOST and not enemy.ghost_visible):
            if enemy.enemy_type == EnemyType.MIMIC and enemy.disguised:
                return enemy.mimic_item_symbol or "?", curses.color_pair(ColorPairs.WHITE.value)
            return enemy.symbol, curses.color_pair(enemy.color)

        # Обычные тайлы
        return self._tile_minimap_symbol(level.tile_at(Pos(x, y)))

    def _tile_minimap_symbol(self, tile: str) -> Tuple[str, int]:
        """Символ тайла для миникарты."""
        if tile == Tile.WALL.value:
            return tile, curses.color_pair(ColorPairs.BLUE.value)
        elif tile == Tile.EXIT.value:
            return tile, curses.color_pair(ColorPairs.WHITE.value)
        elif tile == Tile.DOOR_RED.value:
            return tile, curses.color_pair(ColorPairs.RED.value) | curses.A_BOLD
        elif tile == Tile.DOOR_BLUE.value:
            return tile, curses.color_pair(ColorPairs.BLUE.value) | curses.A_BOLD
        elif tile == Tile.DOOR_YELLOW.value:
            return tile, curses.color_pair(ColorPairs.YELLOW.value) | curses.A_BOLD
        else:
            return ".", curses.color_pair(ColorPairs.CYAN.value) | curses.A_DIM

    # ---------------- 2D Rendering ----------------

    def _render_tiles(self, session: GameSession, visible: set[tuple[int, int]]) -> None:
        """Рендерит тайлы уровня."""
        level = session.level
        for y in range(level.height):
            for x in range(level.width):
                ch, color = self._tile_char(level, x, y, visible)
                self.safe_addstr(y, x, ch, color)

    def _tile_char(
        self, level: Level, x: int, y: int, visible: set[tuple[int, int]]
    ) -> Tuple[str, int]:
        """Определяет символ и цвет тайла."""
        pos = Pos(x, y)
        room = level.room_for(pos)
        tile = level.tile_at(pos)
        is_visible = (x, y) in visible

        ch = self._determine_tile_char(room, tile, is_visible, level.discovered_corridors, x, y)
        color = self._tile_color(ch)

        return ch, color

    def _determine_tile_char(
        self,
        room,
        tile: str,
        is_visible: bool,
        discovered_corridors: set[tuple[int, int]],
        x: int,
        y: int
    ) -> str:
        """Определяет символ тайла с учетом видимости."""
        if room is not None:
            if not room.discovered:
                return " "
            elif not is_visible:
                if x in (room.x1, room.x2) or y in (room.y1, room.y2):
                    return tile if tile != Tile.FLOOR.value else " "
                return " "
            else:
                return tile
        else:
            if is_visible:
                return tile
            elif (x, y) in discovered_corridors:
                return tile if tile != Tile.FLOOR.value else " "
            return " "

    def _tile_color(self, ch: str) -> int:
        """Цвет тайла."""
        color_map = {
            Tile.WALL.value: curses.color_pair(ColorPairs.BLUE.value),
            Tile.EXIT.value: curses.color_pair(ColorPairs.WHITE.value),
            Tile.FLOOR.value: curses.color_pair(ColorPairs.CYAN.value),
            Tile.DOOR_RED.value: curses.color_pair(ColorPairs.RED.value) | curses.A_BOLD,
            Tile.DOOR_BLUE.value: curses.color_pair(ColorPairs.BLUE.value) | curses.A_BOLD,
            Tile.DOOR_YELLOW.value: curses.color_pair(ColorPairs.YELLOW.value) | curses.A_BOLD,
        }
        return color_map.get(ch, 0)

    def _render_items(self, level: Level, visible: set[tuple[int, int]]) -> None:
        """Рендерит предметы."""
        for (x, y), item in level.items.items():
            if self._should_render_item(level, visible, x, y):
                sym, attr = self._item_symbol(item)
                self.safe_addstr(y, x, sym, attr)

    def _should_render_item(self, level: Level, visible: set[tuple[int, int]], x: int, y: int) -> bool:
        """Проверяет, нужно ли рендерить предмет."""
        if (x, y) not in visible:
            return False
        room = level.room_for(Pos(x, y))
        return room is None or room.discovered

    def _render_enemies(self, level: Level, visible: set[tuple[int, int]]) -> None:
        """Рендерит врагов."""
        for enemy in level.enemies.values():
            pos = (enemy.pos.x, enemy.pos.y)
            if (pos not in visible or 
                (enemy.enemy_type == EnemyType.GHOST and not enemy.ghost_visible)):
                continue

            symbol = enemy.mimic_item_symbol or "?" if enemy.enemy_type == EnemyType.MIMIC and enemy.disguised else enemy.symbol
            self.safe_addstr(enemy.pos.y, enemy.pos.x, symbol, curses.color_pair(enemy.color))

    def _render_hero(self, session: GameSession) -> None:
        """Рендерит героя."""
        self.safe_addstr(
            session.hero_pos.y, session.hero_pos.x, "@",
            curses.color_pair(ColorPairs.WHITE.value) | curses.A_BOLD
        )

    # ---------------- HUD ----------------

    def _render_hud(self, session: GameSession, mode_label: str, facing: int) -> None:
        """Рендерит интерфейс."""
        info_y = self._hud_y_position(mode_label)
        
        self.safe_addstr(info_y, 0, self._hud_status_line(session, mode_label))
        self.safe_addstr(info_y + 1, 0, self._hud_inventory_line(session))
        self.safe_addstr(info_y + 2, 0, self._hud_keys_line(session))
        self.safe_addstr(info_y + 3, 0, self._hud_controls_line(mode_label, facing))
        self.safe_addstr(info_y + 4, 0, self._hud_mode_line(mode_label, facing))
        
        self._render_hud_message(session, info_y + 5)
        self._render_sleep_status(session, info_y + 6)

    def _hud_y_position(self, mode_label: str) -> int:
        """Позиция HUD."""
        return max(_HUD_3D_Y, curses.LINES - _HUD_MIN_LINES) if mode_label == "3D" else min(_LEVEL_HEIGHT_ESTIMATE + _HUD_OFFSET, curses.LINES - _HUD_MIN_LINES)

    def _hud_status_line(self, session: GameSession, mode_label: str) -> str:
        """Строка статуса."""
        hero = session.hero
        return (f"[{mode_label}] Lvl {session.current_level}/21 | "
                f"HP {hero.hp}/{hero.max_hp} | "
                f"AGI {hero.agility} | STR {hero.strength} | "
                f"Treasure {session.backpack.treasure}")

    def _hud_inventory_line(self, session: GameSession) -> str:
        """Строка инвентаря."""
        hero = session.hero
        bp_size = session.backpack._max_slot_size
        weapon_str = f"{hero.weapon.name} (+{hero.weapon.value})" if hero.weapon else "none"
        
        return (f"Equiped W: {weapon_str} | "
                f"Foods:{len(session.backpack.food)}/{bp_size} | "
                f"Elixirs:{len(session.backpack.elixir)}/{bp_size} | "
                f"Scrolls:{len(session.backpack.scroll)}/{bp_size} | "
                f"Weapons:{len(session.backpack.weapon)}/{bp_size}")

    def _hud_keys_line(self, session: GameSession) -> str:
        """Строка ключей."""
        keys_str = ", ".join(session.backpack.keys) if session.backpack.keys else "none"
        return f"Keys: {keys_str}"

    def _hud_controls_line(self, mode_label: str, facing: int) -> str:
        """Строка управления."""
        if mode_label == "3D":
            return "3D: W/S move | A/D turn | h/j/k/e items | Tab mode | q save | Esc quit"
        return "2D: WASD move | h weapon | j food | k elixir | e scroll | q save | Esc quit"

    def _hud_mode_line(self, mode_label: str, facing: int) -> str:
        """Строка режима."""
        return f"Facing: {['N', 'E', 'S', 'W'][facing % 4]}" if mode_label == "3D" else ""

    def _render_hud_message(self, session: GameSession, y: int) -> None:
        """Рендерит сообщение."""
        display_msg = session.flash_message or session.message
        attr = curses.color_pair(ColorPairs.YELLOW.value) | curses.A_BOLD if session.flash_message else 0
        self.safe_addstr(y, 0, display_msg, attr)
        session.flash_message = ""

    def _render_sleep_status(self, session: GameSession, y: int) -> None:
        """Рендерит статус сна."""
        if session.sleep_turns > 0:
            self.safe_addstr(
                y, 0, f"*** SLEEPING ({session.sleep_turns} turns) ***",
                curses.color_pair(ColorPairs.RED.value) | curses.A_BOLD
            )

    # ---------------- Utility ----------------

    def _direction_angle(self, facing: int) -> float:
        """Угол направления."""
        return [-math.pi / 2, 0.0, math.pi / 2, math.pi][facing % 4]

    def _norm_angle(self, angle: float) -> float:
        """Нормализует угол в диапазон [-π, π]."""
        while angle <= -math.pi:
            angle += 2 * math.pi
        while angle > math.pi:
            angle -= 2 * math.pi
        return angle

    def _draw_box(self, y: int, x: int, h: int, w: int, title: str = "") -> None:
        """Рисует рамку."""
        if h < 2 or w < 2:
            return

        # Горизонтальные линии
        for cx in range(x, x + w):
            self.safe_addstr(y, cx, "-")
            self.safe_addstr(y + h - 1, cx, "-")
        
        # Вертикальные линии
        for cy in range(y + 1, y + h - 1):
            self.safe_addstr(cy, x, "|")
            self.safe_addstr(cy, x + w - 1, "|")
        
        # Углы
        self.safe_addstr(y, x, "+")
        self.safe_addstr(y, x + w - 1, "+")
        self.safe_addstr(y + h - 1, x, "+")
        self.safe_addstr(y + h - 1, x + w - 1, "+")
        
        # Заголовок
        if title:
            title_text = title[:max(0, w - 4)]
            self.safe_addstr(y, x + 2, title_text, curses.A_BOLD)

    def _item_symbol(self, item: Item | ItemType) -> Tuple[str, int]:
        """Символ и цвет предмета."""
        item_type = item if isinstance(item, ItemType) else item.item_type
        item_name = "" if isinstance(item, ItemType) else item.name

        symbol_map = {
            ItemType.TREASURE: ("$", ColorPairs.YELLOW.value),
            ItemType.FOOD: ("%", ColorPairs.GREEN.value),
            ItemType.ELIXIR: ("!", ColorPairs.WHITE.value),
            ItemType.SCROLL: ("?", ColorPairs.MAGENTA.value),
        }
        
        if item_type in symbol_map:
            sym, color = symbol_map[item_type]
            return sym, curses.color_pair(color)
        
        if item_type == ItemType.KEY:
            return self._key_symbol(item_name)
        
        return "/", curses.color_pair(ColorPairs.RED.value)

    def _key_symbol(self, key_name: str) -> Tuple[str, int]:
        """Символ ключа по цвету."""
        color_map = {
            "red": ColorPairs.RED.value,
            "blue": ColorPairs.BLUE.value,
            "yellow": ColorPairs.YELLOW.value,
        }
        color_pair = curses.color_pair(color_map.get(key_name, ColorPairs.WHITE.value))
        return "k", color_pair | curses.A_BOLD

    # ---------------- Public Interface ----------------

    def show_records(self, rows: list[RunStats]) -> None:
        """Показывает таблицу рекордов."""
        self.stdscr.erase()
        self.safe_addstr(1, 2, "Leaderboard (by treasure)", curses.A_BOLD)
        self.safe_addstr(_RECORDS_HEADER_Y, 2, self._records_header())
        
        max_rows = max(0, curses.LINES - _RECORDS_MARGIN_Y)
        for i, row in enumerate(rows[:max_rows], start=1):
            self.safe_addstr(_RECORDS_START_Y + i, 2, self._format_record_row(i, row))
        
        self.safe_addstr(curses.LINES - _WIKI_RETURN_Y_OFFSET, 2, "Press any key to return")
        self.stdscr.refresh()
        self.stdscr.getch()

    def _records_header(self) -> str:
        """Заголовок таблицы рекордов."""
        return "#   Trea  Lvl  Kills  Food  Elix  Scroll  Hits+  Hits-  Steps"

    def _format_record_row(self, index: int, row: RunStats) -> str:
        """Форматирует строку рекорда."""
        return (f"{index:>2}  "
                f"{row.treasure:>6}  "
                f"{row.reached_level:>3}  "
                f"{row.kills:>5}  "
                f"{row.food_used:>4}  "
                f"{row.elixirs_used:>4}  "
                f"{row.scrolls_used:>6}  "
                f"{row.hits_dealt:>5}  "
                f"{row.hits_taken:>5}  "
                f"{row.steps:>5}")

    def show_message(self, text: str) -> None:
        """Показывает сообщение."""
        self.stdscr.erase()
        self.safe_addstr(2, 2, text)
        self.stdscr.refresh()
        self.stdscr.getch()

    def show_small_wiki(self) -> None:
        """Показывает вики."""
        wiki_content = self._wiki_content()
        
        self.stdscr.erase()
        self.safe_addstr(_WIKI_TITLE_Y, _WIKI_TITLE_X, "Small wiki (Full annotation in src/readme.md)", curses.A_BOLD)
        
        for i, line in enumerate(wiki_content):
            self.safe_addstr(i + _WIKI_CONTENT_Y, _WIKI_X_MARGIN, line, curses.A_BOLD if self._is_wiki_header(i) else 0)
        
        self.safe_addstr(curses.LINES - _WIKI_RETURN_Y_OFFSET, _WIKI_X_MARGIN, "Press any key to return")
        self.stdscr.refresh()
        self.stdscr.getch()

    def _wiki_content(self) -> List[str]:
        """Содержимое вики."""
        return [
            "    Game:",
            "The game has 21 levels and 9 rooms on each level",
            "The rooms are connected by corridors",
            "Use colored keys to open matching doors",
            "Doors: R-Red, G-Green, B-Blue. Keys: color \"k\"",
            "Hero indicated by the \"@\"",
            "To complete the level you must find Exit indicated by the \"E\"",
            "To complete the game you must reach and complete 21 lvl",
            "In the rooms you also can meet enemies and items",
            "    Enemies: The enemies are getting stronger every 3 lvl",
            "Zombie - \"z\", Vampire - \"v\", Ghost - \"g\", Ogre - \"o\", Snake_Mage - \"s\", Mimic - \"m\"",
            "The reward from enemy kills also getting more every 3 lvl (depends on stats)",
            "    Items:",
            "Food - \"%\", Weapon - \"/\", Scroll - \"?\", Elixir - \"!\"",
            "Food - increases your hp, but not more than max hp",
            "Weapon - you can take it in your hand and stand more strong",
            "Scroll - you can read the scroll to FOREVER increase your stats",
            "Elixir - you can read the scroll to TEMPORARILY increase your stats",
            "    Buttons:",
            "To swtch 2D <-> 3D: \"Tab\"",
            "Movings: 2D - arrows/WSAD, 3D - UP/DOWN/W/S, Turn right/left - RIGHT/LEFT/A/D.",
            "Open backpack: h - weapons, j - foods, k - elixirs, e - scrolls,",
            "To save or exit withot saving: q - save game, esc - quit from game."
        ]

    def _is_wiki_header(self, index: int) -> bool:
        """Проверяет, является ли строка заголовком вики."""
        return index in _WIKI_HEADER_INDICES

    # ---------------- Helpers ----------------

    def safe_addstr(self, y: int, x: int, text: str, attr: int = 0) -> None:
        """Безопасно выводит строку."""
        if y < 0 or x < 0 or y >= curses.LINES or x >= curses.COLS:
            return

        max_len = max(0, curses.COLS - x)
        try:
            self.stdscr.addstr(y, x, text[:max_len], attr)
        except curses.error:
            pass

    def _init_colors(self) -> None:
        """Инициализирует цвета."""
        if not curses.has_colors():
            return

        curses.start_color()
        curses.use_default_colors()
        
        color_pairs = [
            (ColorPairs.RED.value, curses.COLOR_RED),
            (ColorPairs.GREEN.value, curses.COLOR_GREEN),
            (ColorPairs.YELLOW.value, curses.COLOR_YELLOW),
            (ColorPairs.CYAN.value, curses.COLOR_CYAN),
            (ColorPairs.WHITE.value, curses.COLOR_WHITE),
            (ColorPairs.BLUE.value, curses.COLOR_BLUE),
            (ColorPairs.MAGENTA.value, curses.COLOR_MAGENTA),
        ]
        
        for pair_num, color in color_pairs:
            curses.init_pair(pair_num, color, -1)

    def _check_terminal_size(self) -> bool:
        """Проверяет размер терминала."""
        if curses.LINES >= _MIN_LINES and curses.COLS >= _MIN_COLS:
            return True

        self.stdscr.erase()
        msg = f"Terminal too small: need {_MIN_COLS}x{_MIN_LINES}, got {curses.COLS}x{curses.LINES}"
        try:
            self.stdscr.addstr(0, 0, msg[:curses.COLS])
        except curses.error:
            pass

        self.stdscr.refresh()
        return False