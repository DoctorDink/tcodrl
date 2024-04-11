from __future__ import annotations

from typing import Tuple

import tcod

import game.color
import game.engine
import game.game_map


def get_names_at_location(x: int, y: int, game_map: game.game_map.GameMap) -> str:
    if not game_map.in_bounds(x, y) or not game_map.visible[x, y]:
        return ""

    names = ", ".join(entity.name for entity in game_map.entities if entity.x == x and entity.y == y)

    return names.capitalize()


def render_bar(console: tcod.console.Console, 
    current_value: int, maximum_value: int, total_width: int, 
    name: str, xPos: int, yPos: int, 
    colorEmpty: game.color, colorFull: game.color, colorText: game.color) -> None:

    bar_width = int(float(current_value) / maximum_value * total_width)

    console.draw_rect(x=xPos, y=yPos, width=20, height=1, ch=1, bg=colorEmpty) #0, 45

    if bar_width > 0:
        console.draw_rect(x=xPos, y=yPos, width=bar_width, height=1, ch=1, bg=colorFull)

    console.print(x=xPos, y=yPos, string=f"{name}: {current_value}/{maximum_value}", fg=colorText)


def render_dungeon_level(console: tcod.console.Console, dungeon_level: int, location: Tuple[int, int]) -> None:
    """
    Render the level the player is currently on, at the given location.
    """
    x, y = location

    console.print(x=x, y=y, string=f"Dungeon level: {dungeon_level}")


def render_names_at_mouse_location(console: tcod.console.Console, x: int, y: int, engine: game.engine.Engine) -> None:
    mouse_x, mouse_y = engine.mouse_location

    names_at_mouse_location = get_names_at_location(x=mouse_x, y=mouse_y, game_map=engine.game_map)

    console.print(x=x, y=y, string=names_at_mouse_location)
