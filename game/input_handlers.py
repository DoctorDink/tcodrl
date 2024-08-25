from __future__ import annotations

from typing import Callable, Optional, Tuple, Union, TYPE_CHECKING
import os

import tcod
import libtcodpy

import game.components

if TYPE_CHECKING:
    import game.actions


import game.color as color
import game.engine
import game.entity
import game.exceptions
import game.attachment_types
import game.components.attachments


MOVE_KEYS = {
    # Arrow keys.
    tcod.event.KeySym.UP: (0, -1),
    tcod.event.KeySym.DOWN: (0, 1),
    tcod.event.KeySym.LEFT: (-1, 0),
    tcod.event.KeySym.RIGHT: (1, 0),
    tcod.event.KeySym.HOME: (-1, -1),
    tcod.event.KeySym.END: (-1, 1),
    tcod.event.KeySym.PAGEUP: (1, -1),
    tcod.event.KeySym.PAGEDOWN: (1, 1),
    # Numpad keys.
    tcod.event.KeySym.KP_1: (-1, 1),
    tcod.event.KeySym.KP_2: (0, 1),
    tcod.event.KeySym.KP_3: (1, 1),
    tcod.event.KeySym.KP_4: (-1, 0),
    tcod.event.KeySym.KP_6: (1, 0),
    tcod.event.KeySym.KP_7: (-1, -1),
    tcod.event.KeySym.KP_8: (0, -1),
    tcod.event.KeySym.KP_9: (1, -1),
}

WAIT_KEYS = {
    tcod.event.KeySym.PERIOD,
    tcod.event.KeySym.KP_5,
    tcod.event.KeySym.CLEAR,
}

HEAL_KEYS = {
    tcod.event.KeySym.BACKQUOTE,
}

CONFIRM_KEYS = {
    tcod.event.KeySym.RETURN,
    tcod.event.KeySym.KP_ENTER,
}

ActionOrHandler = Union[game.actions.Action, "BaseEventHandler"]
"""An event handler return value which can trigger an action or switch active handlers.

If a handler is returned then it will become the active handler for future events.
If an action is returned it will be attempted and if it's valid then
MainGameEventHandler will become the active handler.
"""


class BaseEventHandler(tcod.event.EventDispatch[ActionOrHandler]):
    def handle_events(self, event: tcod.event.Event) -> BaseEventHandler:
        """Handle an event and return the next active event handler."""
        state = self.dispatch(event)
        if isinstance(state, BaseEventHandler):
            return state
        assert not isinstance(state, game.actions.Action), f"{self!r} can not handle actions."
        return self

    def on_render(self, console: tcod.console.Console) -> None:
        raise NotImplementedError()

    def ev_quit(self, event: tcod.event.Quit) -> Optional[game.actions.Action]:
        raise SystemExit()


class PopupMessage(BaseEventHandler):
    """Display a popup text window."""

    def __init__(self, parent_handler: BaseEventHandler, text: str):
        self.parent = parent_handler
        self.text = text

    def on_render(self, console: tcod.console.Console) -> None:
        """Render the parent and dim the result, then print the message on top."""
        self.parent.on_render(console)
        console.tiles_rgb["fg"] //= 8
        console.tiles_rgb["bg"] //= 8

        console.print(
            console.width // 2,
            console.height // 2,
            self.text,
            fg=game.color.white,
            bg=game.color.black,
            alignment=libtcodpy.CENTER,
        )

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[BaseEventHandler]:
        """Any key returns to the parent handler."""
        return self.parent


class EventHandler(BaseEventHandler):
    def __init__(self, engine: game.engine.Engine):
        self.engine = engine

    def handle_events(self, event: tcod.event.Event) -> BaseEventHandler:
        """Handle events for input handlers with an engine."""
        action_or_state = self.dispatch(event)
        if isinstance(action_or_state, BaseEventHandler):
            return action_or_state
        if self.handle_action(action_or_state):
            # A valid action was performed.
            if not self.engine.player.is_alive:
                # The player was killed sometime during or after the action.
                return GameOverEventHandler(self.engine)
            return MainGameEventHandler(self.engine)  # Return to the main handler. DEFAULT CASE
        return self

    def handle_action(self, action: Optional[game.actions.Action]) -> bool:
        """Handle actions returned from event methods.

        Returns True if the action will advance a turn.
        """
        if action is None:
            return False

        try:
            action.perform()
        except game.exceptions.Impossible as exc:
            self.engine.message_log.add_message(exc.args[0], game.color.impossible)
            return False  # Skip enemy turn on exceptions.

        self.engine.handle_enemy_turns()

        self.engine.update_fov()
        return True

    def ev_mousemotion(self, event: tcod.event.MouseMotion) -> None:
        if self.engine.game_map.in_bounds(event.tile.x, event.tile.y):
            self.engine.mouse_location = event.tile.x, event.tile.y

    def on_render(self, console: tcod.Console) -> None:
        self.engine.render(console)

class WaitHealEventHandler(EventHandler):
    """Handles user input for waiting to heal"""

    def __init__(self, engine: game.engine.Engine):
        self.engine = engine

    def wait_to_heal(self):
        while (self.engine.player.fighter.hp < self.engine.player.fighter.max_hp):
            if (self.engine.review_hostile_enemies()):
                self.engine.message_log.add_message("Sleep aborted, hostile enemies detected.", game.color.needs_target)
                return MainGameEventHandler(self.engine)
            self.engine.player.fighter.hp += 1
            self.engine.handle_enemy_turns()
        return MainGameEventHandler(self.engine)

        #console.print(x=x + 1, y=y + 1, string=f"Level: {self.engine.player.level.current_level}")

class AskUserEventHandler(EventHandler):
    """Handles user input for actions which require special input."""

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        """By default any key exits this input handler."""
        if event.sym in {  # Ignore modifier keys.
            tcod.event.KeySym.LSHIFT,
            tcod.event.KeySym.RSHIFT,
            tcod.event.KeySym.LCTRL,
            tcod.event.KeySym.RCTRL,
            tcod.event.KeySym.LALT,
            tcod.event.KeySym.RALT,
            tcod.event.KeySym.LGUI,
            tcod.event.KeySym.RGUI,
            tcod.event.KeySym.MODE,
        }:
            return None
        return self.on_exit()

    def ev_mousebuttondown(self, event: tcod.event.MouseButtonDown) -> Optional[ActionOrHandler]:
        """By default any mouse click exits this input handler."""
        return self.on_exit()

    def on_exit(self) -> Optional[ActionOrHandler]:
        """Called when the user is trying to exit or cancel an action.

        By default this returns to the main event handler.
        """
        return MainGameEventHandler(self.engine)


class CharacterScreenEventHandler(AskUserEventHandler):
    TITLE = "Character Information"

    def on_render(self, console: tcod.console.Console) -> None:
        super().on_render(console)

        if self.engine.player.x <= 30:
            x = 40
        else:
            x = 0

        y = 0

        width = len(self.TITLE) + 4

        console.draw_frame(
            x=x,
            y=y,
            width=width,
            height=7,
            title=self.TITLE,
            clear=True,
            fg=(255, 255, 255),
            bg=(0, 0, 0),
        )

        console.print(x=x + 1, y=y + 1, string=f"HP: {self.engine.player.fighter.hp} / {self.engine.player.fighter.max_hp}")

        console.print(x=x + 1, y=y + 2, string=f"Bulk: {self.engine.player.fighter.stats.bulk}")
        console.print(x=x + 1, y=y + 3, string=f"Shielding: {self.engine.player.fighter.stats.shielding}")
        console.print(x=x + 1, y=y + 4, string=f"Processing: {self.engine.player.fighter.stats.processing}")
        console.print(x=x + 1, y=y + 5, string=f"Coordination: {self.engine.player.fighter.stats.coordination}")

class AttachmentEventHandler(AskUserEventHandler):
    TITLE = "Socket Equipment Screen"

    def __init__(self, engine: game.engine.Engine):
        super().__init__(engine)
        self.selected_index = 0

    def on_render(self, console: tcod.console.Console) -> None:
        from game.components.attachable import Attachable, Socket

        """
        Render an attachment menu, which displays the attacments the player has equipped, and the letter to select them.
        """
        super().on_render(console)
        number_of_total_sockets = len(self.engine.player.attachments.get_sockets())

        height = 36

        width = 60

        console.draw_frame(
            x=3,
            y=3,
            width=width,
            height=height,
            clear=True,
            fg=color.white,
            bg=color.dark_brown,
        )

        console.print(1, 1, f" {self.TITLE} ", fg=(201, 113, 30), bg=(32, 20, 6)) #TODO: ADD THESE COLORS TO THE COLOR LIST

        if number_of_total_sockets > 0:
            previous_socket : Socket = None
            socket_depth = 0
            for i, socket in enumerate(self.engine.player.attachments.get_sockets()):
                #Find socket depth for indenting
                if previous_socket == None or previous_socket.parent == socket.parent:
                    pass
                elif socket.is_decendent_of(previous_socket):
                    socket_depth += 1
                else: 
                    socket_depth -= 1

                spacer = " " * socket_depth
                if socket_depth > 0:
                    spacer += "∟"

                if (socket.attachment == None):
                    type_string = ""
                    if socket.type == game.attachment_types.AttachmentType.CHASSIS:
                        type_string = "Empty Chassis Socket"
                    elif socket.type == game.attachment_types.AttachmentType.JOINT:
                        type_string = f"Empty Joint Socket"
                    elif socket.type == game.attachment_types.AttachmentType.APPENDAGE:
                        type_string = f"Empty Appendage Socket"
                    elif socket.type == game.attachment_types.AttachmentType.WEAPON:
                        type_string = f"Empty Weapon Socket"
                    socket_string = f"{spacer}{type_string}"

                else:
                    socket_string = f"{spacer}{socket.attachment.name}"

                if i == self.selected_index:
                    socket_string += " <-"

                #TODO: un-magic-numberify this 
                previous_socket = socket
                console.print(1 + 3, 3 + i + 1, socket_string)
                

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        key = event.sym
        
        socket_count = len(self.engine.player.attachments.get_sockets())
        
        if key == tcod.event.KeySym.KP_2:
            self.selected_index += 1
            if self.selected_index > socket_count - 1:
                self.selected_index = socket_count - 1
            return 
        elif key == tcod.event.KeySym.KP_8:
            self.selected_index -= 1
            if self.selected_index < 0:
                self.selected_index = 0
            return 
        elif key in {
            tcod.event.KeySym.SPACE,
            tcod.event.KeySym.KP_ENTER,
            tcod.event.KeySym.RETURN
        }:
            return self.on_item_selected(self.engine.player.attachments.get_sockets()[self.selected_index])
        
        return super().ev_keydown(event)
    
    from game.components.attachable import Attachable, Socket
    def on_item_selected(self, socket: Socket) -> Optional[ActionOrHandler]:
        if(not socket.attachment):
            self.engine.message_log.add_message("Invalid entry.", game.color.invalid)
            return AttachmentSelectionEventHandler(self.engine, self, self.selected_index)
        
        self.engine.player.inventory.items.append(socket.attachment)
        socket.detach()
        return
    
class AttachmentSelectionEventHandler(AskUserEventHandler):

    MIN_WINDOW_HEIGHT = 2
    MIN_SIZE_HEIGHT = 23
    WINDOW_WIDTH = 40
    TITLE = "Choose an attachment"

    def __init__(self, engine: game.engine.Engine, parent: BaseEventHandler, socket_index: int):
        super().__init__(engine)
        self.parent = parent
        self.socket_index = socket_index
        self.selected_index = 0

    def on_render(self, console: tcod.console.Console) -> None:
        from game.components.attachable import Attachable, Socket

        super().on_render(console)

        self.parent.on_render(console)
        console.rgb["fg"] //= 2
        console.rgb["bg"] //= 2

        player = self.engine.player

        all_sockets = player.attachments.get_sockets()

        available_attachments = list(filter(lambda item : item.attachable != None and item.attachable.type == all_sockets[self.socket_index].type, player.inventory.items))

        height = self.MIN_WINDOW_HEIGHT + max(1, len(available_attachments))

        

        top = console.height // 2 - height // 2

        left = console.width // 2 - self.WINDOW_WIDTH // 2

        console.draw_frame(
            x=left,
            y=top,
            width=self.WINDOW_WIDTH,
            height=height,
            clear=True,
            fg=color.white,
            bg=color.dark_brown,
        )

        console.print(left, top - 1, f" {self.TITLE} ", fg=color.pale_sand, bg=tuple(ti//2 for ti in color.dark_brown))

        if len(available_attachments) > 0:
            for i, attachment in enumerate(available_attachments):

                attachment_string = attachment.name

                if i == self.selected_index: 
                    attachment_string += " <-"

                console.print(left + 1, top + 1 + i, attachment_string, color.white, color.dark_brown)
        else:
            console.print(left + 1, top + 1, "No valid attachments", color.white, color.dark_brown)
                

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        player = self.engine.player
        key = event.sym
        all_sockets = player.attachments.get_sockets()
        available_attachments = list(filter(lambda item : item.attachable != None and item.attachable.type == all_sockets[self.socket_index].type, player.inventory.items))
        
        if key == tcod.event.KeySym.KP_2:
            self.selected_index += 1
            if self.selected_index > len(available_attachments) - 1:
                self.selected_index = len(available_attachments) - 1
            return 
        elif key == tcod.event.KeySym.KP_8:
            self.selected_index -= 1
            if self.selected_index < 0:
                self.selected_index = 0
            return
        elif key in {
            tcod.event.KeySym.SPACE,
            tcod.event.KeySym.KP_ENTER,
            tcod.event.KeySym.RETURN
        }:
            if len(available_attachments) > 0:
                return self.on_item_selected(available_attachments[self.selected_index])
            else:
                return self.parent
        
        elif key == tcod.event.KeySym.ESCAPE:
            return self.parent
    
    def on_item_selected(self, item: game.entity.Item) -> Optional[ActionOrHandler]:
        self.engine.player.inventory.items.remove(item)
        self.engine.player.attachments.attach(item, self.socket_index)
        return self.parent


class AreYouSureEventHandler(AskUserEventHandler):

    WINDOW_HEIGHT = 5
    WINDOW_WIDTH = 15
    TITLE = "Are you sure?"

    def __init__(self, engine: game.engine.Engine, parent: BaseEventHandler, text: str):
        super().__init__(engine)
        self.parent = parent
        self.text = text
        self.selected_yes = False

    def on_render(self, console: tcod.console.Console) -> None:
        from game.components.attachable import Attachable, Socket

        super().on_render(console)


        console.draw_frame(
            x=console.width // 2 - self.WINDOW_WIDTH // 2,
            y=console.height // 2 - self.WINDOW_HEIGHT // 2,
            width=self.WINDOW_WIDTH,
            height=self.WINDOW_HEIGHT,
            clear=True,
            fg=color.white,
            bg=color.dark_brown,
        )

        top = console.height // 2 - self.WINDOW_HEIGHT // 2

        console.print(30, top - 1, f" {self.TITLE} ", fg=color.pale_sand, bg=color.dark_brown)
                

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[game.entity.Item]:
        player = self.engine.player
        key = event.sym
        if key == tcod.event.KeySym.y:
            return
    
    def on_item_selected(self, item: game.entity.Item) -> Optional[game.entity.Item]:
        self.engine.player.inventory.items.remove(item)
        return item
    


class InventoryEventHandler(AskUserEventHandler):
    """This handler lets the user select an item.

    What happens then depends on the subclass.
    """

    TITLE = "<missing title>"

    def on_render(self, console: tcod.console.Console) -> None:
        """Render an inventory menu, which displays the items in the inventory, and the letter to select them.
        Will move to a different position based on where the player is located, so the player can always see where
        they are.
        """
        super().on_render(console)
        number_of_items_in_inventory = len(self.engine.player.inventory.items)

        height = 36

        width = 60

        console.draw_frame(
            x=3,
            y=3,
            width=width,
            height=height,
            clear=True,
            fg=(255, 255, 255), #TODO: MORE COLORS TO ADD TO THE COLOR FILE
            bg=(32, 20, 6),
        )
        console.print(1, 1, f" {self.TITLE} ", fg=(201, 113, 30), bg=(32, 20, 6)) #TODO: MORE COLORS TO ADD TO THE COLOR FILE

        if number_of_items_in_inventory > 0:
            for i, item in enumerate(self.engine.player.inventory.items):
                item_key = chr(ord("a") + i)

                is_equipped = self.engine.player.equipment.item_is_equipped(item)
                
                item_string = f"({item_key}) {item.name} x {item.count}"

                if is_equipped:
                    item_string = f"{item_string} (E)"

                console.print(1 + 3, 3 + i + 1, item_string)
        else:
            console.print(1 + 1, 1 + 1, "(Empty)")

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        player = self.engine.player
        key = event.sym
        index = key - tcod.event.KeySym.a

        if 0 <= index <= 26:
            try:
                selected_item = player.inventory.items[index]
            except IndexError:
                self.engine.message_log.add_message("Invalid entry.", game.color.invalid)
                return None
            return self.on_item_selected(selected_item)
        return super().ev_keydown(event)

    def on_item_selected(self, item: game.entity.Item) -> Optional[ActionOrHandler]:
        """Called when the user selects a valid item."""
        raise NotImplementedError()


class InventoryActivateHandler(InventoryEventHandler):
    """Handle using an inventory item."""

    TITLE = "Select an item to use"

    def on_item_selected(self, item: game.entity.Item) -> Optional[ActionOrHandler]:
        if item.consumable:
            # Return the action for the selected item.
            return item.consumable.get_action(self.engine.player)
        elif item.equippable:
            return game.actions.EquipAction(100, self.engine.player, item)
        elif item.attachable:
            self.engine.player.attachments.attach(item)
            self.engine.player.inventory.items.remove(item)
            return
        else:
            return None


class InventoryDropHandler(InventoryEventHandler):
    """Handle dropping an inventory item."""

    TITLE = "Select an item to drop"

    def on_item_selected(self, item: game.entity.Item) -> Optional[ActionOrHandler]:
        """Drop this item."""
        return game.actions.DropItem(self.engine.player, item)


class SelectIndexHandler(AskUserEventHandler):
    """Handles asking the user for an index on the map."""

    def __init__(self, engine: game.engine.Engine):
        """Sets the cursor to the player when this handler is constructed."""
        super().__init__(engine)
        player = self.engine.player
        engine.mouse_location = player.x, player.y

    def on_render(self, console: tcod.console.Console) -> None:
        """Highlight the tile under the cursor."""
        super().on_render(console)
        x, y = self.engine.mouse_location
        console.tiles_rgb["bg"][x, y] = game.color.white
        console.tiles_rgb["fg"][x, y] = game.color.black

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        """Check for key movement or confirmation keys."""
        key = event.sym
        if key in MOVE_KEYS:
            modifier = 1  # Holding modifier keys will speed up key movement.
            if event.mod & (tcod.event.KMOD_LSHIFT | tcod.event.KMOD_RSHIFT):
                modifier *= 5
            if event.mod & (tcod.event.KMOD_LCTRL | tcod.event.KMOD_RCTRL):
                modifier *= 10
            if event.mod & (tcod.event.KMOD_LALT | tcod.event.KMOD_RALT):
                modifier *= 20

            x, y = self.engine.mouse_location
            dx, dy = MOVE_KEYS[key]
            x += dx * modifier
            y += dy * modifier
            # Clamp the cursor index to the map size.
            x = max(0, min(x, self.engine.game_map.width - 1))
            y = max(0, min(y, self.engine.game_map.height - 1))
            self.engine.mouse_location = x, y
            return None
        elif key in CONFIRM_KEYS:
            return self.on_index_selected(*self.engine.mouse_location)
        return super().ev_keydown(event)

    def ev_mousebuttondown(self, event: tcod.event.MouseButtonDown) -> Optional[ActionOrHandler]:
        """Left click confirms a selection."""
        if self.engine.game_map.in_bounds(*event.tile):
            if event.button == 1:
                return self.on_index_selected(*event.tile)
        return super().ev_mousebuttondown(event)

    def on_index_selected(self, x: int, y: int) -> Optional[ActionOrHandler]:
        """Called when an index is selected."""
        raise NotImplementedError()


class LookHandler(SelectIndexHandler):
    """Lets the player look around using the keyboard."""

    def on_index_selected(self, x: int, y: int) -> MainGameEventHandler:
        """Return to main handler."""
        return MainGameEventHandler(self.engine)


class SingleRangedAttackHandler(SelectIndexHandler):
    """Handles targeting a single enemy. Only the enemy selected will be affected."""

    def __init__(
        self, engine: game.engine.Engine, callback: Callable[[Tuple[int, int]], Optional[game.actions.Action]]
    ):
        super().__init__(engine)

        self.callback = callback

    def on_index_selected(self, x: int, y: int) -> Optional[game.actions.Action]:
        return self.callback((x, y))


class AreaRangedAttackHandler(SelectIndexHandler):
    """Handles targeting an area within a given radius. Any entity within the area will be affected."""

    def __init__(
        self,
        engine: game.engine.Engine,
        radius: int,
        callback: Callable[[Tuple[int, int]], Optional[game.actions.Action]],
    ):
        super().__init__(engine)

        self.radius = radius
        self.callback = callback

    def on_render(self, console: tcod.console.Console) -> None:
        """Highlight the tile under the cursor."""
        super().on_render(console)

        x, y = self.engine.mouse_location

        # Draw a rectangle around the targeted area, so the player can see the affected tiles.
        console.draw_frame(
            x=x - self.radius - 1,
            y=y - self.radius - 1,
            width=self.radius ** 2,
            height=self.radius ** 2,
            fg=game.color.red,
            clear=False,
        )

    def on_index_selected(self, x: int, y: int) -> Optional[game.actions.Action]:
        return self.callback((x, y))


class MainGameEventHandler(EventHandler):
    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        action: Optional[game.actions.Action] = None

        key = event.sym
        modifier = event.mod

        player = self.engine.player

        if key == tcod.event.KeySym.COMMA and modifier & (tcod.event.KMOD_LSHIFT | tcod.event.KMOD_RSHIFT):
            return game.actions.TakeStairsAction(player)

        if key in MOVE_KEYS:
            dx, dy = MOVE_KEYS[key]
            action = game.actions.Bump(100, 100, player, dx, dy)
        elif key in WAIT_KEYS:
            action = game.actions.WaitAction(player)
        elif key in HEAL_KEYS:
            return WaitHealEventHandler(self.engine).wait_to_heal()

        elif key == tcod.event.KeySym.ESCAPE:
            raise SystemExit()
        elif key == tcod.event.KeySym.v:
            return HistoryViewer(self.engine)
        elif key == tcod.event.KeySym.e:
            return AttachmentEventHandler(self.engine)
        elif key == tcod.event.KeySym.g:
            action = game.actions.PickupAction(player)

        elif key == tcod.event.KeySym.TAB:
            return InventoryActivateHandler(self.engine)
        elif key == tcod.event.KeySym.d:
            return InventoryDropHandler(self.engine)
        elif key == tcod.event.KeySym.x:
            return LookHandler(self.engine)

        # No valid key was pressed
        return action
        '''
        elif key == tcod.event.KeySym.c:
            return CharacterScreenEventHandler(self.engine)
        '''
        


class GameOverEventHandler(EventHandler):
    def on_quit(self) -> None:
        """Handle exiting out of a finished game."""
        if os.path.exists("savegame.sav"):
            os.remove("savegame.sav")  # Deletes the active save file.
        raise game.exceptions.QuitWithoutSaving()  # Avoid saving a finished game.

    def ev_quit(self, event: tcod.event.Quit) -> None:
        self.on_quit()

    def ev_keydown(self, event: tcod.event.KeyDown) -> None:
        if event.sym == tcod.event.KeySym.ESCAPE:
            self.on_quit()


CURSOR_Y_KEYS = {
    tcod.event.KeySym.UP: -1,
    tcod.event.KeySym.DOWN: 1,
    tcod.event.KeySym.PAGEUP: -10,
    tcod.event.KeySym.PAGEDOWN: 10,
}


class HistoryViewer(EventHandler):
    """Print the history on a larger window which can be navigated."""

    def __init__(self, engine: game.engine.Engine):
        super().__init__(engine)
        self.log_length = len(engine.message_log.messages)
        self.cursor = self.log_length - 1

    def on_render(self, console: tcod.console.Console) -> None:
        super().on_render(console)  # Draw the main state as the background.

        log_console = tcod.console.Console(console.width - 6, console.height - 6)

        # Draw a frame with a custom banner title.
        log_console.draw_frame(0, 0, log_console.width, log_console.height)
        log_console.print_box(0, 0, log_console.width, 1, "┤Message history├", alignment=tcod.CENTER)

        # Render the message log using the cursor parameter.
        self.engine.message_log.render_messages(
            log_console,
            1,
            1,
            log_console.width - 2,
            log_console.height - 2,
            self.engine.message_log.messages[: self.cursor + 1],
        )
        log_console.blit(console, 3, 3)

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[MainGameEventHandler]:
        # Fancy conditional movement to make it feel right.
        if event.sym in CURSOR_Y_KEYS:
            adjust = CURSOR_Y_KEYS[event.sym]
            if adjust < 0 and self.cursor == 0:
                # Only move from the top to the bottom when you're on the edge.
                self.cursor = self.log_length - 1
            elif adjust > 0 and self.cursor == self.log_length - 1:
                # Same with bottom to top movement.
                self.cursor = 0
            else:
                # Otherwise move while staying clamped to the bounds of the history log.
                self.cursor = max(0, min(self.cursor + adjust, self.log_length - 1))
        elif event.sym == tcod.event.KeySym.HOME:
            self.cursor = 0  # Move directly to the top message.
        elif event.sym == tcod.event.KeySym.END:
            self.cursor = self.log_length - 1  # Move directly to the last message.
        else:  # Any other key moves back to the main game state.
            return MainGameEventHandler(self.engine)
        return None



'''
class LevelUpEventHandler(AskUserEventHandler):
    TITLE = "Level Up"

    def on_render(self, console: tcod.console.Console) -> None:
        super().on_render(console)

        if self.engine.player.x <= 30:
            x = 40
        else:
            x = 0

        console.draw_frame(
            x=x,
            y=0,
            width=35,
            height=8,
            title=self.TITLE,
            clear=True,
            fg=(255, 255, 255),
            bg=(0, 0, 0),
        )

        console.print(x=x + 1, y=1, string="Congratulations! You level up!")
        console.print(x=x + 1, y=2, string="Select an attribute to increase.")

        console.print(
            x=x + 1,
            y=4,
            string=f"a) Constitution (+20 HP, from {self.engine.player.fighter.max_hp})",
        )
        console.print(
            x=x + 1,
            y=5,
            string=f"b) Strength (+1 attack, from {self.engine.player.fighter.power})",
        )
        console.print(
            x=x + 1,
            y=6,
            string=f"c) Agility (+1 defense, from {self.engine.player.fighter.defense})",
        )

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        player = self.engine.player
        key = event.sym
        index = key - tcod.event.KeySym.a

        if 0 <= index <= 2:
            if index == 0:
                player.stats.increase_max_hp()
            elif index == 1:
                player.stats.increase_power()
            else:
                player.stats.increase_defense()
        else:
            self.engine.message_log.add_message("Invalid entry.", game.color.invalid)

            return None

        return super().ev_keydown(event)

    def ev_mousebuttondown(self, event: tcod.event.MouseButtonDown) -> Optional[ActionOrHandler]:
        """
        Don't allow the player to click to exit the menu, like normal.
        """
        return None
'''