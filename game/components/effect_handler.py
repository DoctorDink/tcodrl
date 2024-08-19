from __future__ import annotations

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from game.entity import Entity

import game.actions
import game.exceptions
import game.stat_types
import game.components.effect as effect
import game.components.base_component as base_component

class EffectHandler(base_component.BaseComponent):
    parent: Entity

    def __init__(self) -> None:
        self.effects: list[effect.Effect] = []
        self.current_stat_changes = {}

    def add_effect(self, new_effect: effect.Effect, stacks = 1) -> None:
        for effect in self.effects:
            if effect.name == new_effect.name:
                if effect.stackable:
                    effect.stacks += stacks
                    return
                else:
                    raise game.exceptions.Impossible(f"{self.parent.name} already has effect {new_effect.name}!")
        
        self.effects.append(new_effect)
        

    def remove_effect(self, effect_index, stacks: Optional[int] = None) -> None:
        if not stacks:
            self.effects.pop(effect_index)
        else:
            if self.effects[effect_index].stacks < stacks:
                self.effects.pop(effect_index)
            else:
                self.effects[effect_index].stacks -= stacks


    def activate_all(self, action: Optional[game.actions.Action] = None) -> None:
        stat_changes: dict[game.stat_types.StatType, int] = {}
        to_remove = []
        for effect in self.effects:
            result = effect.activate(action)

            if isinstance(result, bool):
                if not result:
                    to_remove.append(effect)
            
            if isinstance(result, dict):
                for stat in result:
                    if stat in stat_changes:
                        stat_changes[stat] = stat_changes[stat] + result[stat]
                    else:
                        stat_changes[stat] = result[stat]
        
        for r_effect in to_remove:
            for i, effect in enumerate(self.effects):
                if effect == r_effect: 
                    self.remove_effect(i)

        self.current_stat_changes = stat_changes


