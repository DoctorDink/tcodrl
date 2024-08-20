from __future__ import annotations

from typing import Optional, Union, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    import game.components.effect_handler as effect_handler

import game.components.base_component as base_component
import game.actions 
import game.stat_types 


class Effect(base_component.BaseComponent):
    parent: effect_handler.EffectHandler

    def __init__(
            self,
            name,
            description,
            effect: Callable[[Optional[game.actions.Action]], Union[dict[game.stat_types.StatType, int], bool]],
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