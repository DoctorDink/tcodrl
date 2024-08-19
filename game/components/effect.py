from typing import Optional, Union, Callable

from game.components.base_component import BaseComponent
from game.actions import Action
from game.stat_types import StatType
from game.components.effect_handler import EffectHandler

class Effect(BaseComponent):
    parent: EffectHandler

    def __init__(
            self,
            name,
            description,
            effect: Callable[[Action], Union[dict[StatType, int], bool]],
            stacks: int = 1,
            stackable: bool = False, 
            ): 
        
        self.name = name
        self.description = description
        self._effect = effect
        self.stacks = stacks
        self.stackable = stackable

    def activate(self, action) -> Union[dict[StatType, int], bool]:
        return self._effect(action)