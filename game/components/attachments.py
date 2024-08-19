from __future__ import annotations

from typing import Optional

import game.components.attachable
import game.attachment_types
import game.entity


class Attachments(game.components.base_component.BaseComponent):
    parent: game.entity.Actor

    def __init__(self, chassis: Optional[game.entity.Item] = None):
        self.chassis_socket = game.components.attachable.Attachable(game.attachment_types.AttachmentType.CHASSIS, chassis)

    def get_sockets(self) -> list[Socket]:
        #DFS
        sockets: list[Socket] = []
        sockets_to_visit = [self.chassis_socket]
        while len(sockets_to_visit) > 0:
            current_socket = sockets_to_visit.pop(0)
            sockets.append(current_socket)
            if current_socket.attachment:
                for child_socket in current_socket.attachment.attachable.sockets.reverse():
                    sockets_to_visit.insert(0, child_socket)

        return sockets

    def attach(self, socket_index: int, attachment: game.entity.Item) -> None:
        sockets = self.get_sockets()
        sockets[socket_index].attach(attachment)


