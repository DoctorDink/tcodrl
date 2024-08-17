from __future__ import annotations

from game.components.base_component import BaseComponent
import game.entity


class Stats(BaseComponent):
    parent: game.entity.Actor

    def __init__(
        self,
        bulk: int = 1,
        shielding: int = 1,
        processing: int = 1,
        coordination: int = 1,
    ):
        self.bulk = bulk
        self.shielding = shielding
        self.processing = processing
        self.coordination = coordination