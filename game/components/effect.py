from typing import Optional, Union, Callable

import game.components.base_component as base_component
import game.components.effect_handler as effect_handler
import game.actions 
import game.stat_types 


class Effect(base_component.BaseComponent):
    parent: effect_handler.EffectHandler

    def __init__(
            self,
            name,
            description,
            effect: Callable[[game.actions.Action], Union[dict[game.stat_types.StatType, int], bool]],
            stacks: int = 1,
            stackable: bool = False, 
            ): 
        
        self.name = name
        self.description = description
        self._effect = effect
        self.stacks = stacks
        self.stackable = stackable

    def activate(self, action) -> Union[dict[game.stat_types.StatType, int], bool]:
        return self._effect(action)