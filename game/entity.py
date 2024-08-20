from __future__ import annotations

from typing import Optional, Tuple, Type, TypeVar, Union, TYPE_CHECKING
import copy
import math

if TYPE_CHECKING:
    import game.components.ai
    
import game.components.attachments
import game.components.consumable
import game.components.equipment
import game.components.equippable
import game.components.fighter
import game.components.inventory
import game.components.stats
import game.components.attachable
import game.game_map
import game.render_order
import game.components.effect_handler

T = TypeVar("T", bound="Entity")


class Entity:
    """
    A generic object to represent players, enemies, items, etc.
    """

    parent: Union[game.game_map.GameMap, game.components.inventory.Inventory]

    def __init__(
        self,
        parent: Optional[game.game_map.GameMap] = None,
        x: int = 0,
        y: int = 0,
        char: str = "?",
        color: Tuple[int, int, int] = (255, 255, 255),
        name: str = "<Unnamed>",
        blocks_movement: bool = False,
        render_order: game.render_order.RenderOrder = game.render_order.RenderOrder.CORPSE,
    ):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks_movement = blocks_movement
        self.render_order = render_order
        if parent:
            # If parent isn't provided now then it will be set later.
            self.parent = parent
            parent.entities.add(self)

        self.effect_handler = game.components.effect_handler.EffectHandler()

    @property
    def gamemap(self) -> game.game_map.GameMap:
        return self.parent.gamemap

    def spawn(self: T, gamemap: game.game_map.GameMap, x: int, y: int) -> T:
        """Spawn a copy of this instance at the given location."""
        clone = copy.deepcopy(self)
        clone.x = x
        clone.y = y
        clone.parent = gamemap
        gamemap.entities.add(clone)
        return clone

    def place(self, x: int, y: int, gamemap: Optional[game.game_map.GameMap] = None) -> None:
        """Place this entitiy at a new location.  Handles moving across GameMaps."""
        self.x = x
        self.y = y
        if gamemap:
            if hasattr(self, "parent"):  # Possibly uninitialized.
                if self.parent is self.gamemap:
                    self.gamemap.entities.remove(self)
            self.parent = gamemap
            gamemap.entities.add(self)

    def distance(self, x: int, y: int) -> float:
        """
        Return the distance between the current entity and the given (x, y) coordinate.
        """
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

    def move(self, dx: int, dy: int) -> None:
        # Move the entity by a given amount
        self.x += dx
        self.y += dy


class Actor(Entity):
    def __init__(
        self,
        *,
        x: int = 0,
        y: int = 0,
        char: str = "?",
        color: Tuple[int, int, int] = (255, 255, 255),
        name: str = "<Unnamed>",
        ai_cls: Type[game.components.ai.BaseAI],
        cooldown: int = 0,
        equipment: game.components.equipment.Equipment,
        fighter: game.components.fighter.Fighter,
        inventory: game.components.inventory.Inventory,
    ):
        super().__init__(
            x=x,
            y=y,
            char=char,
            color=color,
            name=name,
            blocks_movement=True,
            render_order=game.render_order.RenderOrder.ACTOR,
        )

        self.ai: Optional[game.components.ai.BaseAI] = ai_cls(self)
        
        self.cooldown = cooldown

        self.equipment: game.components.equipment.Equipment = equipment
        self.equipment.parent = self

        self.fighter = fighter
        self.fighter.parent = self

        self.attachments: game.components.attachments.Attachments = game.components.attachments.Attachments()
        self.attachments.parent = self

        self.inventory = inventory
        self.inventory.parent = self

    @property
    def is_alive(self) -> bool:
        """Returns True as long as this actor can perform actions."""
        return bool(self.ai)


class Item(Entity):
    def __init__(
        self,
        *,
        x: int = 0,
        y: int = 0,
        char: str = "?",
        color: Tuple[int, int, int] = (255, 255, 255),
        name: str = "<Unnamed>",
        consumable: Optional[game.components.consumable.Consumable] = None,
        equippable: Optional[game.components.equippable.Equippable] = None,
        attachable: Optional[game.components.attachable.Attachable] = None,
        value: float = 0,
        weight: float = 0,
        count: int = 1,
        stackable: bool = True
    ):
        super().__init__(
            x=x,
            y=y,
            char=char,
            color=color,
            name=name,
            blocks_movement=False,
            render_order=game.render_order.RenderOrder.ITEM,
        )

        self.consumable = consumable

        if self.consumable:
            self.consumable.parent = self

        self.equippable = equippable

        if self.equippable:
            self.equippable.parent = self

        self.attachable = attachable
        
        if self.attachable:
            self.attachable.parent = self


        self.value = value
        self.weight = weight
        self.count = count

        self.stackable = stackable
