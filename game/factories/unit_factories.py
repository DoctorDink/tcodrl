from __future__ import annotations

import copy

from game.factories.limb_factories import *
from game.components.ai import HostileEnemy
from game.components.equipment import Equipment
from game.components.fighter import Fighter
from game.components.inventory import Inventory
from game.components.stats import Stats
from game.entity import Item, Actor

"""
Use this function to create new units, see below
The parts list is the list of parts that you want attached
Think of the necessary order of items like this:
If we were looking at our attachment inventory and we wanted to see this:

MY_CHASSIS
    MY_ARM
        MY_HAND
    MY_ARM
        MY_HAND
    MY_LEG
        MY_FOOT

we'd want a parts list that looked like this:

[MY_CHASSIS, MY_ARM, MY_HAND, MY_ARM, MY_HAND, MY_LEG, MY_FOOT]

it's essentially the flattened version of the above 'tree'
"""
def create_unit(parts: list[Item], char, color, name, ai, equipment, fighter, inventory) -> Actor:
    unit = Actor(char=char, color=color, name=name, ai_cls=ai, equipment=equipment, fighter=fighter, inventory=inventory)
    for part in parts:
        unit.attachments.attach(copy.deepcopy(part))
    return unit
    

player = create_unit(
    parts=[basic_chassis],
    char="@",
    color=(50, 130, 33),
    name="Player",
    ai=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(Stats(50, 10, 50, 50)),
    inventory=Inventory(capacity=26),
)

rust_ghoul = create_unit(
    parts=[rusted_chassis, rusted_arm, rusted_hand, rusted_leg, rusted_foot, rusted_leg, rusted_foot],
    char="g",
    color=(128, 42, 36),
    name="Rust Ghoul",
    ai=HostileEnemy,
    equipment=Equipment(),
    fighter=Fighter(Stats(10, 10, 10, 10)),
    inventory=Inventory(capacity=0),
)