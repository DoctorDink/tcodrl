from __future__ import annotations

import copy

import game.components.base_component as base_component
import game.components.stats as stats
import game.color
import game.entity
import game.input_handlers
import game.render_order
import game.stat_types


class Fighter(base_component.BaseComponent):
    parent: game.entity.Actor

    def __init__(self, base_stats: stats.Stats):
        self.parent = None
        self.base_stats = base_stats
        self.max_hp = self.calculate_max_health()
        self._hp = self.max_hp
        


    @property
    def stats(self) -> stats.Stats:
        stats_after_effects = copy.deepcopy(self.base_stats)

        if not self.parent:
            return stats_after_effects
        
        for stat in self.parent.effect_handler.current_stat_changes:
            if stat == game.stat_types.StatType.BULK:
                stats_after_effects.bulk += self.parent.effect_handler.current_stat_changes[stat]
            if stat == game.stat_types.StatType.COORDINATION:
                stats_after_effects.coordination += self.parent.effect_handler.current_stat_changes[stat]
            if stat == game.stat_types.StatType.SHIELDING:
                stats_after_effects.shielding += self.parent.effect_handler.current_stat_changes[stat]
            if stat == game.stat_types.StatType.PROCESSING:
                stats_after_effects.processing += self.parent.effect_handler.current_stat_changes[stat]

        return stats_after_effects
            

    @property
    def hp(self) -> int:
        return self._hp

    @hp.setter
    def hp(self, value: int) -> None:
        self._hp = max(0, min(value, self.max_hp))
        if self._hp == 0 and self.parent.ai:
            self.die()

    def die(self) -> None:
        if self.engine.player is self.parent:
            death_message = "You died!"
            death_message_color = game.color.player_die
        else:
            death_message = f"{self.parent.name} is dead!"
            death_message_color = game.color.enemy_die

        self.parent.char = "%"
        self.parent.color = (191, 0, 0)
        self.parent.blocks_movement = False
        self.parent.ai = None
        self.parent.name = f"remains of {self.parent.name}"
        self.parent.render_order = game.render_order.RenderOrder.CORPSE

        self.engine.message_log.add_message(death_message, death_message_color)

    def heal(self, amount: int) -> int:
        if self.hp == self.max_hp:
            return 0

        new_hp_value = self.hp + amount

        if new_hp_value > self.max_hp:
            new_hp_value = self.max_hp

        amount_recovered = new_hp_value - self.hp

        self.hp = new_hp_value

        return amount_recovered

    def take_damage(self, amount: int) -> None:
        self.hp -= amount

    def calculate_max_health(self) -> int:
        return 10 + (self.stats.bulk * 2)
    
    def calculate_difficulty_class(self) -> int:
        pass