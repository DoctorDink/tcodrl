from __future__ import annotations

from game.components.base_component import BaseComponent
import game.entity


class Stats(BaseComponent):
    parent: game.entity.Actor

    def __init__(
        self,
        bulk: int,
        shielding: int,
        processing: int,
        coordination: int,
    ):
        self.bulk = bulk
        self.shielding = shielding
        self.processing = processing
        self.coordination = coordination
