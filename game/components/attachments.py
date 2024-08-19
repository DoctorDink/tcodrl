from __future__ import annotations

from typing import Optional

from game.components.base_component import BaseComponent
from game.components.attachable import Socket, Attachable
from game.attachment_types import AttachmentType
import game.entity


class Attachments(BaseComponent):
    parent: game.entity.Actor

    def __init__(self, chassis: Optional[game.entity.Item] = None):
        self.chassis_socket = Socket(AttachmentType.CHASSIS, chassis)


    def attach(self, item: game.entity.Item) -> None:
        pass


