from typing import Optional, Union, Callable

import game.actions
from game.components.base_component import BaseComponent
from game.components.effect import Effect

from game.entity import Entity
import game.exceptions
import game.stat_types

class EffectHandler(BaseComponent):
    parent: Entity

    def __init__(self) -> None:
        self.effects: list[Effect] = []

    def add_effect(self, new_effect: Effect, stacks = 1) -> None:
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


    def activate_all(self, action: game.actions.Action) -> dict[game.stat_types.StatType, int]:
        boosts: dict[game.stat_types.StatType, int] = {}
        to_remove = []
        for effect in self.effects:
            result = effect.activate(action)

            if isinstance(result, bool):
                if not result:
                    to_remove.append(effect)
            
            if isinstance(result, dict[game.stat_types.StatType, int]):
                for stat in result:
                    if stat in boosts:
                        boosts[stat] = boosts[stat] + result[stat]
                    else:
                        boosts[stat] = result[stat]
        
        for r_effect in to_remove:
            for i, effect in enumerate(self.effects):
                if effect == r_effect: 
                    self.remove_effect(i)

        return boosts


