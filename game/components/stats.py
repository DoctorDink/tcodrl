from __future__ import annotations

import game.components.base_component as base_component
import game.entity

#TODO: Convert stats class to use a map for stats
class Stats(base_component.BaseComponent):
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



