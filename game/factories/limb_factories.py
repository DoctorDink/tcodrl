from game.entity import Actor, Item
from game.components.attachable import Attachable, Socket
from game.attachment_types import AttachmentType
from game.components.effect import Effect
from game.stat_types import StatType


basic_chassis_effect = Effect(
    name = "ATTACHMENT:Basic Chassis",
    description="",
    effect = lambda action: {StatType.BULK: 5, StatType.SHIELDING: 5},
    stacks = 1,
    stackable = True,
)


basic_chassis = Item(
    char="H",
    color=(100, 100, 100),
    name="Basic Chassis",
    attachable=Attachable(AttachmentType.CHASSIS, hp = 10, max_hp = 10, sockets = [Socket(AttachmentType.JOINT), Socket(AttachmentType.JOINT), Socket(AttachmentType.JOINT), Socket(AttachmentType.JOINT)], effects=basic_chassis_effect),
    count=1,
    stackable=False,
)
