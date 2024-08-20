from typing import Optional, Union

from game.entity import Actor, Item
from game.actions import Action
from game.components.attachable import Attachable, Socket
from game.attachment_types import AttachmentType
from game.components.effect import Effect
from game.stat_types import StatType


basic_stat_callable = lambda bulk, shielding, processing, coordination: lambda action : {StatType.BULK: bulk, StatType.SHIELDING: shielding, StatType.PROCESSING: processing, StatType.COORDINATION: coordination}

basic_chassis_effect = Effect(
    name = "ATTACHMENT:Basic Chassis",
    description="",
    effect = basic_stat_callable(5,5,5,5),
    stacks = 1,
    stackable = True,
)


basic_chassis = Item(
    char="H",
    color=(100, 100, 100),
    name="Basic Chassis",
    attachable=Attachable(AttachmentType.CHASSIS, hp = 10, max_hp = 10, sockets = [Socket(AttachmentType.JOINT), Socket(AttachmentType.JOINT), Socket(AttachmentType.JOINT), Socket(AttachmentType.JOINT)], effects=[basic_chassis_effect]),
    count=1,
    stackable=False,
)
 