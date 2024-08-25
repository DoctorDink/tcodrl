from __future__ import annotations

from typing import Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from game.entity import Actor

import game.color
import game.entity
import game.exceptions
import game.engine



class Action:
    def __init__(self, entity: Actor, cooldown: int = 100) -> None:
        super().__init__()
        self.entity = entity
        self.cooldown = cooldown

    @property
    def engine(self) -> game.engine.Engine:
        """Return the engine this action belongs to."""
        return self.entity.gamemap.engine

    def action_performed(self, cooldown: int):
        self.entity.cooldown = cooldown
        self.entity.effect_handler.activate_all(self)
        

    def perform(self) -> None:
        """Perform this action with the objects needed to determine its scope.

        `self.engine` is the scope this action is being performed in.

        `self.entity` is the object performing the action.

        This method must be overridden by Action subclasses.
        """

        raise NotImplementedError()


class PickupAction(Action):
    """Pickup an item and add it to the inventory, if there is room for it."""

    def __init__(self, entity: Actor, cooldown: int = 25):
        super().__init__(entity, cooldown)

    def perform(self) -> None:
        actor_location_x = self.entity.x
        actor_location_y = self.entity.y
        inventory = self.entity.inventory

        for item in self.engine.game_map.items:
            if actor_location_x == item.x and actor_location_y == item.y:
                if len(inventory.items) >= inventory.capacity:
                    raise game.exceptions.Impossible("Your inventory is full.")

                self.engine.game_map.entities.remove(item)
                item.parent = self.entity.inventory

                found = False

                for id in inventory.items:
                    if (id.name == item.name and item.stackable):
                        id.count += 1
                        found = True

                if(not found):
                    item.count = 1
                    inventory.items.append(item)

                self.engine.message_log.add_message(f"You picked up the {item.name}!")
                
                self.action_performed(self.cooldown)
                return

        raise game.exceptions.Impossible("There is nothing here to pick up.")


class ItemAction(Action):
    def __init__(self, entity: game.entity.Actor, item: game.entity.Item, target_xy: Optional[Tuple[int, int]] = None, cooldown: int = 25):
        super().__init__(entity)
        self.item = item
        if not target_xy:
            target_xy = entity.x, entity.y
        self.target_xy = target_xy

    @property
    def target_actor(self) -> Optional[game.entity.Actor]:
        """Return the actor at this actions destination."""
        return self.engine.game_map.get_actor_at_location(*self.target_xy)

    def perform(self) -> None:
        """Invoke the items ability, this action will be given to provide context."""
        if self.item.consumable:
            cooldown = self.item.consumable.activate(self)
            self.action_performed(cooldown)



class DropItem(ItemAction):
    def perform(self) -> None:
        if self.entity.equipment.item_is_equipped(self.item):
            self.entity.equipment.toggle_equip(self.item)
        self.entity.inventory.drop(self.item)
        self.action_performed(0)


class EquipAction(Action):
    def __init__(self, cooldown, entity: game.entity.Actor, item: game.entity.Item):
        super().__init__(entity, cooldown)

        self.item = item

    def perform(self) -> None:
        self.entity.equipment.toggle_equip(self.item)
        self.action_performed(self.cooldown)


class WaitAction(Action):
    def perform(self) -> None:
        self.action_performed(100)


class TakeStairsAction(Action):
    def __init__(self, entity: game.entity.Actor, cooldown: int = 100) -> None:
        super().__init__(entity, cooldown)

    def perform(self) -> None:
        """
        Take the stairs, if any exist at the entity's location.
        """
        if (self.entity.x, self.entity.y) == self.engine.game_map.downstairs_location:
            self.engine.game_world.generate_floor()
            self.engine.message_log.add_message("You ascend the staircase.", game.color.descend)
            self.action_performed(self.cooldown)
        else:
            raise game.exceptions.Impossible("There are no stairs here.")


class ActionWithDirection(Action):
    def __init__(self, cooldown, entity: game.entity.Actor, dx: int, dy: int):
        super().__init__(entity,cooldown)

        self.dx = dx
        self.dy = dy

    @property
    def dest_xy(self) -> Tuple[int, int]:
        """Returns this actions destination."""
        return self.entity.x + self.dx, self.entity.y + self.dy

    @property
    def blocking_entity(self) -> Optional[game.entity.Entity]:
        """Return the blocking entity at this actions destination.."""
        return self.engine.game_map.get_blocking_entity_at_location(*self.dest_xy)

    @property
    def target_actor(self) -> Optional[game.entity.Actor]:
        """Return the actor at this actions destination."""
        return self.engine.game_map.get_actor_at_location(*self.dest_xy)

    def perform(self) -> None:
        raise NotImplementedError()


class MeleeAction(ActionWithDirection):
    def perform(self) -> None:
        target = self.target_actor
        if not target:
            raise game.exceptions.Impossible("Nothing to attack.")

        damage = self.entity.fighter.stats.bulk // 5 - target.fighter.stats.shielding // 10

        attack_desc = f"{self.entity.name.capitalize()} attacks {target.name}"
        if self.entity is self.engine.player:
            attack_color = game.color.player_atk
        else:
            attack_color = game.color.enemy_atk

        if damage > 0:
            self.engine.message_log.add_message(f"{attack_desc} for {damage} hit points.", attack_color)
            target.fighter.hp -= damage
        else:
            self.engine.message_log.add_message(f"{attack_desc} but does no damage.", attack_color)
        
        self.action_performed(self.cooldown)


class Move(ActionWithDirection):
    def perform(self) -> None:
        dest_x, dest_y = self.dest_xy

        if not self.engine.game_map.in_bounds(dest_x, dest_y):
            # Destination is out of bounds.
            raise game.exceptions.Impossible("That way is blocked.")
        if not self.engine.game_map.tiles["walkable"][dest_x, dest_y]:
            # Destination is blocked by a tile.
            raise game.exceptions.Impossible("That way is blocked.")
        if self.engine.game_map.get_blocking_entity_at_location(dest_x, dest_y):
            # Destination is blocked by an entity.
            if self.entity.name == "Orc":
                self.entity.cooldown = 150 
            else:
                self.entity.cooldown = self.cooldown            
            raise game.exceptions.Impossible("That way is blocked.")

        self.entity.move(self.dx, self.dy)
        
        self.action_performed(self.cooldown)


class Bump(ActionWithDirection):
    def __init__(self, melee_cooldown: int, move_cooldown: int, entity: game.entity.Actor, dx: int, dy: int):
        super().__init__(0, entity, dx, dy)
        self.melee_cooldown = melee_cooldown
        self.move_cooldown = move_cooldown

    def perform(self) -> None:
        if self.target_actor:
            return MeleeAction(self.melee_cooldown, self.entity, self.dx, self.dy).perform()

        else:
            return Move(self.move_cooldown, self.entity, self.dx, self.dy).perform()
