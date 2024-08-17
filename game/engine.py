from __future__ import annotations

import lzma
import pickle

import tcod

import game.color
import game.entity
import game.exceptions
import game.audio
import game.game_map
import game.input_handlers
import game.message_log
import game.render_functions


class Engine:
    game_map: game.game_map.GameMap
    game_world: game.game_map.GameWorld

    def __init__(self, player: game.entity.Actor):
        self.message_log = game.message_log.MessageLog()
        self.mouse_location = (0, 0)
        self.player = player
        self.audio = game.audio.Audio()
        self.audio.load_sounds()
        self.audio.play_music("data/scratch.wav")

    def review_hostile_enemies(self) -> None:
        for entity in set(self.game_map.actors) - {self.player}:
            if entity.ai.isHostile:
                return True
        return False
                

    def handle_enemy_turns(self) -> None:
        for entity in set(self.game_map.actors) - {self.player}:
            if entity.ai:
                try:
                    entity.ai.perform()
                except game.exceptions.Impossible:
                    pass  # Ignore impossible action exceptions from AI.

    def update_fov(self) -> None:
        """Recompute the visible area based on the players point of view."""
        self.game_map.visible[:] = tcod.map.compute_fov(
            self.game_map.tiles["transparent"],
            (self.player.x, self.player.y),
            radius=8,
        )
        # If a tile is "visible" it should be added to "explored".
        self.game_map.explored |= self.game_map.visible

    def render(self, console: tcod.console.Console) -> None:
        self.game_map.render(console)

        self.message_log.render(console=console, x=21, y=45, width=40, height=5)

        game.render_functions.render_bar(
            console=console,
            current_value=self.player.fighter.hp,
            maximum_value=self.player.fighter.max_hp,
            total_width=20,
            name="Hp:",
            xPos=0,
            yPos=45,
            colorEmpty=game.color.hp_bar_empty,
            colorFull=game.color.hp_bar_filled,
            colorText=game.color.bar_text,
        )

        game.render_functions.render_bar(
            console=console,
            current_value=self.player.stats.current_xp,
            maximum_value=self.player.stats.experience_to_next_level,
            total_width=10,
            name="Xp:",
            xPos=0,
            yPos=46,
            colorEmpty=game.color.xp_bar_empty,
            colorFull=game.color.xp_bar_filled,
            colorText=game.color.bar_text,
        )

        game.render_functions.render_dungeon_level(
            console=console,
            dungeon_level=self.game_world.current_floor,
            location=(0, 47),
        )

        game.render_functions.render_names_at_mouse_location(console=console, x=21, y=44, engine=self)

    def save_as(self, filename: str) -> None:
        """Save this Engine instance as a compressed file."""
        save_data = lzma.compress(pickle.dumps(self))
        with open(filename, "wb") as f:
            f.write(save_data)
