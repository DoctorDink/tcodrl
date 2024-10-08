"""Handle the loading and initialization of game sessions."""
from __future__ import annotations

from typing import Optional
import copy
import lzma
import dill as pickle
import traceback

from PIL import Image  # type: ignore
import tcod
from tcod import libtcodpy

import game.input_handlers
import game.color
import game.engine
import game.factories.unit_factories
import game.game_map
import game.input_handlers
import game.procgen

# Load the background image.  Pillow returns an object convertable into a NumPy array.
background_image = Image.open("data/menu.jpg")


def new_game() -> game.engine.Engine:
    """Return a brand new game session as an Engine instance."""
    map_width = 65
    map_height = 40

    room_max_size = 8
    room_min_size = 6
    max_rooms = 30

    player = copy.deepcopy(game.factories.unit_factories.player)

    engine = game.engine.Engine(player=player)

    engine.game_world = game.game_map.GameWorld(
        engine=engine,
        max_rooms=max_rooms,
        room_min_size=room_min_size,
        room_max_size=room_max_size,
        map_width=map_width,
        map_height=map_height,
    )

    engine.game_world.generate_floor()
    engine.update_fov()

    engine.message_log.add_message("You enter the first floor of the pyramid, filled with the rusted husks of previous adventurers.", game.color.welcome_text)

    dagger = copy.deepcopy(game.factories.entity_factories.dagger)
    leather_armor = copy.deepcopy(game.factories.entity_factories.leather_armor)

    dagger.parent = player.inventory
    leather_armor.parent = player.inventory

    player.inventory.items.append(dagger)
    player.equipment.toggle_equip(dagger, add_message=False)

    player.inventory.items.append(leather_armor)
    player.equipment.toggle_equip(leather_armor, add_message=False)

    return engine


def load_game(filename: str) -> game.engine.Engine:
    """Load an Engine instance from a file."""
    with open(filename, "rb") as f:
        engine = pickle.loads(lzma.decompress(f.read()))
    assert isinstance(engine, game.engine.Engine)
    return engine


class MainMenu(game.input_handlers.BaseEventHandler):
    """Handle the main menu rendering and input."""
    def on_render(self, console: tcod.console.Console) -> None:
        """Render the main menu on a background image."""
        console.draw_semigraphics(background_image, 0, 0)

        console.print(
            console.width // 2,
            console.height // 2 - 4,
            "CYBERGORE",
            fg=game.color.menu_title,
            alignment=libtcodpy.CENTER,
        )
        console.print(
            console.width // 2,
            console.height - 2,
            "By Doctor Dink and Toggytokyo",
            fg=game.color.menu_title,
            alignment=libtcodpy.CENTER,
        )

        menu_width = 24
        for i, text in enumerate(["[N] Play a new game", "[C] Continue last game", "[Q] Quit"]):
            console.print(
                console.width // 2,
                console.height // 2 - 2 + i,
                text.ljust(menu_width),
                fg=game.color.menu_text,
                bg=game.color.black,
                alignment=libtcodpy.CENTER,
                bg_blend=libtcodpy.BKGND_ALPHA(64),
            )

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[game.input_handlers.BaseEventHandler]:
        if event.sym in (tcod.event.KeySym.q, tcod.event.KeySym.ESCAPE):
            raise SystemExit()
        elif event.sym == tcod.event.KeySym.c:
            try:
                return game.input_handlers.MainGameEventHandler(load_game("savegame.sav"))
            except FileNotFoundError:
                return game.input_handlers.PopupMessage(self, "No saved game to load.")
            except Exception as exc:
                traceback.print_exc()  # Print to stderr.
                return game.input_handlers.PopupMessage(self, f"Failed to load save:\n{exc}")
        elif event.sym == tcod.event.KeySym.n:
            return game.input_handlers.MainGameEventHandler(new_game())

        return None
