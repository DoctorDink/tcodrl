from __future__ import annotations

from typing import List

import game.components.base_component as base_component
import game.entity


class Inventory(base_component.BaseComponent):
    parent: game.entity.Actor

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.items: List[game.entity.Item] = []

    def drop(self, item: game.entity.Item) -> None:
        """
        Removes an item from the inventory and restores it to the game map, at the player's current location.
        """

        item.count -= 1
        item.spawn(self.gamemap, self.parent.x, self.parent.y)

        if (item.count <= 0):
            self.items.remove(item)

        self.engine.message_log.add_message(f"You dropped the {item.name}.")
