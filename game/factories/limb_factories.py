from typing import Optional, Union

from game.entity import Actor, Item
from game.actions import Action
from game.components.attachable import Attachable, Socket
from game.attachment_types import AttachmentType
from game.components.effect import Effect
from game.stat_types import StatType


basic_stat_callable = lambda bulk=0, shielding=0, processing=0, coordination=0: lambda action : {StatType.BULK: bulk, StatType.SHIELDING: shielding, StatType.PROCESSING: processing, StatType.COORDINATION: coordination}



basic_chassis_effect = Effect(
    name = "ATTACHMENT:Basic Chassis",
    description="",
    effect = basic_stat_callable(bulk=5, shielding=5),
    stacks = 1,
    stackable = True,
)

basic_chassis = Item(
    char="C",
    color=(100, 100, 100),
    name="Basic Chassis",
    attachable=Attachable(AttachmentType.CHASSIS, hp = 10, max_hp = 10, sockets = [Socket(AttachmentType.JOINT), Socket(AttachmentType.JOINT), Socket(AttachmentType.JOINT), Socket(AttachmentType.JOINT)], effects=[basic_chassis_effect]),
    count=1,
    stackable=False,
)



rusted_chassis_effect = Effect(
    name = "ATTACHMENT:Rusted Chassis",
    description="",
    effect = basic_stat_callable(bulk= 3, shielding= 3, coordination= -3, processing= -3),
    stacks = 1,
    stackable = True,
)

rusted_chassis = Item(
    char="C",
    color=(128, 42, 36),
    name="Rusted Chassis",
    attachable=Attachable(AttachmentType.CHASSIS, hp = 5, max_hp = 5, sockets = [Socket(AttachmentType.JOINT), Socket(AttachmentType.JOINT), Socket(AttachmentType.JOINT)], effects=[rusted_chassis_effect]),
    count=1,
    stackable=False,
)



rusted_leg_effect = Effect(
    name = "ATTACHMENT:Rusted Leg",
    description="",
    effect = basic_stat_callable(bulk= 2, shielding= 2, coordination= -2),
    stacks = 1,
    stackable = True,
)

rusted_leg = Item(
    char="L",
    color=(128, 42, 36),
    name="Rusted Leg",
    attachable=Attachable(AttachmentType.JOINT, hp = 5, max_hp = 5, sockets = [Socket(AttachmentType.APPENDAGE)], effects=[rusted_leg_effect]),
    count=1,
    stackable=False,
)

rusted_arm_effect = Effect(
    name = "ATTACHMENT:Rusted Arm",
    description="",
    effect = basic_stat_callable(bulk= 2, shielding= 2, coordination= -2),
    stacks = 1,
    stackable = True,
)

rusted_arm = Item(
    char="|",
    color=(128, 42, 36),
    name="Rusted Arm",
    attachable=Attachable(AttachmentType.JOINT, hp = 5, max_hp = 5, sockets = [Socket(AttachmentType.APPENDAGE)], effects=[rusted_arm_effect]),
    count=1,
    stackable=False,
)



rusted_hand_effect = Effect(
    name = "ATTACHMENT:Rusted Hand",
    description="",
    effect = basic_stat_callable(bulk= 1, shielding= 1, coordination= -1),
    stacks = 1,
    stackable = True,
)

rusted_hand = Item(
    char="W",
    color=(128, 42, 36),
    name="Rusted Hand",
    attachable=Attachable(AttachmentType.APPENDAGE, hp = 5, max_hp = 5, sockets = [], effects=[rusted_hand_effect]),
    count=1,
    stackable=False,
)



rusted_foot_effect = Effect(
    name = "ATTACHMENT:Rusted Foot",
    description="",
    effect = basic_stat_callable(bulk= 1, shielding= 1, coordination= -1),
    stacks = 1,
    stackable = True,
)

rusted_foot = Item(
    char="M",
    color=(128, 42, 36),
    name="Rusted Foot",
    attachable=Attachable(AttachmentType.APPENDAGE, hp = 5, max_hp = 5, sockets = [], effects=[rusted_foot_effect]),
    count=1,
    stackable=False,
)

 
 