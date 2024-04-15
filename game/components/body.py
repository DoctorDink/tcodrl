from __future__ import annotations

from enum import Enum

from game.components.base_component import BaseComponent
import game.color
import game.entity
import game.input_handlers
import game.render_order

class BodyType(Enum):
    FLESH = 1
    METAL = 2
    GEL = 3
    FLAME = 4
    WATER = 5
    STONE = 6
    SHADE = 7

class ArmorType(Enum):
    HELM = 1
    TORSO = 2
    BACK = 3
    ARMS = 4
    LEGS = 5
    DIGITS = 6

class BodyPart(BaseComponent):
    parent: game.entity.Actor    
    def __init__(self, hp: int, maxHp: int, capacity: int, focus: int,
                 bodyType: BodyType, 
                 canWield: bool, canMove: bool, canSense: bool,
                 isVital: bool) -> None:
        self.hp = hp
        self.maxHp = maxHp
        self.focus = focus
        self.capacity = capacity
        self.bodyType = bodyType
        self.canWield = canWield
        self.canMove = canMove
        self.canSense = canSense
        self.isVital = isVital

class HumanoidArm(BodyPart):
    def __init__(self) -> None:
        super().__init__(5, 5, 5, 5, BodyType.FLESH, 1, 0, 0, 0)


class Body(BaseComponent):
    parent: game.entity.Actor

    def __init__(self, *args : BodyPart):
        totalHp = 0
        totalMaxHp = 0
        totalCapacity = 0
        totalFocus = 0

        for arg in args:
            totalHp += arg.hp
            totalMaxHp += arg.maxHp
            totalCapacity += arg.capacity
            totalFocus += arg.focus
        
        self.hp = totalHp
        self.max_hp = totalMaxHp
        self.capacity = totalCapacity
        self.focus = totalFocus

        
