from typing import Optional, Union

from game.color import *
from game.entity import Actor, Item
from game.actions import Action
from game.components.attachable import Attachable, Socket
from game.attachment_types import AttachmentType
from game.components.effect import Effect
from game.stat_types import StatType


basic_stat_callable = lambda bulk=0, shielding=0, processing=0, coordination=0: lambda action : {StatType.BULK: bulk, StatType.SHIELDING: shielding, StatType.PROCESSING: processing, StatType.COORDINATION: coordination}



rusted_chassis_effect = Effect(
    name = "ATTACHMENT:Rusted Chassis",
    description="",
    effect = basic_stat_callable(bulk= 3, shielding= 3, coordination= -3, processing= -3),
    stacks = 1,
    stackable = True,
)

rusted_chassis = Item(
    char="C",
    color=red_brown,
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
    color=red_brown,
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
    color=red_brown,
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
    color=red_brown,
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
    color=red_brown,
    name="Rusted Foot",
    attachable=Attachable(AttachmentType.APPENDAGE, hp = 5, max_hp = 5, sockets = [], effects=[rusted_foot_effect]),
    count=1,
    stackable=False,
)


#########################################################################################################

basic_chassis_effect = Effect(
    name = "ATTACHMENT:Basic Chassis",
    description="",
    effect = basic_stat_callable(bulk=5, shielding=5),
    stacks = 1,
    stackable = True,
)

basic_chassis = Item(
    char="C",
    color=light_gray,
    name="Basic Chassis",
    attachable=Attachable(AttachmentType.CHASSIS, hp = 10, max_hp = 10, sockets = [Socket(AttachmentType.JOINT), Socket(AttachmentType.JOINT), Socket(AttachmentType.JOINT), Socket(AttachmentType.JOINT)], effects=[basic_chassis_effect]),
    count=1,
    stackable=False,
)


basic_leg_effect = Effect(
    name = "ATTACHMENT:Basic Leg",
    description="",
    effect = basic_stat_callable(bulk= 4, shielding= 4),
    stacks = 1,
    stackable = True,
)

basic_leg = Item(
    char="L",
    color=light_gray,
    name="Basic Leg",
    attachable=Attachable(AttachmentType.JOINT, hp = 10, max_hp = 10, sockets = [Socket(AttachmentType.APPENDAGE)], effects=[basic_leg_effect]),
    count=1,
    stackable=False,
)

basic_arm_effect = Effect(
    name = "ATTACHMENT:Basic Arm",
    description="",
    effect = basic_stat_callable(bulk= 4, shielding= 4),
    stacks = 1,
    stackable = True,
)

basic_arm = Item(
    char="|",
    color=light_gray,
    name="Basic Arm",
    attachable=Attachable(AttachmentType.JOINT, hp =10, max_hp = 10, sockets = [Socket(AttachmentType.APPENDAGE)], effects=[basic_arm_effect]),
    count=1,
    stackable=False,
)


basic_hand_effect = Effect(
    name = "ATTACHMENT:Basic Hand",
    description="",
    effect = basic_stat_callable(bulk= 2, shielding= 2),
    stacks = 1,
    stackable = True,
)

basic_hand = Item(
    char="W",
    color=light_gray,
    name="Basic Hand",
    attachable=Attachable(AttachmentType.APPENDAGE, hp = 10, max_hp = 10, sockets = [], effects=[basic_hand_effect]),
    count=1,
    stackable=False,
)

basic_foot_effect = Effect(
    name = "ATTACHMENT:Basic Foot",
    description="",
    effect = basic_stat_callable(bulk= 2, shielding= 2),
    stacks = 1,
    stackable = True,
)

basic_foot = Item(
    char="M",
    color=light_gray,
    name="Basic Foot",
    attachable=Attachable(AttachmentType.APPENDAGE, hp = 10, max_hp = 10, sockets = [], effects=[basic_foot_effect]),
    count=1,
    stackable=False,
)


#########################################################################################################

golden_chassis_effect = Effect(
    name = "ATTACHMENT:Golden Chassis",
    description="",
    effect = basic_stat_callable(bulk=10, shielding=10),
    stacks = 1,
    stackable = True,
)
golden_chassis = Item(
    char="C",
    color=yellow,
    name="Golden Chassis",
    attachable=Attachable(AttachmentType.CHASSIS, hp = 20, max_hp = 20, sockets = [Socket(AttachmentType.JOINT), Socket(AttachmentType.JOINT), Socket(AttachmentType.JOINT), Socket(AttachmentType.JOINT)], effects=[golden_chassis_effect]),
    count=1,
    stackable=False,
)


golden_leg_effect = Effect(
    name = "ATTACHMENT:Golden Leg",
    description="",
    effect = basic_stat_callable(bulk= 8, shielding= 8),
    stacks = 1,
    stackable = True,
)

golden_leg = Item(
    char="L",
    color=yellow,
    name="Golden Leg",
    attachable=Attachable(AttachmentType.JOINT, hp = 20, max_hp = 20, sockets = [Socket(AttachmentType.APPENDAGE)], effects=[golden_leg_effect]),
    count=1,
    stackable=False,
)

golden_arm_effect = Effect(
    name = "ATTACHMENT:Golden Arm",
    description="",
    effect = basic_stat_callable(bulk= 8, shielding= 8),
    stacks = 1,
    stackable = True,
)

golden_arm = Item(
    char="|",
    color=yellow,
    name="Golden Arm",
    attachable=Attachable(AttachmentType.JOINT, hp =20, max_hp = 20, sockets = [Socket(AttachmentType.APPENDAGE)], effects=[golden_arm_effect]),
    count=1,
    stackable=False,
)


golden_hand_effect = Effect(
    name = "ATTACHMENT:Golden Hand",
    description="",
    effect = basic_stat_callable(bulk= 4, shielding= 4),
    stacks = 1,
    stackable = True,
)

golden_hand = Item(
    char="W",
    color=yellow,
    name="Golden Hand",
    attachable=Attachable(AttachmentType.APPENDAGE, hp = 20, max_hp = 20, sockets = [], effects=[golden_hand_effect]),
    count=1,
    stackable=False,
)

golden_foot_effect = Effect(
    name = "ATTACHMENT:Golden Foot",
    description="",
    effect = basic_stat_callable(bulk= 4, shielding= 4),
    stacks = 1,
    stackable = True,
)

golden_foot = Item(
    char="M",
    color=yellow,
    name="Golden Foot",
    attachable=Attachable(AttachmentType.APPENDAGE, hp = 20, max_hp = 20, sockets = [], effects=[golden_foot_effect]),
    count=1,
    stackable=False,
)


 