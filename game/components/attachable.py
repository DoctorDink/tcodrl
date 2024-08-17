
from __future__ import annotations

from typing import Optional

from game.components.base_component import BaseComponent
from game.attachment_types import AttachmentType
import game.entity


class Socket():
    
    def __init__(self, type: AttachmentType, attachment:Optional[Attachable]) -> None:
        self.type = type
        self.attachment = attachment
        

class Attachable(BaseComponent):
    parent: game.entity.Item

    def __init__(
            self,
            hp: int = 1,
            max_hp: int = 1,
            sockets: list[Socket] = []
            ) -> None:
        
        self.hp = hp
        self.max_hp = max_hp
        self.sockets = sockets
        