
from __future__ import annotations

from typing import Optional

import game.components.base_component as base_component
import game.attachment_types  as attachment_types
import game.components.effect as effect
import game.entity
import game.exceptions
import game.components.effect

class Socket(base_component.BaseComponent):
    parent: Attachable 

    def __init__(self, type: attachment_types.AttachmentType, attachment: Optional[game.entity.Item] = None) -> None:
        self.type = type
        self.attachment = attachment

    def attach(self, attachment: game.entity.Item):
        if not attachment.attachable:
            raise game.exceptions.Impossible(f"{attachment.name} is not attachable!")
        
        elif attachment.attachable.type != self.type:
            raise game.exceptions.Impossible(f"{attachment.name} is not attachable in this socket!")

        elif self.attachment:
            raise game.exceptions.Impossible(f"{self.attachment.name} is already attached in this spot!")
        
        else:
            self.attachment = attachment

    def detach(self) -> Optional[game.entity.Item]:
        attachment_temp = self.attachment
        self.attachment = None
        return attachment_temp
    
    def get_all_effects(self, others = []) -> list[game.components.effect.Effect]:
        if not self.attachment:
            return others
        
        all_effects =  others + self.attachment.attachable.effects
        for socket in self.attachment.attachable.sockets:
            all_effects = socket.get_all_effects(all_effects)

        return all_effects


class Attachable(game.components.base_component.BaseComponent):
    parent: game.entity.Item

    def __init__(
            self,
            type: attachment_types.AttachmentType,
            hp: int = 1,
            max_hp: int = 1,
            sockets: list[Socket] = [],
            effects: list[effect.Effect] = []
            ) -> None:

        self.type = type
        self.hp = hp
        self.max_hp = max_hp
        self.sockets = sockets
        for socket in self.sockets:
            socket.parent = self

        self.effects = effects


    def attach(self, socket_index: int, attachment: game.entity.Item) -> None:
        if socket_index >= len(self.sockets) or socket_index < 0:
            raise game.exceptions.Impossible("That is not a valid socket!")
        
        #Error checking for attachment is done in the Socket class
        self.sockets[socket_index].attach(attachment)

    def detach(self, socket_index: int) -> Optional[game.entity.Item]:
        if socket_index >= len(self.sockets) or socket_index < 0:
            raise game.exceptions.Impossible("That is not a valid spot!")
        
        return self.sockets[socket_index].detach()
    
    


